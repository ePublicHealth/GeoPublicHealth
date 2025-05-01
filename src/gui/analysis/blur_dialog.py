# -*- coding: utf-8 -*-
"""
/***************************************************************************

                                 GeoPublicHealth
                                 A QGIS plugin

                              -------------------
        begin                : 2014-08-20
        copyright            : (C) 2014 by Etienne Trimaille
                              (C) 2020-2024 by ePublicHealth/GeoPublicHealth Team
        email                : manuel.vidaurre@gmail.com
 ***************************************************************************/

/***************************************************************************
 * *
 * This program is free software; you can redistribute it and/or modify  *
 * it under the terms of the GNU General Public License as published by  *
 * the Free Software Foundation; either version 2 of the License, or     *
 * (at your option) any later version.                                   *
 * *
 ***************************************************************************/
"""

from os.path import dirname, basename
import traceback # For debugging unexpected errors

# QGIS Imports
from qgis.core import (
    QgsField,
    QgsFields,
    QgsVectorFileWriter,
    QgsProject,
    QgsVectorLayer,
    QgsMapLayerProxyModel,
    QgsWkbTypes,
    QgsProcessingUtils,
    Qgis, # Keep for message levels (Qgis.Info, Qgis.Warning etc)
    QgsUnitTypes, # For CRS unit checking
    QgsCoordinateTransformContext # Added for writer
)
from qgis.gui import QgsMessageBar
from qgis.utils import iface

# PyQt Imports
from qgis.PyQt.QtWidgets import QWidget, QDialogButtonBox, QFileDialog, QApplication
from qgis.PyQt.QtCore import pyqtSignal, QSettings, QVariant, Qt # <-- Added Qt import

# Plugin Imports
from GeoPublicHealth.src.core.blurring.layer_index import LayerIndex
from GeoPublicHealth.src.core.blurring.blur import Blur
from GeoPublicHealth.src.core.tools import (
    get_last_input_path, set_last_input_path, tr, display_message_bar
)
from GeoPublicHealth.src.core.exceptions import (
    GeoPublicHealthException,
    NoLayerProvidedException,
    NoFileNoDisplayException,
    DifferentCrsException,
    CreatingShapeFileException,
    PointOutsideEnvelopeException # Added for specific exception handling
)
from GeoPublicHealth.src.utilities.resources import get_ui_class

# Load the UI class from the .ui file
FORM_CLASS = get_ui_class('analysis', 'blur.ui')


class BlurWidget(QWidget, FORM_CLASS):
    """
    Widget for the Blurring tool GUI. Handles user input and triggers the
    blurring process outside of the Processing framework.
    """

    signalAskCloseWindow = pyqtSignal(name='signalAskCloseWindow')

    def __init__(self, parent=None):
        self.parent = parent
        super(BlurWidget, self).__init__(parent) # Pass parent to superclass
        self.setupUi(self)

        self.label_progress.setText('')
        self.checkBox_envelope.setChecked(False)
        self.comboBox_envelope.setEnabled(False) # Keep disabled until checkbox checked

        # Connect signals to slots
        self.pushButton_browseFolder.clicked.connect(self.select_file)
        self.buttonBox_blur.button(QDialogButtonBox.Ok).clicked.connect(self.run_blur)
        self.buttonBox_blur.button(QDialogButtonBox.Cancel).clicked.connect(self.signalAskCloseWindow.emit) # Emit signal directly
        self.checkBox_envelope.toggled.connect(self.comboBox_envelope.setEnabled) # Enable/disable combo box

        self.settings = QSettings()

        # Set filters for combo boxes
        self.comboBox_layerToBlur.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.comboBox_envelope.setFilters(QgsMapLayerProxyModel.PolygonLayer)

    def select_file(self):
        """Opens a file dialog to select the output shapefile."""
        last_folder = get_last_input_path()
        output_file, _ = QFileDialog.getSaveFileName(
            self, # Parent should be self (the widget)
            tr('Select Output Shapefile'),
            last_folder, # Start in the last used directory
            tr('ESRI Shapefiles (*.shp)') # Filter for shapefiles, translated
        )

        if output_file:
            self.lineEdit_outputFile.setText(output_file)
            set_last_input_path(dirname(output_file))
        else:
            self.lineEdit_outputFile.setText('')

    def run_blur(self):
        """Executes the blurring logic when the OK button is clicked."""
        self.progressBar_blur.setValue(0)
        self.label_progress.setText(tr('Starting...')) # Initial message
        QApplication.processEvents() # Show initial message
        QApplication.setOverrideCursor(Qt.WaitCursor) # <-- Use imported Qt here

        # --- Get Parameters from UI ---
        layer_to_blur = self.comboBox_layerToBlur.currentLayer()
        radius = self.spinBox_radius.value()
        display_result = self.checkBox_addToMap.isChecked()
        selected_features_only = self.checkBox_selectedOnlyFeatures.isChecked()
        file_name = self.lineEdit_outputFile.text()
        export_radius = self