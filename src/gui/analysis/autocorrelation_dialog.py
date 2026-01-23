# -*- coding: utf-8 -*-
"""
/***************************************************************************

                               GeoPublicHealth
                                 A QGIS plugin

                              -------------------
        begin                : 2016-02-17
        copyright            : (C) 2016 by ePublicHealth
        email                : manuel@epublichealth.co

        Based on the work of Geohealth
        begin                : 2014-08-20
        copyright            : (C) 2014 by Etienne Trimaille
        email                : etienne@trimaille.eu
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

import os.path
import warnings
import traceback
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional, Union, Any, Tuple

from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QApplication, QFileDialog
from qgis.PyQt.QtCore import QVariant, Qt, pyqtSignal, QSettings
from qgis.PyQt.QtGui import QColor

from qgis.utils import Qgis
from qgis.core import (
    QgsField,
    QgsRendererCategory,
    QgsCategorizedSymbolRenderer,
    QgsGradientColorRamp,
    QgsGraduatedSymbolRenderer,
    QgsSymbol,
    QgsVectorFileWriter,
    QgsFeature,
    QgsVectorLayer,
    QgsProject,
    QgsGeometry,
    QgsMapLayerProxyModel,
    QgsFieldProxyModel,
    QgsWkbTypes,
    QgsApplication,
    QgsClassificationMethod,
    QgsCoordinateTransformContext,
    QgsMessageLog,
)
from qgis.gui import QgsFieldComboBox, QgsMapLayerComboBox

import numpy as np

# Import PySAL libraries with fallbacks
try:
    # Filter out specific PySAL deprecation warnings
    warnings.filterwarnings(
        "ignore",
        category=FutureWarning,
        message="Objects based on the `Geometry` class will deprecated",
    )
    warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed file")

    import libpysal
    from libpysal.weights import Queen, Rook
    from esda.moran import Moran_Local

    # Check if geopandas is available for modern approach
    try:
        import geopandas as gpd

        GEOPANDAS_AVAILABLE = True
    except ImportError:
        GEOPANDAS_AVAILABLE = False

    PYSAL_AVAILABLE = True
except ImportError:
    PYSAL_AVAILABLE = False
    GEOPANDAS_AVAILABLE = False

from geopublichealth.src.core.graph_toolbar import CustomNavigationToolbar
from geopublichealth.src.core.tools import display_message_bar, tr
from geopublichealth.src.core.exceptions import (
    GeoPublicHealthException,
    NoLayerProvidedException,
    FieldExistingException,
    NotANumberException,
)
from geopublichealth.src.core.stats import Stats
from geopublichealth.src.utilities.resources import get_ui_class

FORM_CLASS = get_ui_class("analysis", "autocorrelation.ui")


class CommonAutocorrelationDialog(QDialog):
    """
    Common dialog class for Autocorrelation analysis.
    """

    signalAskCloseWindow = pyqtSignal(int, name="signalAskCloseWindow")
    signalStatus = pyqtSignal(int, str, name="signalStatus")

    def __init__(self, parent=None):
        """
        Constructor for the Autocorrelation dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.parent = parent
        self.name_field = None
        self.admin_layer = None
        self.figure = None
        self.canvas = None
        self.toolbar = None
        self.output_file_path = None
        self.output_layer = None
        self.use_area = None
        self.layer = None

        # Log dependency availability
        QgsMessageLog.logMessage(
            f"PySAL available: {PYSAL_AVAILABLE}, GeoPandas available: {GEOPANDAS_AVAILABLE}",
            "GeoPublicHealth",
            Qgis.Info,
        )

        # Check if PySAL is available
        if not PYSAL_AVAILABLE:
            display_message_bar(
                tr(
                    "PySAL library is required for spatial autocorrelation analysis. "
                    "Please install libpysal and esda packages."
                ),
                level=Qgis.Critical,
                duration=10,
            )

    def setup_ui(self):
        """Set up the UI components."""
        try:
            # Connect signals to slots
            if hasattr(self, "button_browse"):
                self.button_browse.clicked.connect(self.open_file_browser)

            if hasattr(self, "button_box_ok"):
                ok_button = self.button_box_ok.button(QDialogButtonBox.Ok)
                cancel_button = self.button_box_ok.button(QDialogButtonBox.Cancel)

                if ok_button:
                    ok_button.clicked.connect(self.run_stats)
                if cancel_button:
                    cancel_button.clicked.connect(self.hide)
                    cancel_button.clicked.connect(
                        lambda: self.signalAskCloseWindow.emit(0)
                    )

            # Set up layer and field selectors
            if hasattr(self, "cbx_aggregation_layer"):
                self.cbx_aggregation_layer.setFilters(
                    QgsMapLayerProxyModel.PolygonLayer
                )

            if hasattr(self, "cbx_indicator_field") and hasattr(
                self, "cbx_aggregation_layer"
            ):
                self.cbx_indicator_field.setFilters(QgsFieldProxyModel.Numeric)
                self.cbx_indicator_field.setLayer(
                    self.cbx_aggregation_layer.currentLayer()
                )
                self.cbx_aggregation_layer.layerChanged.connect(
                    self.cbx_indicator_field.setLayer
                )

            # LISA categories with colors and labels
            self.lisa = {
                1: ("#b92815", "High - High"),
                2: ("#3f70df", "Low - High"),
                3: ("#aecbdd", "Low - Low"),
                4: ("#e79e2c", "High - Low"),
            }

            # Display information about available libraries
            if hasattr(self, "label_library_info"):
                if GEOPANDAS_AVAILABLE:
                    self.label_library_info.setText(
                        tr("Using modern GeoPandas approach")
                    )
                elif PYSAL_AVAILABLE:
                    self.label_library_info.setText(tr("Using legacy PySAL approach"))
                else:
                    self.label_library_info.setText(
                        tr("Required libraries not available")
                    )

        except Exception as e:
            display_message_bar(
                f"{tr('Error setting up UI:')} {str(e)}", level=Qgis.Critical
            )
            traceback.print_exc()

    def open_file_browser(self):
        """Method to open file browser and get output file path."""
        if not hasattr(self, "le_output_filepath"):
            return

        # Get the last directory from QSettings if available
        last_dir = QSettings().value("GeoPublicHealth/lastDir", os.path.expanduser("~"))

        output_file, selected_filter = QFileDialog.getSaveFileName(
            self.parent,
            tr("Save Output Layer"),
            last_dir,
            tr("ESRI Shapefile (*.shp);;GeoPackage (*.gpkg)"),
        )

        if output_file:
            # Apply correct extension based on filter
            is_shp = "(*.shp)" in selected_filter
            is_gpkg = "(*.gpkg)" in selected_filter
            base, ext = os.path.splitext(output_file)

            if is_shp and not ext.lower() == ".shp":
                output_file = base + ".shp"
            elif is_gpkg and not ext.lower() == ".gpkg":
                output_file = base + ".gpkg"
            elif not ext:  # Default to Shapefile if no extension
                output_file += ".shp"

            self.le_output_filepath.setText(output_file)

            # Save the directory for next time
            QSettings().setValue(
                "GeoPublicHealth/lastDir", os.path.dirname(output_file)
            )

    def run_stats(self):
        """Main analysis function."""
        if not PYSAL_AVAILABLE:
            display_message_bar(
                tr(
                    "PySAL library is required for spatial autocorrelation analysis. "
                    "Please install libpysal and esda packages."
                ),
                level=Qgis.Critical,
            )
            return

        try:
            # Prepare UI for processing
            self.prepare_run()

            # Get input parameters
            self.admin_layer = self.cbx_aggregation_layer.currentLayer()
            input_name = self.admin_layer.name()
            field = self.cbx_indicator_field.currentField()

            # Get the layer from the project
            self.layer = QgsProject.instance().mapLayersByName(input_name)[0]
            self.output_file_path = self.le_output_filepath.text()

            # Validate input parameters
            self.check_layer_and_file_path()
            crs_admin_layer = self.admin_layer.crs()

            # Get field structure and add new fields
            admin_layer_provider = self.layer.dataProvider()
            fields = admin_layer_provider.fields()
            self.check_existing_field(fields)
            self.append_new_fields(fields)

            # Prepare file writer
            file_writer = self.prepare_file_writer(fields, crs_admin_layer)

            # Calculate spatial weights and local Moran's I
            # Use modern approach if available, fall back to legacy approach
            if GEOPANDAS_AVAILABLE:
                QgsMessageLog.logMessage(
                    "Using modern GeoPandas approach for spatial weights",
                    "GeoPublicHealth",
                    Qgis.Info,
                )
                w = self.get_weights_modern()
                y = self.get_indicator_values_modern(field)
            else:
                QgsMessageLog.logMessage(
                    "Using legacy PySAL approach for spatial weights",
                    "GeoPublicHealth",
                    Qgis.Info,
                )
                w = self.get_weights_legacy()
                y = self.get_indicator_values_legacy(field)

            # Calculate Local Moran's I
            lm = self.calculate_moran_local(y, w)

            # Get significant clusters (p <= 0.05)
            sig_q = lm.q * (lm.p_sim <= 0.05)

            # Create output features
            self.create_output_features(file_writer, lm, sig_q)
            del file_writer

            # Create output layer and add symbology
            self.output_layer = self.create_output_layer(field)
            QgsProject.instance().addMapLayer(self.output_layer)
            self.add_symbology()

            # Success message
            self.signalStatus.emit(3, tr("Successful process"))

        except GeoPublicHealthException as e:
            display_message_bar(msg=e.msg, level=e.level, duration=e.duration)
        except Exception as e:
            display_message_bar(
                f"{tr('Error processing autocorrelation:')} {str(e)}",
                level=Qgis.Critical,
            )
            traceback.print_exc()
        finally:
            self.end_run()

    def prepare_run(self):
        """Prepare UI for processing."""
        if hasattr(self, "button_box_ok"):
            self.button_box_ok.setDisabled(True)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()

    def end_run(self):
        """Reset UI after processing."""
        if hasattr(self, "button_box_ok"):
            self.button_box_ok.setDisabled(False)
        QApplication.restoreOverrideCursor()
        QApplication.processEvents()

    def check_layer_and_file_path(self):
        """Validate layer and output path."""
        if not self.admin_layer:
            raise NoLayerProvidedException

        # Create temporary file if no output path specified
        if not self.output_file_path:
            with NamedTemporaryFile(
                delete=False, suffix="-geopublichealth.shp"
            ) as temp_file:
                self.output_file_path = temp_file.name
        else:
            # Check if file exists and create unique name if needed
            if os.path.exists(self.output_file_path):
                base, extension = os.path.splitext(self.output_file_path)
                counter = 1
                while os.path.exists(self.output_file_path):
                    self.output_file_path = f"{base}_{counter}{extension}"
                    counter += 1

    def check_existing_field(self, fields):
        """Check if output fields already exist in the layer."""
        for field_name in ["LISA_P", "LISA_Z", "LISA_Q", "LISA_I", "LISA_C"]:
            if fields.indexOf(field_name) != -1:
                raise FieldExistingException(field=field_name)

    def append_new_fields(self, fields):
        """Add new fields for LISA results."""
        # Add the LISA result fields
        fields.append(QgsField("LISA_P", 6, "Real", 10, 6))  # P-value
        fields.append(QgsField("LISA_Z", 6, "Real", 10, 6))  # Z-score
        fields.append(QgsField("LISA_Q", 2, "Integer", 1, 0))  # Quadrant
        fields.append(QgsField("LISA_I", 6, "Real", 10, 6))  # Local Moran's I
        fields.append(QgsField("LISA_C", 2, "Integer", 1, 0))  # Cluster (sig. quadrant)

    def prepare_file_writer(self, fields, crs_admin_layer):
        """Prepare the output file writer."""
        # Determine output format based on file extension
        output_ext = os.path.splitext(self.output_file_path)[1].lower()
        driver_name = "GPKG" if output_ext == ".gpkg" else "ESRI Shapefile"

        # Setup save options
        save_options = QgsVectorFileWriter.SaveVectorOptions()
        save_options.driverName = driver_name
        save_options.encoding = "UTF-8"

        # If it's a GPKG, set the layer name
        if driver_name == "GPKG":
            field_name = self.cbx_indicator_field.currentField()
            save_options.layerName = f"LISA_{field_name}".replace(" ", "_")

        # Create the vector file writer
        file_writer = QgsVectorFileWriter.create(
            self.output_file_path,
            fields,
            QgsWkbTypes.Polygon,
            crs_admin_layer,
            QgsProject.instance().transformContext(),
            save_options,
        )

        if file_writer.hasError():
            error_message = file_writer.errorMessage()
            raise GeoPublicHealthException(
                msg=f"Error creating output file: {error_message}"
            )

        return file_writer

    def get_weights_modern(self):
        """
        Get spatial weights matrix using GeoPandas (modern approach).

        Returns:
            libpysal.weights: Spatial weights matrix
        """
        try:
            contiguity_index = 0  # Default to Queen
            if hasattr(self, "cbx_contiguity"):
                contiguity_index = self.cbx_contiguity.currentIndex()

            # Read the shapefile using geopandas
            gdf = gpd.read_file(self.admin_layer.source())

            # Create weights matrix
            if contiguity_index == 0:  # queen
                # Explicitly set use_index parameter to silence the warning
                w = Queen.from_dataframe(gdf, use_index=True)
            else:  # rook
                # Also update the Rook method for consistency
                w = Rook.from_dataframe(gdf, use_index=True)

            return w

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Modern weights approach failed, falling back to legacy: {str(e)}",
                "GeoPublicHealth",
                Qgis.Warning,
            )
            return self.get_weights_legacy()

    def get_weights_legacy(self):
        """
        Get spatial weights matrix using legacy PySAL approach.

        Returns:
            libpysal.weights: Spatial weights matrix
        """
        try:
            contiguity_index = 0  # Default to Queen
            if hasattr(self, "cbx_contiguity"):
                contiguity_index = self.cbx_contiguity.currentIndex()

            # Use context manager to ensure proper file closing
            with libpysal.io.open(self.admin_layer.source()) as shp_file:
                if contiguity_index == 0:  # queen
                    w = Queen.from_shapefile(self.admin_layer.source())
                else:  # rook
                    w = Rook.from_shapefile(self.admin_layer.source())

            return w

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error in legacy weights approach: {str(e)}",
                "GeoPublicHealth",
                Qgis.Critical,
            )
            raise

    def get_indicator_values_modern(self, field):
        """
        Get indicator values using GeoPandas (modern approach).

        Args:
            field: Field name containing indicator values

        Returns:
            numpy.ndarray: Array of indicator values
        """
        try:
            # Read the shapefile using geopandas
            gdf = gpd.read_file(self.admin_layer.source())

            # Get values of the specified field
            if field in gdf.columns:
                y = np.array(gdf[field])
                return y
            else:
                QgsMessageLog.logMessage(
                    f"Field '{field}' not found in GeoDataFrame, falling back to legacy method",
                    "GeoPublicHealth",
                    Qgis.Warning,
                )
                return self.get_indicator_values_legacy(field)

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Modern indicator approach failed, falling back to legacy: {str(e)}",
                "GeoPublicHealth",
                Qgis.Warning,
            )
            return self.get_indicator_values_legacy(field)

    def get_indicator_values_legacy(self, field):
        """
        Get indicator values using legacy PySAL approach.

        Args:
            field: Field name containing indicator values

        Returns:
            numpy.ndarray: Array of indicator values
        """
        try:
            # Use context manager to ensure proper file closing
            with libpysal.io.open(
                self.admin_layer.source().replace(".shp", ".dbf")
            ) as f:
                y = np.array(f.by_col[str(field)])
            return y

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error in legacy indicator approach: {str(e)}",
                "GeoPublicHealth",
                Qgis.Critical,
            )
            raise

    def calculate_moran_local(self, y, w):
        """
        Calculate Local Moran's I statistics.

        Args:
            y: Array of indicator values
            w: Spatial weights matrix

        Returns:
            esda.moran.Moran_Local: Local Moran's I statistics
        """
        try:
            return Moran_Local(y, w, transformation="r", permutations=999)
        except Exception as e:
            error_msg = tr("Error calculating Local Moran's I:")
            display_message_bar(f"{error_msg} {str(e)}", level=Qgis.Critical)
            raise

    def create_output_features(self, file_writer, lm, sig_q):
        """
        Create output features with LISA statistics.

        Args:
            file_writer: QgsVectorFileWriter
            lm: Local Moran's I statistics
            sig_q: Significant quadrants
        """
        try:
            for i, feature in enumerate(self.admin_layer.getFeatures()):
                attributes = feature.attributes()

                # Add LISA statistics as attributes
                attributes.append(float(lm.p_sim[i]))  # P-value
                attributes.append(float(lm.z_sim[i]))  # Z-score
                attributes.append(int(lm.q[i]))  # Quadrant
                attributes.append(float(lm.Is[i]))  # Local Moran's I
                attributes.append(int(sig_q[i]))  # Significant quadrant

                # Create new feature with same geometry
                new_feature = QgsFeature()
                new_geom = QgsGeometry(feature.geometry())
                new_feature.setAttributes(attributes)
                new_feature.setGeometry(new_geom)

                # Add to output file
                file_writer.addFeature(new_feature)
        except Exception as e:
            display_message_bar(
                f"{tr('Error creating output features:')} {str(e)}", level=Qgis.Critical
            )
            raise

    def create_output_layer(self, field):
        """
        Create output layer from the output file.

        Args:
            field: Field name for layer naming

        Returns:
            QgsVectorLayer: Output layer
        """
        if not self.output_file_path:
            return

        # Determine if GeoPackage or Shapefile
        is_gpkg = self.output_file_path.lower().endswith(".gpkg")

        # Construct layer URI
        if is_gpkg:
            layer_name = f"LISA_{field}".replace(" ", "_")
            layer_uri = f"{self.output_file_path}|layername={layer_name}"
        else:
            layer_uri = self.output_file_path

        # Create vector layer
        output_layer = QgsVectorLayer(layer_uri, "LISA Moran's I - " + field, "ogr")

        if not output_layer.isValid():
            display_message_bar(tr("Output layer invalid"), level=Qgis.Critical)
            raise GeoPublicHealthException(
                msg=tr("Failed to create valid output layer")
            )

        return output_layer

    def add_symbology(self):
        """Add symbology to the output layer."""
        try:
            # Create categories for LISA quadrants
            categories = []
            for lisaCategory, (color, label) in self.lisa.items():
                sym = QgsSymbol.defaultSymbol(self.output_layer.geometryType())
                sym.setColor(QColor(color))
                category = QgsRendererCategory(lisaCategory, sym, label)
                categories.append(category)

            # Create a new layer for significance
            # Determine if GeoPackage or Shapefile
            is_gpkg = self.output_file_path.lower().endswith(".gpkg")

            # Create a new layer
            if is_gpkg:
                # For GeoPackage, clone the original layer
                field_name = self.cbx_indicator_field.currentField()
                new_layer_name = f"LISA_{field_name}_sig".replace(" ", "_")

                # Need to create a new copy in the GeoPackage
                options = QgsVectorFileWriter.SaveVectorOptions()
                options.driverName = "GPKG"
                options.layerName = new_layer_name
                options.actionOnExistingFile = (
                    QgsVectorFileWriter.CreateOrOverwriteLayer
                )

                # Create the new layer
                result = QgsVectorFileWriter.writeAsVectorFormat(
                    self.output_layer, self.output_file_path, options
                )

                if result[0] != QgsVectorFileWriter.NoError:
                    display_message_bar(
                        tr("Failed to create significance layer"), level=Qgis.Warning
                    )
                    return

                # Load the new layer
                layer_uri = f"{self.output_file_path}|layername={new_layer_name}"
                new_layer = QgsVectorLayer(
                    layer_uri, self.output_layer.name() + " significance test", "ogr"
                )
            else:
                # For Shapefile, just create a new layer with the same source
                new_layer = QgsVectorLayer(
                    self.output_layer.source(),
                    self.output_layer.name() + " significance test",
                    self.output_layer.providerType(),
                )

            # Set layer opacity
            self.output_layer.setOpacity(0.4)
            QgsProject.instance().addMapLayer(new_layer)

            # Set categorized renderer for LISA quadrants
            renderer = QgsCategorizedSymbolRenderer("LISA_Q", categories)
            self.output_layer.setRenderer(renderer)

            # Set graduated renderer for significance
            symbol = QgsSymbol.defaultSymbol(new_layer.geometryType())
            color_ramp = QgsGradientColorRamp(QColor(0, 0, 0), QColor(255, 0, 0))

            # Get registry and method for classification
            registry = QgsApplication.classificationMethodRegistry()
            method_id = "Jenks"  # Natural breaks
            classification_method = registry.method(method_id)

            if classification_method:
                # Set method and create renderer
                renderer = QgsGraduatedSymbolRenderer("LISA_C")
                renderer.setSourceSymbol(symbol.clone())
                renderer.setSourceColorRamp(color_ramp.clone())
                renderer.setClassificationMethod(classification_method.clone())
                renderer.updateClasses(new_layer, 4)

                # Apply renderer
                new_layer.setRenderer(renderer)
                new_layer.setOpacity(0.4)
                new_layer.triggerRepaint()

                # Refresh layer tree
                root = QgsProject.instance().layerTreeRoot()
                if root:
                    layer_node = root.findLayer(new_layer.id())
                    if layer_node:
                        layer_node.setCustomProperty("refreshLegend", 1)
            else:
                # Fallback to older method if classification method not available
                renderer = QgsGraduatedSymbolRenderer.createRenderer(
                    new_layer,
                    "LISA_C",
                    4,
                    QgsGraduatedSymbolRenderer.Jenks,
                    symbol,
                    color_ramp,
                )
                new_layer.setRenderer(renderer)
                new_layer.setOpacity(0.4)
                new_layer.triggerRepaint()

        except Exception as e:
            display_message_bar(
                f"{tr('Error applying symbology:')} {str(e)}", level=Qgis.Critical
            )
            traceback.print_exc()


class AutocorrelationDialog(CommonAutocorrelationDialog, FORM_CLASS):
    """
    Dialog implementation for Autocorrelation analysis.
    """

    def __init__(self, parent=None):
        """
        Constructor for the Autocorrelation dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        FORM_CLASS.setupUi(self, self)

        # Set NULL constant for comparison
        global NULL
        NULL = QVariant()

        self.use_area = False
        self.setup_ui()

    def run_stats(self):
        """Main function which do the process."""
        super().run_stats()
