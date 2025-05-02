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

import os
import traceback
from tempfile import NamedTemporaryFile
from typing import Dict, List, Tuple, Optional, Any

from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QMessageBox, QApplication, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QVariant
from qgis.utils import Qgis
from qgis.core import (
    QgsField, QgsGradientColorRamp, QgsGraduatedSymbolRenderer,
    QgsSymbol, QgsVectorFileWriter, QgsFeature, QgsVectorLayer,
    QgsProject, QgsGeometry, QgsMapLayerProxyModel, QgsFieldProxyModel, 
    QgsWkbTypes, QgsCoordinateTransformContext, QgsClassificationMethod,
    QgsApplication, QgsClassificationRange, QgsRendererRange
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from GeoPublicHealth.src.core.graph_toolbar import CustomNavigationToolbar
from GeoPublicHealth.src.core.tools import display_message_bar, tr
from GeoPublicHealth.src.core.exceptions import (
    GeoPublicHealthException, NoLayerProvidedException,
    FieldExistingException, FieldException
)
from GeoPublicHealth.src.core.stats import Stats
from GeoPublicHealth.src.utilities.resources import get_ui_class

FORM_CLASS = get_ui_class('analysis', 'composite_index.ui')

class CommonCompositeIndexDialog(QDialog):
    """Base class for the Composite Index dialog."""

    signalAskCloseWindow = pyqtSignal(int, name='signalAskCloseWindow')
    signalStatus = pyqtSignal(int, str, name='signalStatus')

    def __init__(self, parent=None):
        """
        Constructor for base class of Composite Index dialog.

        Parameters:
        - parent: Parent widget for the dialog.

        Attributes:
        - parent: Parent widget for the dialog.
        - name_field: Name field of the layer.
        - admin_layer: Administrative layer.
        - figure: The figure object for the dialog.
        - canvas: The canvas object for the dialog.
        - toolbar: The toolbar object for the dialog.
        - output_file_path: The output file path for the dialog.
        - output_layer: The output layer for the dialog.
        - selected_indicators: List of selected indicators.
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
        self.selected_indicators = []
        self.use_area = None
        self.use_point_layer = None

    def setup_ui(self):
        """
        Set up the UI for the dialog.
        """
        try:
            # Connect signals to slots
            self.button_browse.clicked.connect(self.open_file_browser)
            self.command_link_button.clicked.connect(self.add_indicator)
            
            # Use button_box_ok button connections
            ok_button = self.button_box_ok.button(QDialogButtonBox.Ok)
            cancel_button = self.button_box_ok.button(QDialogButtonBox.Cancel)
            
            if ok_button:
                ok_button.clicked.connect(self.run_stats)
            if cancel_button:
                cancel_button.clicked.connect(self.close_window)

            # Set initial state
            self.setup_indicator_list()
            self.setup_aggregation_layer()
            self.setup_indicator_field()
            
            # Setup matplotlib plot area if needed
            self.setup_plot_area()
            
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error during setup_ui: {str(e)}\n{traceback.format_exc()}",
                "GeoPublicHealth",
                Qgis.Critical
            )

    def setup_plot_area(self):
        """Set up the matplotlib plot area."""
        if hasattr(self, 'layout_plot') and self.layout_plot:
            try:
                self.figure = Figure(figsize=(5, 3), dpi=100)
                self.canvas = FigureCanvas(self.figure)
                self.toolbar = CustomNavigationToolbar(self.canvas, self)
                
                # Clear any existing widgets
                while self.layout_plot.count():
                    item = self.layout_plot.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
                
                # Add new widgets
                self.layout_plot.addWidget(self.toolbar)
                self.layout_plot.addWidget(self.canvas)
                
            except Exception as e:
                QgsMessageLog.logMessage(
                    f"Error setting up plot area: {str(e)}",
                    "GeoPublicHealth",
                    Qgis.Warning
                )

    def close_window(self):
        """
        Close the window
        """
        self.hide()
        self.signalAskCloseWindow.emit(0)

    def setup_indicator_list(self):
        """
        Setup the list of indicators
        """
        # Clear existing items
        self.cbx_mode.clear()

        # Define classification modes for QGIS 3.42
        modes = {
            'Quantile (equal count)': QgsGraduatedSymbolRenderer.Quantile,
            'Natural breaks': QgsGraduatedSymbolRenderer.Jenks,
            'Standard deviation': QgsGraduatedSymbolRenderer.StdDev,
            'Pretty breaks': QgsGraduatedSymbolRenderer.Pretty,
            'Equal interval': QgsGraduatedSymbolRenderer.EqualInterval,
        }

        for text, mode in modes.items():
            self.cbx_mode.addItem(text, mode)

        self.cbx_list_indicators.itemDoubleClicked.connect(self.remove_item)

    def setup_aggregation_layer(self):
        """
        Setup the aggregation layer
        """
        if hasattr(self, 'cbx_aggregation_layer'):
            self.cbx_aggregation_layer.setFilters(QgsMapLayerProxyModel.PolygonLayer)

    def setup_indicator_field(self):
        """
        Setup the indicator field
        """
        if not all(hasattr(self, attr) for attr in ['cbx_indicator_field', 'cbx_aggregation_layer']):
            return
            
        self.cbx_indicator_field.setFilters(QgsFieldProxyModel.Numeric)
        self.cbx_indicator_field.setLayer(self.cbx_aggregation_layer.currentLayer())
        self.cbx_aggregation_layer.layerChanged.connect(self.cbx_indicator_field.setLayer)
        self.cbx_aggregation_layer.layerChanged.connect(self.reset_field_indicator)
        self.reset_field_indicator()

    def reset_field_indicator(self):
        """Reset the indicator field selection."""
        if hasattr(self, 'cbx_indicator_field'):
            self.cbx_indicator_field.setCurrentIndex(0)

    def remove_item(self):
        """Remove selected item from indicators list."""
        if hasattr(self, 'cbx_list_indicators') and self.cbx_list_indicators.currentRow() >= 0:
            self.cbx_list_indicators.takeItem(self.cbx_list_indicators.currentRow())

    def add_indicator(self):
        """Add an indicator to the list."""
        if not hasattr(self, 'cbx_list_indicators'):
            return
            
        indicator_text = self.vector_indicator()
        
        # Check if indicator already exists in the list
        exists = False
        for index in range(self.cbx_list_indicators.count()):
            if self.cbx_list_indicators.item(index).text() == indicator_text:
                exists = True
                break
                
        if not exists:
            self.cbx_list_indicators.addItem(indicator_text)

    def vector_indicator(self) -> str:
        """
        Get the selected indicator with its direction.
        
        Returns:
            str: The indicator and direction in format "field | +/-"
        """
        if not hasattr(self, 'cbx_indicator_field'):
            return ""
            
        return f"{self.cbx_indicator_field.currentField()} | {self.vector_direction()}"

    def vector_direction(self) -> str:
        """
        Get the selected vector direction.
        
        Returns:
            str: "+" for positive or "-" for negative
        """
        if hasattr(self, 'radioButton_vector_positive') and self.radioButton_vector_positive.isChecked():
            return '+'
        return '-'

    def open_file_browser(self):
        """Method to open file browser and get output file path."""
        if not hasattr(self, 'le_output_filepath'):
            return
            
        # Get the last directory from QSettings if available
        last_dir = QSettings().value("GeoPublicHealth/lastDir", os.path.expanduser("~"))
        
        output_file, selected_filter = QFileDialog.getSaveFileName(
            self.parent, 
            tr('Save Output Layer'),
            last_dir,
            tr('ESRI Shapefile (*.shp);;GeoPackage (*.gpkg)')
        )
        
        if output_file:
            # Apply correct extension based on filter
            is_shp = '(*.shp)' in selected_filter
            is_gpkg = '(*.gpkg)' in selected_filter
            base, ext = os.path.splitext(output_file)
            
            if is_shp and not ext.lower() == '.shp':
                output_file = base + '.shp'
            elif is_gpkg and not ext.lower() == '.gpkg':
                output_file = base + '.gpkg'
            elif not ext:  # Default to Shapefile if no extension
                output_file += '.shp'
                
            self.le_output_filepath.setText(output_file)
            
            # Save the directory for next time
            QSettings().setValue("GeoPublicHealth/lastDir", os.path.dirname(output_file))

    def indicators_list(self) -> List[List[str]]:
        """
        Get the list of indicators and their directions.
        
        Returns:
            List[List[str]]: List of [indicator_name, direction] pairs
        """
        if not hasattr(self, 'cbx_list_indicators'):
            return []
            
        items = []
        for index in range(self.cbx_list_indicators.count()):
            items.append(self.cbx_list_indicators.item(index).text())
            
        return [item.split(" | ") for item in items]

    def run_stats(self):
        """Main function which does the process."""
        if not all(hasattr(self, attr) for attr in [
            'cbx_aggregation_layer', 'le_new_column', 'le_output_filepath'
        ]):
            display_message_bar(
                tr("UI elements not properly initialized"),
                level=Qgis.Critical
            )
            return

        self.setup_fields_and_output()

        try:
            self.set_application_state(is_busy=True)

            self.check_admin_layer()
            self.check_indicators()

            fields = self.admin_layer.fields()

            self.add_fields_to_layer(fields)
            self.calculate_composite_index(fields)

            self.add_output_layer_to_project()

            if hasattr(self, 'symbology') and self.symbology.isChecked():
                self.add_symbology()

            self.signalStatus.emit(3, tr('Successful process'))

        except GeoPublicHealthException as e:
            display_message_bar(msg=e.msg, level=e.level, duration=e.duration)
        except Exception as e:
            display_message_bar(
                f"{tr('Error processing composite index:')} {str(e)}",
                level=Qgis.Critical
            )
            traceback.print_exc()

        finally:
            self.set_application_state(is_busy=False)

    def check_admin_layer(self):
        """
        Check if the admin layer is provided.
        Raises NoLayerProvidedException if not provided.
        """
        if not self.admin_layer:
            raise NoLayerProvidedException

    def check_indicators(self):
        """
        Check the validity of the indicators.
        Raises FieldException if the list of indicators is empty.
        """
        if not self.use_point_layer and not self.use_area:
            if not hasattr(self, 'cbx_list_indicators') or self.cbx_list_indicators.count() == 0:
                raise FieldException(field_1='List Indicators should not be empty')
            
    def setup_fields_and_output(self):
        """Initialize fields and output settings."""
        if hasattr(self, 'cbx_aggregation_layer'):
            self.admin_layer = self.cbx_aggregation_layer.currentLayer()
            
        self.selected_indicators = self.indicators_list()
        
        if hasattr(self, 'le_new_column'):
            self.name_field = self.le_new_column.text() or self.le_new_column.placeholderText()
            
        self.output_file_path = self.get_output_file_path()

    def set_application_state(self, is_busy: bool):
        """
        Set the application state to busy or normal.
        
        Args:
            is_busy: Whether the application is busy processing
        """
        if hasattr(self, 'button_box_ok'):
            self.button_box_ok.setDisabled(is_busy)
            
        QApplication.setOverrideCursor(Qt.WaitCursor if is_busy else Qt.ArrowCursor)
        QApplication.processEvents()

    def get_output_file_path(self) -> str:
        """
        Get the output file path from the UI or create a temporary file.
        
        Returns:
            str: The output file path
        """
        if hasattr(self, 'le_output_filepath') and self.le_output_filepath.text():
            return self.le_output_filepath.text()

        # Create temporary file if no path specified
        with NamedTemporaryFile(delete=False, suffix='-geopublichealth.shp') as temp_file:
            return temp_file.name

    def add_fields_to_layer(self, fields):
        """
        Add the necessary fields to the output layer.
        
        Args:
            fields: The fields to add to
        """
        admin_layer_provider = self.admin_layer.dataProvider()
        if admin_layer_provider.fields().indexOf(self.name_field) != -1:
            raise FieldExistingException(field=self.name_field)

        # Add Z-score fields for each indicator
        for indicator_selected in self.selected_indicators:
            # Create a field with QVariant.Double for the Z-score
            fields.append(QgsField("Z" + indicator_selected[0], 6, "Real", 20, 10))  # 6 = QVariant.Double

        # Add the composite index field
        fields.append(QgsField(self.name_field, 6, "Real", 20, 10))  # 6 = QVariant.Double

    def calculate_composite_index(self, fields):
        """
        Calculate the composite index for each feature.
        
        Args:
            fields: The fields to use
        """
        # Determine output format based on file extension
        output_ext = os.path.splitext(self.output_file_path)[1].lower()
        driver_name = "GPKG" if output_ext == ".gpkg" else "ESRI Shapefile"
        
        # Setup save options
        save_options = QgsVectorFileWriter.SaveVectorOptions()
        save_options.driverName = driver_name
        save_options.encoding = "UTF-8"
        
        # If it's a GPKG, set the layer name
        if driver_name == "GPKG":
            save_options.layerName = self.name_field.replace(' ', '_')
            
        # Create the vector file writer
        file_writer = QgsVectorFileWriter.create(
            self.output_file_path,
            fields,
            QgsWkbTypes.Polygon,
            self.admin_layer.crs(),
            QgsProject.instance().transformContext(),
            save_options
        )
        
        if file_writer.hasError():
            error_message = file_writer.errorMessage()
            raise GeoPublicHealthException(msg=f"Error creating output file: {error_message}")

        # Calculate statistics for each indicator
        stats = self.calculate_stats()

        # Process each feature
        for feature in self.admin_layer.getFeatures():
            attributes, composite_index_value = self.calculate_attributes_and_composite_index(feature, stats)
            new_feature = self.create_new_feature(feature, attributes)
            file_writer.addFeature(new_feature)

        # Clean up
        del file_writer

    def calculate_stats(self) -> Dict[str, Stats]:
        """
        Calculate statistics for each indicator.
        
        Returns:
            Dict[str, Stats]: Dictionary of statistics objects by indicator name
        """
        stats = {}
        for indicator_selected in self.selected_indicators:
            values = self.get_feature_values(indicator_selected)
            stats[str(indicator_selected[0])] = Stats(values)

        return stats

    def get_feature_values(self, indicator_selected) -> List[float]:
        """
        Get the values for all features for a given indicator.
        
        Args:
            indicator_selected: The indicator to get values for
            
        Returns:
            List[float]: List of values for all features
        """
        values = []
        indicator_selected_name = str(indicator_selected[0])
        
        for feature in self.admin_layer.getFeatures():
            index = self.admin_layer.fields().indexOf(indicator_selected_name)
            
            # Get the value, default to 0.0 if null
            value = 0.0
            if feature[index] not in (None, NULL):
                try:
                    value = float(feature[index])
                except (ValueError, TypeError):
                    # If conversion fails, use 0.0
                    pass
                    
            values.append(value)

        return values

    def calculate_attributes_and_composite_index(self, feature, stats) -> Tuple[List[Any], float]:
        """
        Calculates the attributes and composite index value for a feature.

        Args:
            feature: A QgsFeature object
            stats: Dictionary of statistics by indicator name

        Returns:
            Tuple[List[Any], float]: The feature attributes and composite index value
        """
        attributes = feature.attributes()
        composite_index_value = 0.0

        for indicator in self.selected_indicators:
            name = str(indicator[0])
            index = self.admin_layer.fields().indexOf(name)
            
            # Get value, default to 0.0 if null
            value = 0.0
            if feature[index] not in (None, NULL):
                try:
                    value = float(feature[index])
                except (ValueError, TypeError):
                    pass
            
            # Calculate Z-score
            zscore = 0.0
            if stats[name].standard_deviation() > 0:
                zscore = (value - stats[name].average()) / stats[name].standard_deviation()

            attributes.append(float(zscore))
            composite_index_value += self.calculate_composite_index_value(indicator, zscore)

        attributes.append(float(composite_index_value))
        return attributes, composite_index_value

    def calculate_composite_index_value(self, indicator_selected, zscore) -> float:
        """
        Calculate the composite index value component for an indicator.
        
        Args:
            indicator_selected: The indicator
            zscore: The Z-score for this indicator
            
        Returns:
            float: The component value for this indicator
        """
        # Invert Z-score if the indicator direction is positive
        return -zscore if indicator_selected[1] == '+' else zscore

    def create_new_feature(self, feature, attributes) -> QgsFeature:
        """
        Create a new feature with the given attributes.
        
        Args:
            feature: The source feature
            attributes: The attributes for the new feature
            
        Returns:
            QgsFeature: The new feature
        """
        new_feature = QgsFeature()
        new_geom = QgsGeometry(feature.geometry())
        new_feature.setAttributes(attributes)
        new_feature.setGeometry(new_geom)

        return new_feature

    def add_output_layer_to_project(self):
        """Add the output layer to the QGIS project."""
        if not self.output_file_path:
            return
            
        # Determine if GeoPackage or Shapefile
        is_gpkg = self.output_file_path.lower().endswith('.gpkg')
        
        # Construct layer URI
        if is_gpkg:
            layer_name = self.name_field.replace(' ', '_')
            layer_uri = f"{self.output_file_path}|layername={layer_name}"
        else:
            layer_uri = self.output_file_path
            
        # Create vector layer
        self.output_layer = QgsVectorLayer(layer_uri, self.name_field, 'ogr')
        
        if not self.output_layer.isValid():
            display_message_bar(
                tr("Output layer invalid"),
                level=Qgis.Critical
            )
            return
            
        # Get unique layer name
        unique_layer_name = self.get_unique_layer_name(self.name_field)
        self.output_layer.setName(unique_layer_name)

        # Add to project
        QgsProject.instance().addMapLayer(self.output_layer)

    def get_unique_layer_name(self, base_name: str) -> str:
        """
        Get a unique layer name for the QGIS project.
        
        Args:
            base_name: The base name to start with
            
        Returns:
            str: A unique layer name
        """
        layer_name = base_name
        suffix = 1
        while QgsProject.instance().mapLayersByName(layer_name):
            layer_name = f"{base_name}_{suffix}"
            suffix += 1
        return layer_name

    def draw_plot(self, data):
        """
        Draw the plot and display it in the canvas.

        Args:
            data: The data to display
        """
        if not (self.figure and self.canvas):
            return
            
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            if not isinstance(data, list) or not data:
                ax.text(0.5, 0.5, tr("No data to plot"), ha='center', va='center')
            else:
                # Filter valid values
                valid_indices = [i for i, val in enumerate(data) if val is not None]
                valid_values = [data[i] for i in valid_indices]
                
                if valid_values:
                    ax.plot(valid_indices, valid_values, 'b*-', markersize=4)
                else:
                    ax.text(0.5, 0.5, tr("No valid data points to plot"), ha='center', va='center')
                    
            ax.set_xlabel(tr('Polygon Feature Index'))
            ax.set_ylabel(self.name_field if self.name_field else tr("Calculated Value"))
            ax.set_title(tr("Composite Index Values"))
            ax.grid(True)
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            display_message_bar(
                f"{tr('Error drawing plot:')} {str(e)}",
                level=Qgis.Critical
            )
            traceback.print_exc()

    def add_symbology(self) -> None:
        """
        Adds symbology to the output layer
        """
        if not self.output_layer or not self.output_layer.isValid():
            display_message_bar(tr("Cannot apply symbology, output layer is invalid."), level=Qgis.Warning)
            return
            
        try:
            # Get symbology parameters
            low_color = self.color_low_value.color()
            high_color = self.color_high_value.color()
            mode_enum = self.cbx_mode.currentData()  # Get the enum value directly
            num_classes = self.spinBox_classes.value()
            
            # Create symbol
            symbol = QgsSymbol.defaultSymbol(self.output_layer.geometryType())
            if not symbol:
                display_message_bar(tr("Could not create default symbol."), level=Qgis.Warning)
                return
                
            # Create color ramp
            color_ramp = QgsGradientColorRamp(low_color, high_color)
            
            # Method 1: Use QgsClassificationMethod with registry (QGIS 3.42 recommended approach)
            # First create the renderer with the field name
            renderer = QgsGraduatedSymbolRenderer(self.name_field)
            renderer.setSourceSymbol(symbol.clone())
            renderer.setSourceColorRamp(color_ramp.clone())
            
            # Get classification method from registry
            registry = QgsApplication.classificationMethodRegistry()
            if not registry:
                display_message_bar(tr("Cannot access classification registry."), level=Qgis.Warning)
                return
                
            # Map mode_enum to method ID
            method_id_map = {
                QgsGraduatedSymbolRenderer.Quantile: 'Quantile',
                QgsGraduatedSymbolRenderer.EqualInterval: 'EqualInterval',
                QgsGraduatedSymbolRenderer.Jenks: 'Jenks',
                QgsGraduatedSymbolRenderer.StdDev: 'StdDev',
                QgsGraduatedSymbolRenderer.Pretty: 'PrettyBreaks'
            }
            
            method_id = method_id_map.get(mode_enum, 'EqualInterval')
            classification_method = registry.method(method_id)
            
            if classification_method:
                # Set method and update classes
                renderer.setClassificationMethod(classification_method.clone())
                renderer.updateClasses(self.output_layer, num_classes)
                
                # Apply renderer
                self.output_layer.setRenderer(renderer)
                self.output_layer.triggerRepaint()
                
                # Refresh layer tree - without using iface
                # Try to get layer tree from the project instead
                from qgis.core import QgsProject
                project = QgsProject.instance()
                if project:
                    # Emit dataChanged signal to refresh symbology
                    layer_id = self.output_layer.id()
                    root = project.layerTreeRoot()
                    if root:
                        layer_node = root.findLayer(layer_id)
                        if layer_node:
                            layer_node.setCustomProperty("refreshLegend", 1)
            else:
                display_message_bar(tr("Classification method not found."), level=Qgis.Warning)
                
        except Exception as e:
            display_message_bar(
                f"{tr('Error applying symbology:')} {str(e)}",
                level=Qgis.Critical
            )
            traceback.print_exc()

class CompositeIndexDialog(CommonCompositeIndexDialog, FORM_CLASS):
    """Dialog implementation for Composite Index."""
    
    def __init__(self, parent=None):
        """
        Constructor for the Composite Index dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        FORM_CLASS.setupUi(self, self)

        # Set NULL constant for comparison
        global NULL
        NULL = QVariant()
        
        # Setup UI
        self.setup_ui()

    def run_stats(self):
        """Main function which do the process."""
        super().run_stats()