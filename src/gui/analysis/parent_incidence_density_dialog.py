# -*- coding: utf-8 -*-
"""
/***************************************************************************

                                 GeoPublicHealth
                                 A QGIS plugin

                              -------------------
        begin                : 2014-08-20
        copyright            : (C) 2014 by Etienne Trimaille
                              (C) 2020-2025 by GeoPublicHealth Team
        email                : info@geopublichealth.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

# Standard Library Imports
import traceback
import tempfile
import os
from typing import Dict, List, Optional, Union, Any

# Third-Party Imports
import numpy as np

from geopublichealth.src.core.optional_deps import (
    MATPLOTLIB_AVAILABLE,
    Figure,
    FigureCanvas,
)

# PyQt Imports
from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QTableWidgetItem,
    QApplication,
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
    QCheckBox,
)
from qgis.PyQt.QtCore import QSize, QVariant, Qt, pyqtSignal, QSettings
from qgis.PyQt.QtGui import QColor

# QGIS Core Imports
from qgis.core import (
    QgsApplication,
    QgsTask,
    QgsMessageLog,
    Qgis,
    QgsField,
    QgsFields,
    QgsFeature,
    QgsFeatureRequest,
    QgsVectorLayer,
    QgsProject,
    QgsGeometry,
    QgsWkbTypes,
    QgsMapLayerProxyModel,
    QgsProcessingUtils,
    QgsFieldConstraints,
    QgsVectorFileWriter,
    QgsSpatialIndex,
    QgsUnitTypes,
    QgsGraduatedSymbolRenderer,
    QgsSymbol,
    QgsGradientColorRamp,
    QgsCoordinateTransformContext,
    QgsFieldProxyModel,
    QgsVectorDataProvider,
    QgsRendererRange,
    QgsClassificationRange,
)

# QGIS GUI Imports
from qgis.gui import (
    QgsFieldComboBox,
    QgsMapLayerComboBox,
    QgsColorButton,
    QgsCollapsibleGroupBox,
)
from qgis.utils import iface

# Plugin-Specific Imports
from geopublichealth.src.core.graph_toolbar import CustomNavigationToolbar
from geopublichealth.src.core.tools import display_message_bar, tr
from geopublichealth.src.core.exceptions import (
    GeoPublicHealthException,
    NoLayerProvidedException,
    DifferentCrsException,
    FieldExistingException,
    FieldException,
    NotANumberException,
)
from geopublichealth.src.core.stats import Stats


# --------------------------------------------------------------------------
# Background Task Class
# --------------------------------------------------------------------------
class IncidenceDensityTask(QgsTask):
    """Background task for calculating incidence or density rates."""

    taskCompleted = pyqtSignal(bool, object, str)  # success, results, message
    progressChanged = pyqtSignal(float)  # Current progress (0-100)

    # Result data keys
    RESULT_DATA = "data"
    RESULT_TOTAL_CASES = "total_cases"
    RESULT_WARNINGS = "warnings"
    RESULT_DRIVER = "driver_name"

    def __init__(
        self,
        description: str,
        admin_layer_uri: str,
        point_layer_uri: Optional[str],
        case_field_name: Optional[str],
        population_field_name: Optional[str],
        output_field_name: str,
        add_intersections_flag: bool,
        ratio_value: float,
        output_file_path: str,
        use_area_flag: bool,
        use_point_layer_flag: bool,
        transform_context: QgsCoordinateTransformContext,
        project_crs: Any,
        driver_name: str,
    ):
        """Initialize the task with necessary parameters."""
        super().__init__(description, QgsTask.CanCancel)

        # Input parameters
        self.admin_layer_uri = admin_layer_uri
        self.point_layer_uri = point_layer_uri
        self.case_field_name = case_field_name
        self.population_field_name = population_field_name
        self.output_field_name = output_field_name
        self.add_intersections_flag = add_intersections_flag
        self.ratio = ratio_value
        self.output_path = output_file_path  # Base path without suffix
        self.use_area_flag = use_area_flag
        self.use_point_layer_flag = use_point_layer_flag
        self.transform_context = transform_context
        self.project_crs = project_crs
        self.driver_name = driver_name

        # Output/state variables
        self.exception = None
        self.calculated_data = []
        self.total_case_count = 0
        self.task_warnings = []

    def run(self) -> bool:
        """Main processing logic executed in the background thread."""
        QgsMessageLog.logMessage(
            f"Task '{self.description()}' started for {self.output_path}",
            "GeoPublicHealth",
            Qgis.Info,
        )

        file_writer = None
        output_target_path = self.output_path + (
            ".gpkg" if self.driver_name == "GPKG" else ".shp"
        )

        try:
            # --- Load Layers ---
            admin_layer = QgsVectorLayer(
                self.admin_layer_uri, "admin_layer_task", "ogr"
            )
            if not admin_layer or not admin_layer.isValid():
                raise GeoPublicHealthException(tr("Admin layer invalid in task."))

            point_layer = None
            if self.use_point_layer_flag and self.point_layer_uri:
                point_layer = QgsVectorLayer(
                    self.point_layer_uri, "point_layer_task", "ogr"
                )
                if not point_layer or not point_layer.isValid():
                    raise NoLayerProvidedException(tr("Point layer invalid in task."))

                if admin_layer.crs() != point_layer.crs():
                    raise DifferentCrsException(
                        epsg1=admin_layer.crs().authid(),
                        epsg2=point_layer.crs().authid(),
                    )

            # --- Prepare Output Fields ---
            admin_fields = admin_layer.fields()
            output_fields = QgsFields()
            output_fields.extend(admin_fields)

            # Create rate field
            rate_field = QgsField(
                name=self.output_field_name,
                type=6,  # 6 is equivalent to QVariant.Double
                typeName="Real",
                len=20,
                prec=10,
            )

            # Handle intersection field if needed
            intersection_field = None
            intersection_field_name = "intersect_ct"
            if self.add_intersections_flag:
                if admin_fields.indexOf(intersection_field_name) == -1:
                    intersection_field = QgsField(intersection_field_name, QVariant.Int)
                else:
                    QgsMessageLog.logMessage(
                        tr(f"Field '{intersection_field_name}' exists, skipping."),
                        "GeoPublicHealth",
                        Qgis.Warning,
                    )
                    self.add_intersections_flag = False

            # Check if output field already exists
            if output_fields.indexOf(self.output_field_name) != -1:
                raise FieldExistingException(field=self.output_field_name)

            # Add fields to output
            output_fields.append(rate_field)
            if intersection_field:
                output_fields.append(intersection_field)

            # --- Setup Vector File Writer ---
            gpkg_layer_name = (
                self.output_field_name.replace(" ", "_")
                if self.driver_name == "GPKG"
                else None
            )

            save_options = QgsVectorFileWriter.SaveVectorOptions()
            save_options.driverName = self.driver_name
            save_options.encoding = "UTF-8"
            if gpkg_layer_name:
                save_options.layerName = gpkg_layer_name

            # Create the output file
            file_writer = QgsVectorFileWriter.create(
                output_target_path,
                output_fields,
                QgsWkbTypes.Polygon,
                admin_layer.crs(),
                self.transform_context,
                save_options,
            )

            if file_writer is None or file_writer.hasError():
                error_msg = (
                    file_writer.errorMessage() if file_writer else "Unknown error"
                )
                raise CreatingShapeFileException(
                    tr("Failed to create output file writer: ") + error_msg
                )

            # --- Prepare indices ---
            point_layer_index = None
            index_case = -1
            index_population = -1
            self.total_case_count = 0

            # Set up spatial index for point layer if needed
            if self.use_point_layer_flag and point_layer:
                self.total_case_count = point_layer.featureCount()
                if self.total_case_count > 0:
                    point_layer_index = QgsSpatialIndex(point_layer.getFeatures())
            else:
                # Get case field index
                index_case = admin_fields.lookupField(self.case_field_name)
                if index_case == -1:
                    raise FieldException(
                        tr("Case field '{}' not found.").format(self.case_field_name)
                    )

            # Get population field index if needed
            if not self.use_area_flag:
                index_population = admin_fields.lookupField(self.population_field_name)
                if index_population == -1:
                    raise FieldException(
                        tr("Population field '{}' not found.").format(
                            self.population_field_name
                        )
                    )

                # Check that case and population fields are different
                if not self.use_point_layer_flag and index_population == index_case:
                    raise FieldException(field_1="Population", field_2="Case")

            # --- Process Features ---
            self.calculated_data = []
            admin_features_iterator = admin_layer.getFeatures()
            num_admin_features = admin_layer.featureCount()

            if num_admin_features == 0:
                del file_writer
                return True

            # Setup progress tracking
            progress_step = 100.0 / num_admin_features

            # Get output field indices
            output_field_idx = output_fields.lookupField(self.output_field_name)
            intersection_field_idx = (
                output_fields.lookupField(intersection_field_name)
                if self.add_intersections_flag
                else -1
            )

            # Process each admin feature
            for i, admin_feature in enumerate(admin_features_iterator):
                if self.isCanceled():
                    del file_writer
                    return False

                attributes = admin_feature.attributes()
                admin_geom = admin_feature.geometry()
                feature_id_str = f"ID {admin_feature.id()}"
                count = 0
                value = None  # Default to None

                # Get Case Count based on method
                if self.use_point_layer_flag and point_layer_index and point_layer:
                    # Count points that intersect with the admin polygon
                    candidate_fids = point_layer_index.intersects(
                        admin_geom.boundingBox()
                    )
                    if candidate_fids:
                        request = QgsFeatureRequest().setFilterFids(candidate_fids)
                        prepared_admin_geom = QgsGeometry(admin_geom)

                        for point_feat in point_layer.getFeatures(request):
                            point_geom = point_feat.geometry()
                            if (
                                point_geom
                                and not point_geom.isEmpty()
                                and point_geom.intersects(prepared_admin_geom)
                            ):
                                count += 1

                elif not self.use_point_layer_flag:
                    # Get case count from attribute field
                    case_val = attributes[index_case]
                    count = 0

                    if not (
                        case_val is None
                        or (isinstance(case_val, QVariant) and case_val.isNull())
                    ):
                        try:
                            f_count = float(str(case_val).replace(",", ""))
                            count = int(f_count) if f_count >= 0 else 0
                        except (ValueError, TypeError):
                            QgsMessageLog.logMessage(
                                f"{tr('Warning:')} {feature_id_str} {tr('has invalid case value')} "
                                f"('{case_val}'), {tr('treating as 0.')}",
                                "GeoPublicHealth",
                                Qgis.Warning,
                            )

                    if i == 0:
                        self.total_case_count = 0
                    self.total_case_count += count

                # Calculate Value based on method
                try:
                    if self.use_area_flag:
                        # Density calculation (count / area)
                        denominator = admin_geom.area()

                        if denominator > 1e-9:
                            value = float(count) / denominator * self.ratio
                        elif count != 0:
                            QgsMessageLog.logMessage(
                                f"{tr('Warning:')} {feature_id_str} {tr('has zero/negligible area.')}",
                                "GeoPublicHealth",
                                Qgis.Warning,
                            )
                    else:
                        # Incidence calculation (count / population)
                        pop_val = attributes[index_population]
                        denominator = 0.0

                        if not (
                            pop_val is None
                            or (isinstance(pop_val, QVariant) and pop_val.isNull())
                        ):
                            try:
                                denominator = float(str(pop_val).replace(",", ""))
                            except (ValueError, TypeError):
                                QgsMessageLog.logMessage(
                                    f"{tr('Warning:')} {feature_id_str} {tr('has invalid population value')} "
                                    f"('{pop_val}').",
                                    "GeoPublicHealth",
                                    Qgis.Warning,
                                )

                        if denominator > 1e-9:
                            value = float(count) / denominator * self.ratio
                        elif count != 0:
                            QgsMessageLog.logMessage(
                                f"{tr('Warning:')} {feature_id_str} {tr('has zero/negligible population.')}",
                                "GeoPublicHealth",
                                Qgis.Warning,
                            )
                except Exception as e:
                    QgsMessageLog.logMessage(
                        f"{tr('Warning: Calculation error for')} {feature_id_str}: {str(e)}",
                        "GeoPublicHealth",
                        Qgis.Warning,
                    )
                    value = None

                # Store the calculated value
                self.calculated_data.append(value)

                # Prepare and Write Feature
                new_feature = QgsFeature(output_fields)
                new_feature.setGeometry(QgsGeometry(admin_geom))

                # Copy original attributes
                for fld_idx, src_fld in enumerate(admin_fields):
                    new_feature[src_fld.name()] = attributes[fld_idx]

                # Set calculated value
                new_feature[output_field_idx] = value  # None handled as NULL

                # Set intersection count if requested
                if self.add_intersections_flag and intersection_field_idx != -1:
                    new_feature[intersection_field_idx] = count

                # Add feature to output file
                if not file_writer.addFeature(new_feature):
                    QgsMessageLog.logMessage(
                        f"{tr('Error writing feature')} {feature_id_str}: {file_writer.errorMessage()}",
                        "GeoPublicHealth",
                        Qgis.Warning,
                    )

                # Update progress
                self.progressChanged.emit((i + 1) * progress_step)

            # --- Finalize ---
            del file_writer
            file_writer = None

            if self.isCanceled():
                QgsProcessingUtils.deleteFile(output_target_path)
                return False

            return True

        # --- Error Handling ---
        except Exception as e:
            self.exception = e
            QgsMessageLog.logMessage(
                f"Task '{self.description()}' failed: {str(e)}\n{traceback.format_exc()}",
                "GeoPublicHealth",
                Qgis.Critical,
            )

            if file_writer is not None:
                del file_writer

            # Try to clean up output file on error
            if hasattr(self, "output_path") and self.output_path:
                try:
                    output_target_path_on_error = self.output_path + (
                        ".gpkg" if self.driver_name == "GPKG" else ".shp"
                    )
                    os.remove(output_target_path_on_error)
                except OSError:
                    pass

            return False

    def finished(self, result: bool):
        """Called when the task's run() method finishes."""
        if result:
            results_dict = {
                self.RESULT_DATA: self.calculated_data,
                self.RESULT_TOTAL_CASES: self.total_case_count,
                self.RESULT_WARNINGS: self.task_warnings,
                self.RESULT_DRIVER: self.driver_name,
            }
            self.taskCompleted.emit(True, results_dict, self.output_path)
            QgsMessageLog.logMessage(
                f"Task '{self.description()}' finished successfully.",
                "GeoPublicHealth",
                Qgis.Info,
            )
        else:
            error_msg = (
                f"{tr('Task failed:')} {str(self.exception)}"
                if self.exception
                else tr("Task cancelled or failed.")
            )
            self.taskCompleted.emit(False, None, error_msg)
            QgsMessageLog.logMessage(
                f"Task '{self.description()}' finished with error or cancellation.",
                "GeoPublicHealth",
                Qgis.Warning,
            )


