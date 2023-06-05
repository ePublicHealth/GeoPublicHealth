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

from tempfile import NamedTemporaryFile
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QMessageBox, QApplication, QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal, QVariant
from qgis.utils import Qgis
from qgis.core import (
    QgsField, QgsGradientColorRamp, QgsGraduatedSymbolRenderer,
    QgsSymbol, QgsVectorFileWriter, QgsFeature, QgsVectorLayer,
    QgsProject, QgsGeometry, QgsMapLayerProxyModel, QgsFieldProxyModel, QgsWkbTypes
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

    signalAskCloseWindow = pyqtSignal(int, name='signalAskCloseWindow')
    signalStatus = pyqtSignal(int, str, name='signalStatus')

    def __init__(self, parent=None):
        """
        Constructor for base class of Incidence and Density dialogs.

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
        - use_area: Boolean for whether to use the area of the polygon or the population field.
        - use_point_layer: Boolean for whether to use a point layer or a field in the polygon layer.
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
        self.use_point_layer = None


    def setup_ui(self):
        """
        Set up the UI for the dialog.
        """
        try:
            # Connect signals to slots
            self.button_browse.clicked.connect(self.open_file_browser)
            self.command_link_button.clicked.connect(self.add_indicator)
            self.button_box_ok.button(QDialogButtonBox.Ok).clicked.connect(self.run_stats)
            self.button_box_ok.button(QDialogButtonBox.Cancel).clicked.connect(self.close_window)

            # Set initial state
            self.setup_indicator_list()
            self.setup_aggregation_layer()
            self.setup_indicator_field()
        except Exception as e:
            print(f"Error during setup_ui: {e}")



    def close_window(self):
        """
        Close the window
        """
        self.hide()
        self.signalAskCloseWindow.emit()

    def setup_indicator_list(self):
        """
        Setup the list of indicators
        """

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
        self.cbx_aggregation_layer.setFilters(QgsMapLayerProxyModel.PolygonLayer)

    def setup_indicator_field(self):
        """
        Setup the indicator field
        """
        self.cbx_indicator_field.setFilters(QgsFieldProxyModel.Numeric)
        self.cbx_indicator_field.setLayer(self.cbx_aggregation_layer.currentLayer())
        self.cbx_aggregation_layer.layerChanged.connect(self.cbx_indicator_field.setLayer)
        self.cbx_aggregation_layer.layerChanged.connect(self.reset_field_indicator)
        self.reset_field_indicator()

    def reset_field_indicator(self):
        self.cbx_indicator_field.setCurrentIndex(0)

    def remove_item(self):
        self.cbx_list_indicators.takeItem(self.cbx_list_indicators.currentRow())

    def add_indicator(self):
        if not any(self.cbx_list_indicators.item(index).text() == self.vector_indicator()
                   for index in range(self.cbx_list_indicators.count())):
            self.cbx_list_indicators.addItem(self.vector_indicator())

    def vector_indicator(self):
        return f"{self.cbx_indicator_field.currentField()} | {self.vector_direction()}"

    def vector_direction(self):
        return '+' if self.radioButton_vector_positive.isChecked() else '-'

    def open_file_browser(self):
        """Method to open file browser and get output file path."""
        output_file, __ = QFileDialog.getSaveFileName(
            self.parent, tr('Save shapefile'), filter='SHP (*.shp)')
        self.le_output_filepath.setText(output_file)

    def indicators_list(self):
        items = [self.cbx_list_indicators.item(index).text()
                 for index in range(self.cbx_list_indicators.count())]
        return [item.split(" | ") for item in items]

    def run_stats(self):
        """Main function which does the process."""

        self.setup_fields_and_output()

        try:
            self.set_application_state(is_busy=True)

            self.check_admin_layer()
            self.check_indicators()

            fields = self.admin_layer.fields()

            self.add_fields_to_layer(fields)
            self.calculate_composite_index(fields)

            self.add_output_layer_to_project()

            if self.symbology.isChecked():
                self.add_symbology()

            self.signalStatus.emit(3, tr('Successful process'))

        except GeoPublicHealthException as e:
            display_message_bar(msg=e.msg, level=e.level, duration=e.duration)

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
            if not self.cbx_list_indicators.count():
                raise FieldException(field_1='List Indicators should not be empty')
            
    def setup_fields_and_output(self):
        self.admin_layer = self.cbx_aggregation_layer.currentLayer()
        self.selected_indicators = self.indicators_list()
        self.name_field = self.le_new_column.placeholderText() if not self.name_field else self.name_field
        self.output_file_path = self.get_output_file_path()

    def set_application_state(self, is_busy):
        self.button_box_ok.setDisabled(is_busy)
        QApplication.setOverrideCursor(Qt.WaitCursor if is_busy else Qt.ArrowCursor)
        QApplication.processEvents()

    def get_output_file_path(self):
        if self.le_output_filepath.text():
            return self.le_output_filepath.text()

        with NamedTemporaryFile(delete=False, suffix='-geopublichealth.shp') as temp_file:
            return temp_file.name

    def add_fields_to_layer(self, fields):
        admin_layer_provider = self.admin_layer.dataProvider()
        if admin_layer_provider.fields().indexFromName(self.name_field) != -1:
            raise FieldExistingException(field=self.name_field)

        for indicator_selected in self.selected_indicators:
            fields.append(QgsField("Z" + indicator_selected[0], QVariant.Double))

        fields.append(QgsField(self.name_field, QVariant.Double))

    def calculate_composite_index(self, fields):
        file_writer = QgsVectorFileWriter(
            self.output_file_path,
            'utf-8',
            fields,
            QgsWkbTypes.Polygon,
            self.admin_layer.crs(),
            'ESRI Shapefile')

        stats = self.calculate_stats()

        for feature in self.admin_layer.getFeatures():
            attributes, composite_index_value = self.calculate_attributes_and_composite_index(feature, stats)
            new_feature = self.create_new_feature(feature, attributes)
            file_writer.addFeature(new_feature)

        del file_writer

    def calculate_stats(self):
        stats = {}
        for indicator_selected in self.selected_indicators:
            values = self.get_feature_values(indicator_selected)
            stats[str(indicator_selected[0])] = Stats(values)

        return stats

    def get_feature_values(self, indicator_selected):
        values = []
        indicator_selected_name = str(indicator_selected[0])
        for feature in self.admin_layer.getFeatures():
            index = self.admin_layer.fields().indexFromName(indicator_selected_name)
            value = float(feature[index]) if feature[index] else 0.0
            values.append(value)

        return values

    def calculate_attributes_and_composite_index(self, feature, stats):
        """
        Calculates the attributes and composite index value for a given feature using selected indicators and their stats.

        :param feature: A QgsFeature object representing the feature to calculate attributes and composite index value for.
        :type feature: QgsFeature

        :param stats: A dictionary containing the stats for each selected indicator.
        :type stats: dict

        :return: A tuple containing the attributes as a list of floats and the composite index value as a float.
        :rtype: tuple
        """
        attributes = feature.attributes()
        composite_index_value = 0.0

        for indicator in self.selected_indicators:
            name = str(indicator[0])
            index = self.admin_layer.fields().indexFromName(name)
            value = float(feature[index]) if feature[index] else 0.0
            zscore = (value - stats[name].average()) / stats[name].standard_deviation()

            attributes.append(float(zscore))
            composite_index_value += self.calculate_composite_index_value(indicator, zscore)

        attributes.append(float(composite_index_value))
        return attributes, composite_index_value


    def calculate_composite_index_value(self, indicator_selected, zscore):
        return -zscore if indicator_selected[1] == '+' else zscore

    def create_new_feature(self, feature, attributes):
        new_feature = QgsFeature()
        new_geom = QgsGeometry(feature.geometry())
        new_feature.setAttributes(attributes)
        new_feature.setGeometry(new_geom)

        return new_feature

    def add_output_layer_to_project(self):
        self.output_layer = QgsVectorLayer(self.output_file_path, self.name_field, 'ogr')
        unique_layer_name = self.get_unique_layer_name(self.name_field)
        self.output_layer.setName(unique_layer_name)

        # Check if a layer with the same name already exists
        existing_layers = QgsProject.instance().mapLayersByName(unique_layer_name)
        if existing_layers:
            unique_layer_name = self.get_unique_layer_name(unique_layer_name)
            self.output_layer.setName(unique_layer_name)

        QgsProject.instance().addMapLayer(self.output_layer)

    def get_unique_layer_name(self, base_name):
        layer_name = base_name
        suffix = 1
        while QgsProject.instance().mapLayersByName(layer_name):
            layer_name = f"{base_name}_{suffix}"
            suffix += 1
        return layer_name

    def draw_plot(self, data):
        """Function to draw the plot and display it in the canvas.

        :param data: The data to display
        :type data: list
        """
        ax = self.figure.add_subplot(111)

        ax.plot(data, '*-')
        ax.set_xlabel('Polygon')
        ax.set_ylabel(self.name_field)
        ax.grid()
        self.canvas.draw()

    def add_symbology(self) -> None:
        """
        Adds symbology to the output layer
        """

        # Get low and high colors, mode, and number of classes
        low_color = self.color_low_value.color()
        high_color = self.color_high_value.color()
        mode = self.cbx_mode.itemData(self.cbx_mode.currentIndex())
        num_classes = self.spinBox_classes.value()

        # Construct default symbol and color ramp
        default_symbol = QgsSymbol.defaultSymbol(QgsWkbTypes.geometryType(QgsWkbTypes.Polygon))
        color_ramp = QgsGradientColorRamp(low_color, high_color)

        # Create renderer and assign to output layer
        renderer = QgsGraduatedSymbolRenderer.createRenderer(
            self.output_layer,
            self.name_field,
            num_classes,
            mode,
            default_symbol,
            color_ramp)

        self.output_layer.setRenderer(renderer)

class CompositeIndexDialog(CommonCompositeIndexDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        FORM_CLASS.setupUi(self, self)

        self.setup_ui()

    def run_stats(self):
        """Main function which do the process."""
        super().run_stats()
