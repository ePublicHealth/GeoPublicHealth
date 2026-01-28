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

from builtins import object
from os.path import dirname, join, exists

from qgis.core import (
    QgsApplication,
    QgsMessageLog,
    QgsProcessingProvider,
    QgsProcessingRegistry,
    Qgis,
)
from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
# from processing.core.Processing import Processing

from geopublichealth.src.gui.main_window import MainDialog
from geopublichealth.src.processing_geopublichealth.provider import Provider
from geopublichealth.src.utilities.resources import resource


class GeoPublicHealthPlugin(object):
    def __init__(self, iface):
        self.provider = None
        self.iface = iface
        self.plugin_dir = dirname(__file__)
        self._ensure_proj_data_dir()
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        locale_path = join(
            self.plugin_dir, "i18n", "GeoPublicHealth_{}.qm".format(locale)
        )

        if exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > "4.3.3":
                # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
                QCoreApplication.installTranslator(self.translator)

        self.plugin_menu = None
        self.geopublichealth_menu = None
        self.main_action = None
        self.xy_action = None
        self.blur_action = None
        self.incidence_action = None
        self.density_action = None
        self.histogram_action = None

    @staticmethod
    def _ensure_proj_data_dir():
        try:
            from pyproj import datadir
        except ImportError:
            return

        try:
            current_dir = datadir.get_data_dir()
        except Exception:
            current_dir = None

        if current_dir and exists(current_dir):
            return

        prefix_path = QgsApplication.prefixPath()
        candidate_paths = [
            join(prefix_path, "Resources", "proj"),
            join(dirname(prefix_path), "Resources", "proj"),
            join(prefix_path, "share", "proj"),
            join(dirname(prefix_path), "share", "proj"),
        ]

        for candidate in candidate_paths:
            if exists(candidate):
                datadir.set_data_dir(candidate)
                QgsMessageLog.logMessage(
                    f"Set PROJ data directory to {candidate}",
                    "GeoPublicHealth",
                    Qgis.Info,
                )
                return

    def initProcessing(self):
        try:
            self.provider = Provider()
            QgsApplication.processingRegistry().addProvider(self.provider)
        except Exception as exc:
            QgsMessageLog.logMessage(
                f"Processing provider failed to load: {exc}",
                "GeoPublicHealth",
                Qgis.Warning,
            )

    def initGui(self):
        self.initProcessing()
        self.plugin_menu = None
        if self.iface:
            try:
                self.plugin_menu = self.iface.pluginMenu()
            except Exception:
                self.plugin_menu = None

        # Main window
        icon = QIcon(resource("icon-32.png"))
        parent = self.iface.mainWindow() if self.iface else None
        self.main_action = QAction(icon, "GeoPublicHealth", parent)
        if self.plugin_menu:
            try:
                self.plugin_menu.addAction(self.main_action)
            except Exception as exc:
                QgsMessageLog.logMessage(
                    f"Failed to add action to plugin menu: {exc}",
                    "GeoPublicHealth",
                    Qgis.Warning,
                )
        # noinspection PyUnresolvedReferences
        self.main_action.triggered.connect(self.open_main_window)
        if self.iface:
            try:
                self.iface.addPluginToMenu("GeoPublicHealth", self.main_action)
            except Exception as exc:
                QgsMessageLog.logMessage(
                    f"Failed to add action to QGIS menu: {exc}",
                    "GeoPublicHealth",
                    Qgis.Warning,
                )

    def unload(self):
        if self.plugin_menu and self.main_action:
            try:
                self.plugin_menu.removeAction(self.main_action)
            except Exception:
                pass
        if self.iface and self.main_action:
            try:
                self.iface.removePluginMenu("GeoPublicHealth", self.main_action)
            except Exception:
                pass
        if self.provider:
            try:
                QgsApplication.processingRegistry().removeProvider(self.provider)
            except Exception:
                pass

    @staticmethod
    def open_main_window():
        dialog = MainDialog()
        dialog.show()
        dialog.exec_()