# --------------------------------------------------------------------------
# Main Dialog Class
# --------------------------------------------------------------------------
class IncidenceDensityDialog(QDialog):
    """Base Dialog class for Incidence and Density calculations. Uses QgsTask."""

    signalAskCloseWindow = pyqtSignal(int, name="signalAskCloseWindow")
    signalStatus = pyqtSignal(int, str, name="signalStatus")

    def __init__(self, parent=None):
        """Constructor for the base dialog.

        Args:
            parent: Parent widget

        Notes:
            Subclasses must set:
            - use_area: If True, uses area for density calculation, otherwise uses population
            - use_point_layer: If True, uses points for case count, otherwise uses a field
        """
        super().__init__(parent)
        self.parent = parent

        # State variables
        self.name_field = None
        self.admin_layer = None
        self.figure = None
        self.canvas = None
        self.toolbar = None
        self.output_file_path = None
        self.output_layer = None
        self.current_task = None

        # Settings - these must be set by subclasses
        self.use_area = None
        self.use_point_layer = None

    def setup_ui(self):
        """Sets up common UI elements and connections.

        Call AFTER subclass FORM_CLASS.setupUi.
        """
        # --- Assign widget references ---
        self._get_ui_elements()

        # --- Connections ---
        self._setup_ui_connections()

        # --- Symbology Mode Setup ---
        self._setup_classification_modes()

        # --- Matplotlib Setup ---
        self._setup_plot_area()

        # --- Layer ComboBox Setup ---
        if hasattr(self, "cbx_aggregation_layer") and self.cbx_aggregation_layer:
            self.cbx_aggregation_layer.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        else:
            # Log warning but don't block - some dialog variants may not have this element
            QgsMessageLog.logMessage(
                tr(
                    "Aggregation layer combobox ('cbx_aggregation_layer') not found in UI. This is expected for some dialog variants."
                ),
                "GeoPublicHealth",
                Qgis.Warning,
            )
            # Don't return - continue with initialization

        # --- Conditional UI Setup ---
        self._setup_conditional_ui()

    def _get_ui_elements(self):
        """Get references to UI elements safely."""
        # Main controls
        self.button_browse = getattr(self, "button_browse", None)
        self.button_box_ok = getattr(self, "button_box_ok", None)
        self.plot_layout = getattr(self, "layout_plot", None)

        # Layer and field selectors
        self.cbx_aggregation_layer = getattr(self, "cbx_aggregation_layer", None)
        self.le_output_filepath = getattr(self, "le_output_filepath", None)
        self.le_new_column = getattr(self, "le_new_column", None)
        self.checkBox_addNbIntersections = getattr(
            self, "checkBox_addNbIntersections", None
        )
        self.cbx_ratio = getattr(self, "cbx_ratio", None)

        # Symbology widgets
        self.symbology = getattr(self, "symbology", None)
        self.color_low_value = getattr(self, "color_low_value", None)
        self.color_high_value = getattr(self, "color_high_value", None)
        self.spinBox_classes = getattr(self, "spinBox_classes", None)
        self.cbx_mode = getattr(self, "cbx_mode", None)

        # Statistics widgets
        self.checkBox_incidence_runStats = getattr(
            self, "checkBox_incidence_runStats", None
        )
        self.tableWidget = getattr(self, "tableWidget", None)

        # Progress widgets
        self.progressBar = getattr(self, "progressBar", None)
        self.label_progress = getattr(self, "label_progress", None)

        # Point and case field widgets
        self.cbx_case_layer = getattr(self, "cbx_case_layer", None)
        self.cbx_case_field = getattr(self, "cbx_case_field", None)
        self.cbx_population_field = getattr(self, "cbx_population_field", None)

    def _setup_ui_connections(self):
        """Set up signal-slot connections."""
        if self.button_browse:
            self.button_browse.clicked.connect(self.open_file_browser)

        if self.button_box_ok:
            ok_button = self.button_box_ok.button(QDialogButtonBox.Ok)
            cancel_button = self.button_box_ok.button(QDialogButtonBox.Cancel)

            if ok_button:
                ok_button.clicked.connect(self.start_stats_task)
            if cancel_button:
                cancel_button.clicked.connect(self.cancel_task_and_close)

    def _setup_classification_modes(self):
        """Set up classification modes for symbology."""
        # Add classification modes
        modes = {
            tr("Quantile"): QgsGraduatedSymbolRenderer.Quantile,
            tr("Equal Interval"): QgsGraduatedSymbolRenderer.EqualInterval,
            tr("Natural Breaks (Jenks)"): QgsGraduatedSymbolRenderer.Jenks,
            tr("Standard Deviation"): QgsGraduatedSymbolRenderer.StdDev,
            tr("Pretty Breaks"): QgsGraduatedSymbolRenderer.Pretty,
        }

        for text, mode_enum in modes.items():
            self.cbx_mode.addItem(text, mode_enum)

        if self.cbx_mode.count() > 0:
            self.cbx_mode.setCurrentIndex(0)  # Set default

    def _setup_plot_area(self):
        """Set up the matplotlib plot area."""
        if not MATPLOTLIB_AVAILABLE:
            self.figure, self.canvas, self.toolbar = None, None, None
            return

        if self.plot_layout and isinstance(self.plot_layout, QVBoxLayout):
            try:
                # Create figure and canvas
                self.figure = Figure(figsize=(5, 3), dpi=100)
                self.canvas = FigureCanvas(self.figure)
                self.toolbar = CustomNavigationToolbar(self.canvas, self)

                # Clear any existing widgets
                while self.plot_layout.count():
                    item = self.plot_layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()

                # Add the new widgets
                self.plot_layout.addWidget(self.toolbar)
                self.plot_layout.addWidget(self.canvas)

            except Exception as e:
                QMessageBox.warning(
                    self,
                    tr("Plot Setup Warning"),
                    tr("Could not initialize plot area:") + f"\n{str(e)}",
                )
        else:
            self.figure, self.canvas, self.toolbar = None, None, None

    def _setup_conditional_ui(self):
        """Configure UI elements based on processing method."""
        if self.use_point_layer is None or self.use_area is None:
            QMessageBox.critical(
                self,
                tr("Setup Error"),
                tr("Plugin internal error: flags not set by subclass."),
            )
            return

        # Configure case layer UI elements
        self._configure_conditional_widgets(
            "cbx_case_layer", QgsMapLayerProxyModel.PointLayer, self.use_point_layer
        )
        self._configure_conditional_widgets(
            "label_case_layer", None, self.use_point_layer
        )

        # Configure case field UI elements
        self._configure_conditional_widgets(
            "cbx_case_field",
            QgsFieldProxyModel.Numeric | QgsFieldProxyModel.String,
            not self.use_point_layer,
            self.reset_field_case,
        )
        self._configure_conditional_widgets(
            "label_case_field", None, not self.use_point_layer
        )

        # Configure population field UI elements
        self._configure_conditional_widgets(
            "cbx_population_field",
            QgsFieldProxyModel.Numeric | QgsFieldProxyModel.String,
            not self.use_area,
            self.reset_field_population,
        )
        self._configure_conditional_widgets(
            "label_population_field", None, not self.use_area
        )

        # Hide progress indicators initially
        if self.progressBar:
            self.progressBar.setVisible(False)
        if self.label_progress:
            self.label_progress.setVisible(False)

    def _configure_conditional_widgets(
        self, widget_attr_name, filter_or_type, condition_to_enable, reset_func=None
    ):
        """Helper to configure widgets based on conditions.

        Args:
            widget_attr_name: Name of the widget attribute
            filter_or_type: Filter for field or layer combo boxes
            condition_to_enable: Whether to enable the widget
            reset_func: Function to call when resetting the widget
        """
        widget = getattr(self, widget_attr_name, None)
        label_widget = getattr(
            self, f"label_{widget_attr_name.replace('cbx_', '')}", None
        )

        if widget:
            is_field_combo = isinstance(widget, QgsFieldComboBox)
            widget.setEnabled(condition_to_enable)
            widget.setVisible(condition_to_enable)

            if label_widget:
                label_widget.setVisible(condition_to_enable)

            if condition_to_enable and self.cbx_aggregation_layer:
                if isinstance(widget, QgsMapLayerComboBox) and filter_or_type:
                    widget.setFilters(filter_or_type)
                elif is_field_combo and filter_or_type:
                    widget.setFilters(filter_or_type)
                    current_admin_layer = self.cbx_aggregation_layer.currentLayer()
                    widget.setLayer(current_admin_layer)

                    # Connect signals robustly
                    try:
                        self.cbx_aggregation_layer.layerChanged.disconnect(
                            widget.setLayer
                        )
                    except TypeError:
                        pass

                    try:
                        if reset_func:
                            self.cbx_aggregation_layer.layerChanged.disconnect(
                                reset_func
                            )
                    except TypeError:
                        pass

                    self.cbx_aggregation_layer.layerChanged.connect(widget.setLayer)

                    if reset_func:
                        self.cbx_aggregation_layer.layerChanged.connect(reset_func)
                        reset_func()

    def reset_field_population(self):
        """Reset population field selection."""
        widget = getattr(self, "cbx_population_field", None)
        if widget:
            widget.setField("")

    def reset_field_case(self):
        """Reset case field selection."""
        widget = getattr(self, "cbx_case_field", None)
        if widget:
            widget.setField("")

    def open_file_browser(self):
        """Opens file dialog to select output file path."""
        if not self.le_output_filepath:
            return

        last_dir = QSettings().value("GeoPublicHealth/lastDir", os.path.expanduser("~"))

        output_file, selected_filter = QFileDialog.getSaveFileName(
            self,
            tr("Save Output Layer"),
            last_dir,
            tr("GeoPackage (*.gpkg);;ESRI Shapefiles (*.shp)"),
        )

        if output_file:
            is_shp = "(*.shp)" in selected_filter
            is_gpkg = "(*.gpkg)" in selected_filter
            base, ext = os.path.splitext(output_file)

            # Apply correct extension based on filter
            if is_shp and not ext.lower() == ".shp":
                output_file = base + ".shp"
            elif is_gpkg and not ext.lower() == ".gpkg":
                output_file = base + ".gpkg"
            elif not ext:  # Default to GeoPackage if no extension
                output_file += ".gpkg"

            self.le_output_filepath.setText(output_file)
            QSettings().setValue(
                "GeoPublicHealth/lastDir", os.path.dirname(output_file)
            )

    def start_stats_task(self):
        """Validates inputs and starts the background task."""
        if self.current_task:
            display_message_bar(tr("A task is already running."), level=Qgis.Warning)
            return

        # --- Get input values ---
        admin_layer = (
            self.cbx_aggregation_layer.currentLayer()
            if self.cbx_aggregation_layer
            else None
        )
        if not admin_layer:
            display_message_bar(
                tr("Please select an aggregation layer."), level=Qgis.Warning
            )
            return

        self.admin_layer = admin_layer
        admin_layer_uri = admin_layer.source()

        point_layer = None
        point_layer_uri = None
        case_column_name = None
        population_column_name = None

        # Get case source (point layer or field)
        if self.use_point_layer:
            point_layer = (
                self.cbx_case_layer.currentLayer() if self.cbx_case_layer else None
            )
            if not point_layer:
                display_message_bar(
                    tr("Please select a point case layer."), level=Qgis.Warning
                )
                return

            point_layer_uri = point_layer.source()

            if admin_layer.crs() != point_layer.crs():
                display_message_bar(
                    tr("Admin and Point layers must have the same CRS."),
                    level=Qgis.Critical,
                )
                return
        else:
            case_column_name = (
                self.cbx_case_field.currentField() if self.cbx_case_field else None
            )
            if not case_column_name:
                display_message_bar(
                    tr("Please select a case field."), level=Qgis.Warning
                )
                return

        # Get population source (field or area)
        if not self.use_area:
            population_column_name = (
                self.cbx_population_field.currentField()
                if self.cbx_population_field
                else None
            )
            if not population_column_name:
                display_message_bar(
                    tr("Please select a population field."), level=Qgis.Warning
                )
                return

            if not self.use_point_layer and case_column_name == population_column_name:
                display_message_bar(
                    tr("Case field and Population field cannot be the same."),
                    level=Qgis.Warning,
                )
                return

        # Get output field name
        self.name_field = self.le_new_column.text() if self.le_new_column else ""
        if not self.name_field and self.le_new_column:
            self.name_field = self.le_new_column.placeholderText()

        if not self.name_field:
            display_message_bar(
                tr("Output field name cannot be empty."), level=Qgis.Warning
            )
            return

        # Get other parameters
        add_nb_intersections = (
            self.checkBox_addNbIntersections.isChecked()
            if self.checkBox_addNbIntersections
            else False
        )

        # Get ratio value
        try:
            ratio_text = self.cbx_ratio.currentText() if self.cbx_ratio else "1"
            ratio = float(ratio_text.replace(" ", ""))
            assert ratio > 0
        except (ValueError, AssertionError):
            display_message_bar(
                tr("Invalid ratio value entered (must be > 0)."), level=Qgis.Critical
            )
            return

        # --- Handle output path ---
        output_file_path_ui = (
            self.le_output_filepath.text() if self.le_output_filepath else ""
        )
        driver_name = "GPKG"

        if output_file_path_ui:
            if output_file_path_ui.lower().endswith(".shp"):
                driver_name = "ESRI Shapefile"
            elif not output_file_path_ui.lower().endswith(".gpkg"):
                output_file_path_ui += ".gpkg"

            if self.le_output_filepath:
                self.le_output_filepath.setText(output_file_path_ui)

            output_file_path = os.path.splitext(output_file_path_ui)[0]  # Base path
        else:
            # Create temporary file if no output path specified
            try:
                fd, temp_path = tempfile.mkstemp(suffix="_incid_dens")
                os.close(fd)
                os.remove(temp_path)
                output_file_path = temp_path
            except Exception as e:
                display_message_bar(
                    f"{tr('Could not create temporary file:')} {str(e)}",
                    level=Qgis.Critical,
                )
                return

            driver_name = "GPKG"

            if self.le_output_filepath:
                self.le_output_filepath.setText(output_file_path + ".gpkg")

        self.output_file_path = output_file_path  # Store base path

        # Check field name length for shapefiles
        if driver_name == "ESRI Shapefile" and len(self.name_field) > 10:
            display_message_bar(
                tr("Output field name must be 10 characters or less for Shapefiles."),
                level=Qgis.Warning,
            )
            return

        # --- Start the task ---
        self._set_ui_running_state(True)
        QApplication.setOverrideCursor(Qt.WaitCursor)

        task_title = tr("Calculating Incidence/Density for ") + admin_layer.name()

        self.current_task = IncidenceDensityTask(
            task_title,
            admin_layer_uri,
            point_layer_uri,
            case_column_name,
            population_column_name,
            self.name_field,
            add_nb_intersections,
            ratio,
            output_file_path,
            self.use_area,
            self.use_point_layer,
            QgsProject.instance().transformContext(),
            admin_layer.crs(),
            driver_name,
        )

        # Connect signals
        self.current_task.progressChanged.connect(self.update_progress)
        self.current_task.taskCompleted.connect(self.task_finished)

        # Add to task manager
        QgsApplication.taskManager().addTask(self.current_task)

    def update_progress(self, value: float):
        """Slot to update progress UI elements.

        Args:
            value: Progress value (0-100)
        """
        if self.progressBar:
            self.progressBar.setValue(int(value))
        if self.label_progress:
            self.label_progress.setText(f"{tr('Processing...')} {int(value)}%")

    def task_finished(
        self, success: bool, result_data: Optional[Dict[str, Any]], message: str
    ):
        """Slot executed when the background task completes.

        Args:
            success: Whether the task completed successfully
            result_data: Result data dictionary or None on failure
            message: Status message or error message
        """
        self._set_ui_running_state(False)
        QApplication.restoreOverrideCursor()
        self.current_task = None

        if success:
            self.output_file_path = message  # Base path returned
            driver_name = result_data.get(IncidenceDensityTask.RESULT_DRIVER, "GPKG")
            output_suffix = ".gpkg" if driver_name == "GPKG" else ".shp"
            output_full_path = self.output_file_path + output_suffix
            gpkg_layer_name = (
                self.name_field.replace(" ", "_") if driver_name == "GPKG" else None
            )

            # Display any warnings
            layer_warnings = result_data.get(IncidenceDensityTask.RESULT_WARNINGS, [])
            if layer_warnings:
                display_message_bar(
                    tr("Processing completed with warnings:")
                    + "\n - "
                    + "\n - ".join(layer_warnings),
                    level=Qgis.Warning,
                    duration=10,
                )
            else:
                display_message_bar(
                    tr("Processing finished successfully."), level=Qgis.Success
                )

            # Get result data
            data = result_data.get(IncidenceDensityTask.RESULT_DATA, [])
            total_cases = result_data.get(IncidenceDensityTask.RESULT_TOTAL_CASES, 0)

            # Load the output layer
            layer_uri = (
                f"{output_full_path}|layername={gpkg_layer_name}"
                if driver_name == "GPKG"
                else output_full_path
            )
            self.output_layer = QgsVectorLayer(layer_uri, self.name_field, "ogr")

            if self.output_layer and self.output_layer.isValid():
                # Add to map
                QgsProject.instance().addMapLayer(self.output_layer)
                display_message_bar(
                    tr("Output layer loaded: ") + self.output_layer.name(),
                    level=Qgis.Info,
                )

                # Display stats if requested
                if (
                    self.checkBox_incidence_runStats
                    and self.checkBox_incidence_runStats.isChecked()
                ):
                    self.display_stats_and_plot(data, total_cases)

                # Apply symbology if requested
                if self.symbology and self.symbology.isChecked():
                    self.add_symbology()

                self.signalStatus.emit(3, tr("Successful process"))
            else:
                display_message_bar(
                    tr(
                        "Output file may have been created, but failed to load as a layer:"
                    )
                    + f"\n{layer_uri}",
                    level=Qgis.Critical,
                )

                # Debug output
                debug_path_to_check = output_full_path
                if not os.path.exists(debug_path_to_check):
                    QgsMessageLog.logMessage(
                        f"Output file does not exist: {debug_path_to_check}",
                        "GeoPublicHealth",
                        Qgis.Critical,
                    )
                else:
                    QgsMessageLog.logMessage(
                        f"Output file exists, but layer failed to load: {layer_uri}",
                        "GeoPublicHealth",
                        Qgis.Critical,
                    )
        else:
            display_message_bar(
                f"{tr('Processing failed or cancelled:')}\n{message}",
                level=Qgis.Critical,
            )

            # Debug output
            output_base_path_on_fail = (
                self.output_file_path if self.output_file_path else "Unknown"
            )
            QgsMessageLog.logMessage(
                f"Task failed. Output base path was intended to be: {output_base_path_on_fail}",
                "GeoPublicHealth",
                Qgis.Critical,
            )

    def _set_ui_running_state(self, running: bool):
        """Helper to enable/disable UI elements during task execution.

        Args:
            running: Whether a task is running
        """
        # Update buttons
        ok_button = (
            self.button_box_ok.button(QDialogButtonBox.Ok)
            if self.button_box_ok
            else None
        )
        cancel_button = (
            self.button_box_ok.button(QDialogButtonBox.Cancel)
            if self.button_box_ok
            else None
        )

        if ok_button:
            ok_button.setEnabled(not running)

        if cancel_button:
            cancel_button.setText(tr("Cancel Task") if running else tr("Cancel"))

        # Update progress indicators
        if self.progressBar:
            self.progressBar.setVisible(running)
            self.progressBar.setValue(0)

        if self.label_progress:
            self.label_progress.setVisible(running)
            self.label_progress.setText(tr("Task starting...") if running else "")

        QApplication.processEvents()

    def display_stats_and_plot(self, data: List[float], total_case: int):
        """Calculates stats, updates table widget, and draws plot.

        Args:
            data: List of calculated values
            total_case: Total number of cases
        """
        if not self.tableWidget:
            return

        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)

        if not isinstance(data, list):
            display_message_bar(tr("Invalid data for statistics."), level=Qgis.Warning)
            return

        try:
            # Filter out null and invalid values
            valid_data = [val for val in data if val is not None and np.isfinite(val)]
            null_count = len(data) - len(valid_data)
            stats = None

            if valid_data:
                stats = Stats(valid_data)

            # Prepare stats items
            items_stats = [
                (tr("Calculated Nulls/Infs"), null_count),
                (tr("Case Count"), total_case),
            ]

            # Add admin layer count
            admin_layer_count = (
                self.admin_layer.featureCount()
                if self.admin_layer and self.admin_layer.isValid()
                else "N/A"
            )
            items_stats.append((tr("Polygon Count"), admin_layer_count))

            # Add statistical measures
            if stats:
                stat_funcs = {
                    "Min": stats.min,
                    "Average": stats.average,
                    "Max": stats.max,
                    "Median": stats.median,
                    "Range": stats.range,
                    "Variance": stats.variance,
                    "Std Deviation": stats.standard_deviation,
                }

                for name, func in stat_funcs.items():
                    try:
                        items_stats.append((tr(name), func()))
                    except Exception:
                        items_stats.append((tr(name), "Error"))
            else:
                # No valid data for stats
                for name in [
                    "Min",
                    "Average",
                    "Max",
                    "Median",
                    "Range",
                    "Variance",
                    "Std Deviation",
                ]:
                    items_stats.append((tr(name), "N/A"))

            # Populate table
            self.tableWidget.setRowCount(len(items_stats))
            self.tableWidget.setColumnCount(2)
            self.tableWidget.setHorizontalHeaderLabels([tr("Parameter"), tr("Value")])

            for i, (label, value) in enumerate(items_stats):
                self.tableWidget.setItem(i, 0, QTableWidgetItem(label))

                # Format value
                if isinstance(value, float) and np.isfinite(value):
                    val_str = "{:,.4f}".format(value)
                else:
                    val_str = str(value)

                self.tableWidget.setItem(i, 1, QTableWidgetItem(val_str))

            # Resize columns and rows
            self.tableWidget.resizeColumnsToContents()
            self.tableWidget.resizeRowsToContents()

            # Draw plot
            self.draw_plot(data)

        except Exception as e:
            display_message_bar(
                f"{tr('Error displaying statistics or plot:')} {str(e)}",
                level=Qgis.Critical,
            )
            traceback.print_exc()

    def draw_plot(self, data: List[float]):
        """Function to draw the plot and display it in the canvas.

        Args:
            data: List of calculated values
        """
        if not (self.figure and self.canvas):
            return

        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            # Validate data
            if not isinstance(data, list) or not data:
                ax.text(0.5, 0.5, tr("No data to plot"), ha="center", va="center")
            else:
                # Extract valid values and their indices
                valid_indices = [
                    i
                    for i, val in enumerate(data)
                    if val is not None and np.isfinite(val)
                ]
                valid_values = [data[i] for i in valid_indices]

                if valid_values:
                    ax.plot(valid_indices, valid_values, "b.-", markersize=4)
                else:
                    ax.text(
                        0.5,
                        0.5,
                        tr("No valid data points to plot"),
                        ha="center",
                        va="center",
                    )

            # Set labels and title
            ax.set_xlabel(tr("Polygon Feature Index (Original Order)"))
            ax.set_ylabel(
                self.name_field if self.name_field else tr("Calculated Value")
            )
            ax.set_title(tr("Calculated Values per Polygon"))

            # Add grid and draw
            ax.grid(True)
            self.figure.tight_layout()
            self.canvas.draw()

        except Exception as e:
            display_message_bar(
                f"{tr('Error drawing plot:')} {str(e)}", level=Qgis.Critical
            )
            traceback.print_exc()

    def add_symbology(self):
        """Adds graduated symbology to the output layer."""
        if not self.output_layer or not self.output_layer.isValid():
            display_message_bar(
                tr("Cannot apply symbology, output layer is invalid."),
                level=Qgis.Warning,
            )
            return

        try:
            # Get symbology parameters
            low_color = self.color_low_value.color()
            high_color = self.color_high_value.color()
            mode_enum = self.cbx_mode.currentData()  # This is an integer value (enum)
            num_classes = self.spinBox_classes.value()

            # Create symbol
            symbol = QgsSymbol.defaultSymbol(self.output_layer.geometryType())
            if not symbol:
                display_message_bar(
                    tr("Could not create default symbol."), level=Qgis.Warning
                )
                return

            # Create color ramp
            color_ramp = QgsGradientColorRamp(low_color, high_color)

            # Create renderer
            renderer = QgsGraduatedSymbolRenderer(self.name_field)
            renderer.setSourceSymbol(symbol.clone())
            renderer.setSourceColorRamp(color_ramp.clone())

            # Get classification method from registry based on mode_enum
            registry = QgsApplication.classificationMethodRegistry()
            method_id_map = {
                QgsGraduatedSymbolRenderer.Quantile: "Quantile",
                QgsGraduatedSymbolRenderer.EqualInterval: "EqualInterval",
                QgsGraduatedSymbolRenderer.Jenks: "Jenks",
                QgsGraduatedSymbolRenderer.StdDev: "StdDev",
                QgsGraduatedSymbolRenderer.Pretty: "PrettyBreaks",
            }

            # Get method ID based on mode_enum or default to EqualInterval
            method_id = method_id_map.get(mode_enum)
            if not method_id:
                display_message_bar(
                    tr("Unknown classification mode, using EqualInterval."),
                    level=Qgis.Warning,
                )
                method_id = "EqualInterval"

            # Get the classification method from registry
            classification_method = registry.method(method_id)
            if classification_method:
                # Set the method and transfer ownership
                renderer.setClassificationMethod(classification_method.clone())

                # Update classes
                renderer.updateClasses(self.output_layer, num_classes)

                # Apply renderer
                self.output_layer.setRenderer(renderer)
                self.output_layer.triggerRepaint()

                # Refresh layer tree
                if iface and iface.layerTreeView():
                    iface.layerTreeView().refreshLayerSymbology(self.output_layer.id())
            else:
                display_message_bar(
                    tr("Failed to get classification method."), level=Qgis.Warning
                )

        except Exception as e:
            display_message_bar(
                f"{tr('Error applying symbology:')} {str(e)}", level=Qgis.Critical
            )
            traceback.print_exc()

    def cancel_task_and_close(self):
        """Handles Cancel button click: cancels task if running, then rejects dialog."""
        if self.current_task and self.current_task.isActive():
            display_message_bar(
                tr("Attempting to cancel running task..."), level=Qgis.Info
            )
            self.current_task.cancel()
        else:
            self.reject()

    def reject(self):
        """Handle dialog rejection (e.g., Escape key, or called by cancel)."""
        if self.current_task and self.current_task.isActive():
            self.current_task.cancel()

        QApplication.restoreOverrideCursor()
        super().reject()
        self.signalAskCloseWindow.emit(0)

    def closeEvent(self, event):
        """Handle closing the dialog window via 'X' button."""
        if self.current_task and self.current_task.isActive():
            reply = QMessageBox.question(
                self,
                tr("Task Running"),
                tr(
                    "A task is currently running. Do you want to cancel it and close the window?"
                ),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                self.cancel_task_and_close()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
