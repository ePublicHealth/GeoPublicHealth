# -*- coding: utf-8 -*-
"""
/***************************************************************************

                                 GeoPublicHealth
                                 A QGIS plugin

                              -------------------
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

from builtins import str
import sys
from uuid import uuid4

from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QApplication, QFileDialog, QInputDialog
from qgis.utils import iface
from qgis.gui import QgsMessageBar
from qgis.core import (
    QgsVectorLayer,
    Qgis,
    QgsGeometry,
    QgsFeature,
    QgsSpatialIndex,
    QgsWkbTypes,
)


def create_memory_layer(
    layer_name, geometry, coordinate_reference_system=None, fields=None
):
    """Create a vector memory layer.

    :param layer_name: The name of the layer.
    :type layer_name: str

    :param geometry: The geometry of the layer.
    :rtype geometry: Qgis.WkbType

    :param coordinate_reference_system: The CRS of the memory layer.
    :type coordinate_reference_system: QgsCoordinateReferenceSystem

    :param fields: Fields of the vector layer. Default to None.
    :type fields: QgsFields

    :return: The memory layer.
    :rtype: QgsVectorLayer
    """

    if geometry == QgsWkbTypes.Point:
        type_string = "MultiPoint"
    elif geometry == QgsWkbTypes.Line:
        type_string = "MultiLineString"
    elif geometry == QgsWkbTypes.Polygon:
        type_string = "MultiPolygon"
    elif geometry == QgsWkbTypes.NoGeometry:
        type_string = "none"
    else:
        raise Exception(
            "Layer is whether Point nor Line nor Polygon, I got %s" % geometry
        )

    uri = "%s?index=yes&uuid=%s" % (type_string, str(uuid4()))
    if coordinate_reference_system:
        crs = coordinate_reference_system.authid().lower()
        uri += "&crs=%s" % crs
    memory_layer = QgsVectorLayer(uri, layer_name, "memory")
    memory_layer.keywords = {"inasafe_fields": {}}

    if fields:
        data_provider = memory_layer.dataProvider()
        data_provider.addAttributes(fields)
        memory_layer.updateFields()

    return memory_layer


def copy_layer(source, target):
    """Copy a vector layer to another one.

    :param source: The vector layer to copy.
    :type source: QgsVectorLayer

    :param target: The destination.
    :type source: QgsVectorLayer
    """
    out_feature = QgsFeature()
    target.startEditing()

    for feature in source.getFeatures():
        geom = feature.geometry()
        out_feature.setGeometry(QgsGeometry(geom))
        out_feature.setAttributes(feature.attributes())
        target.addFeature(out_feature)
    target.commitChanges()


def remove_fields(layer, fields_to_remove):
    """Remove fields from a vector layer.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :param fields_to_remove: List of fields to remove.
    :type fields_to_remove: list
    """
    index_to_remove = []
    data_provider = layer.dataProvider()

    for field in fields_to_remove:
        index = layer.fields().indexFromName(field)
        if index != -1:
            index_to_remove.append(index)

    data_provider.deleteAttributes(index_to_remove)
    layer.updateFields()


def create_spatial_index(layer):
    """Helper function to create the spatial index on a vector layer.

    This function is mainly used to see the processing time with the decorator.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :return: The index.
    :rtype: QgsSpatialIndex
    """
    spatial_index = QgsSpatialIndex(layer.getFeatures())
    return spatial_index


def get_last_input_path():
    settings = QSettings()
    return settings.value("LastInputPath")


def set_last_input_path(directory):
    settings = QSettings()
    settings.setValue("LastInputPath", str(directory))


def tr(msg):
    # noinspection PyCallByClass,PyArgumentList
    return QApplication.translate("GeoPublicHealth", msg)


def get_save_file_path(parent, title, directory, file_filter, prompt=None):
    if sys.platform == "darwin":
        prompt_text = prompt or tr("Output file path:")
        output_file, ok = QInputDialog.getText(
            parent,
            title,
            prompt_text,
            text=directory,
        )
        if not ok:
            return "", ""
        return output_file, ""

    return QFileDialog.getSaveFileName(parent, title, directory, file_filter)


def get_open_file_path(parent, title, directory, file_filter, prompt=None):
    if sys.platform == "darwin":
        prompt_text = prompt or tr("Input file path:")
        input_file, ok = QInputDialog.getText(
            parent,
            title,
            prompt_text,
            text=directory,
        )
        if not ok:
            return "", ""
        return input_file, ""

    return QFileDialog.getOpenFileName(parent, title, directory, file_filter)


def display_message_bar(title=None, msg=None, level=Qgis.Info, duration=5):
    """
    Display a message in QGIS message bar.

    :param title: Message title (optional, can be None)
    :param msg: Message text
    :param level: Message level (Qgis.Info, Qgis.Warning, Qgis.Critical, Qgis.Success)
    :param duration: Duration in seconds to display message (0 for indefinite)
    """
    # Handle the case where only msg is provided (title is used as msg)
    if msg is None and title is not None:
        message = title
        title = ""
    elif msg is not None and title is not None:
        message = f"{title}: {msg}"
    elif msg is not None:
        message = msg
    else:
        message = ""

    try:
        # Check if there's a custom message bar (for dialogs)
        if (
            hasattr(iface, "Blurring_mainWindowDialog")
            and iface.Blurring_mainWindowDialog.isVisible()
        ):
            iface.Blurring_mainWindowDialog.messageBar.pushMessage(
                "", message, level, duration
            )
        else:
            # Use the main QGIS message bar
            # QGIS 3.x API: pushMessage(text, level, duration)
            iface.messageBar().pushMessage(message, level, duration)
    except (AttributeError, TypeError):
        # Fallback to main message bar with just message text
        iface.messageBar().pushMessage(message, level, duration)
