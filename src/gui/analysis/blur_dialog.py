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
import traceback  # For debugging unexpected errors

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
    Qgis,  # Keep for message levels (Qgis.Info, Qgis.Warning etc)
    QgsUnitTypes,  # For CRS unit checking
    QgsCoordinateTransformContext,  # Added for writer
)
from qgis.gui import QgsMessageBar
from qgis.utils import iface

# PyQt Imports
from qgis.PyQt.QtWidgets import QWidget, QDialogButtonBox, QApplication
from qgis.PyQt.QtCore import pyqtSignal, QSettings, QVariant, Qt  # <-- Added Qt import

# Plugin Imports
from geopublichealth.src.core.blurring.layer_index import LayerIndex
from geopublichealth.src.core.blurring.blur import Blur
from geopublichealth.src.core.tools import (
    display_message_bar,
    get_last_input_path,
    get_save_file_path,
    set_last_input_path,
    tr,
)
from geopublichealth.src.core.exceptions import (
    GeoPublicHealthException,
    NoLayerProvidedException,
    NoFileNoDisplayException,
    DifferentCrsException,
    CreatingShapeFileException,
    PointOutsideEnvelopeException,  # Added for specific exception handling
)
from geopublichealth.src.utilities.resources import get_ui_class

# Load the UI class from the .ui file
FORM_CLASS = get_ui_class("analysis", "blur.ui")


class BlurWidget(QWidget, FORM_CLASS):
    """
    Widget for the Blurring tool GUI. Handles user input and triggers the
    blurring process outside of the Processing framework.
    """

    signalAskCloseWindow = pyqtSignal(name="signalAskCloseWindow")

    def __init__(self, parent=None):
        self.parent = parent
        super(BlurWidget, self).__init__(parent)  # Pass parent to superclass
        self.setupUi(self)

        self.label_progress.setText("")
        self.checkBox_envelope.setChecked(False)
        self.comboBox_envelope.setEnabled(False)  # Keep disabled until checkbox checked

        # Connect signals to slots
        self.pushButton_browseFolder.clicked.connect(self.select_file)
        self.buttonBox_blur.button(QDialogButtonBox.Ok).clicked.connect(self.run_blur)
        self.buttonBox_blur.button(QDialogButtonBox.Cancel).clicked.connect(
            self.signalAskCloseWindow.emit
        )  # Emit signal directly
        self.checkBox_envelope.toggled.connect(
            self.comboBox_envelope.setEnabled
        )  # Enable/disable combo box

        self.settings = QSettings()

        # Set filters for combo boxes
        self.comboBox_layerToBlur.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.comboBox_envelope.setFilters(QgsMapLayerProxyModel.PolygonLayer)

    def select_file(self):
        """Opens a file dialog to select the output shapefile."""
        last_folder = get_last_input_path()
        output_file, _ = get_save_file_path(
            self,  # Parent should be self (the widget)
            tr("Select Output Shapefile"),
            last_folder,  # Start in the last used directory
            tr("ESRI Shapefiles (*.shp)"),  # Filter for shapefiles, translated
            prompt=tr("Output file path (.shp):"),
        )

        if output_file:
            self.lineEdit_outputFile.setText(output_file)
            set_last_input_path(dirname(output_file))
        else:
            self.lineEdit_outputFile.setText("")

    def run_blur(self):
        """Executes the blurring logic when the OK button is clicked."""
        self.progressBar_blur.setValue(0)
        self.label_progress.setText(tr("Starting..."))  # Initial message
        QApplication.processEvents()  # Show initial message
        QApplication.setOverrideCursor(Qt.WaitCursor)  # <-- Use imported Qt here

        # --- Get Parameters from UI ---
        layer_to_blur = self.comboBox_layerToBlur.currentLayer()
        radius = self.spinBox_radius.value()
        display_result = self.checkBox_addToMap.isChecked()
        selected_features_only = self.checkBox_selectedOnlyFeatures.isChecked()
        file_name = self.lineEdit_outputFile.text().strip()
        export_radius = self.checkBox_exportRadius.isChecked()
        export_centroid = self.checkBox_exportCentroid.isChecked()
        use_envelope = self.checkBox_envelope.isChecked()

        try:
            if not layer_to_blur:
                raise NoLayerProvidedException

            envelope_layer = None
            envelope_index = None
            if use_envelope:
                envelope_layer = self.comboBox_envelope.currentLayer()
                if not envelope_layer:
                    raise NoLayerProvidedException

                if layer_to_blur.crs() != envelope_layer.crs():
                    raise DifferentCrsException(
                        epsg1=layer_to_blur.crs().authid(),
                        epsg2=envelope_layer.crs().authid(),
                    )

                envelope_index = LayerIndex(envelope_layer)

            if not file_name and not display_result:
                raise NoFileNoDisplayException

            if not file_name:
                file_name = QgsProcessingUtils.generateTempFilename(
                    "geopublichealth_blur.shp"
                )
                self.lineEdit_outputFile.setText(file_name)
            elif not file_name.lower().endswith(".shp"):
                file_name = file_name + ".shp"
                self.lineEdit_outputFile.setText(file_name)

            set_last_input_path(dirname(file_name))

            if selected_features_only:
                features = layer_to_blur.selectedFeatures()
            else:
                features = list(layer_to_blur.getFeatures())

            if not features:
                raise GeoPublicHealthException(tr("No features to blur."))

            out_fields = QgsFields()
            out_fields.extend(layer_to_blur.fields())

            if export_radius:
                out_fields.append(QgsField("Radius", QVariant.Double))
            if export_centroid:
                out_fields.append(QgsField("X_centroid", QVariant.Double))
                out_fields.append(QgsField("Y_centroid", QVariant.Double))

            save_options = QgsVectorFileWriter.SaveVectorOptions()
            save_options.driverName = "ESRI Shapefile"
            save_options.fileEncoding = "UTF-8"

            writer = QgsVectorFileWriter.create(
                file_name,
                out_fields,
                QgsWkbTypes.Polygon,
                layer_to_blur.crs(),
                QgsCoordinateTransformContext(),
                save_options,
            )

            if writer.hasError():
                raise CreatingShapeFileException(suffix=f": {writer.errorMessage()}")

            algo = Blur(
                radius,
                envelope_index,
                export_radius,
                export_centroid,
            )

            total = len(features)
            for i, feature in enumerate(features):
                try:
                    blurred_feature = algo.blur(feature)
                    writer.addFeature(blurred_feature)
                except PointOutsideEnvelopeException as exc:
                    display_message_bar(
                        msg=exc.msg, level=exc.level, duration=exc.duration
                    )

                percent = int((i + 1) * 100 / total)
                self.progressBar_blur.setValue(percent)
                QApplication.processEvents()

            del writer

            if display_result:
                output_layer = QgsVectorLayer(file_name, basename(file_name), "ogr")
                if output_layer.isValid():
                    QgsProject.instance().addMapLayer(output_layer)
                else:
                    display_message_bar(
                        msg=tr("Output layer is invalid."),
                        level=Qgis.Warning,
                    )

            self.label_progress.setText(tr("Finished"))
            self.progressBar_blur.setValue(100)

        except GeoPublicHealthException as e:
            display_message_bar(msg=e.msg, level=e.level, duration=e.duration)
            traceback.print_exc()
        except Exception as e:
            display_message_bar(
                msg=f"{tr('Unexpected error:')} {str(e)}",
                level=Qgis.Critical,
            )
            traceback.print_exc()
        finally:
            QApplication.restoreOverrideCursor()
