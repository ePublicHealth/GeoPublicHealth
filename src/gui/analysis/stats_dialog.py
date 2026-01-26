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
from builtins import range
from os.path import dirname
from qgis.core import Qgis, QgsMapLayerProxyModel

from qgis.PyQt.QtWidgets import (
    QWidget,
    QDialogButtonBox,
    QApplication,
    QTableWidgetItem,
)
from qgis.PyQt.QtCore import pyqtSignal, QSize

from geopublichealth.src.core.optional_deps import (
    MATPLOTLIB_AVAILABLE,
    Figure,
    FigureCanvas,
)
from geopublichealth.src.core.graph_toolbar import CustomNavigationToolbar
from geopublichealth.src.core.services import spatial_stats
from geopublichealth.src.core.tools import (
    tr,
    display_message_bar,
    get_save_file_path,
    get_last_input_path,
    set_last_input_path,
)
from geopublichealth.src.core.exceptions import (
    GeoPublicHealthException,
    NoLayerProvidedException,
    DifferentCrsException,
)
from geopublichealth.src.utilities.resources import get_ui_class

FORM_CLASS = get_ui_class("analysis", "stats.ui")


class StatsWidget(QWidget, FORM_CLASS):
    signalAskCloseWindow = pyqtSignal(name="signalAskCloseWindow")

    def __init__(self, parent=None):
        self.parent = parent
        super(StatsWidget, self).__init__()
        self.setupUi(self)

        self.label_progressStats.setText("")

        # Connect
        # noinspection PyUnresolvedReferences
        self.pushButton_saveTable.clicked.connect(self.save_table)
        # noinspection PyUnresolvedReferences
        self.pushButton_saveYValues.clicked.connect(self.save_y_values)
        self.buttonBox_stats.button(QDialogButtonBox.Ok).clicked.connect(self.run_stats)
        self.buttonBox_stats.button(QDialogButtonBox.Cancel).clicked.connect(
            self.signalAskCloseWindow.emit
        )

        # a figure instance to plot on
        if MATPLOTLIB_AVAILABLE:
            self.figure = Figure()
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setMinimumSize(QSize(300, 0))
            self.toolbar = CustomNavigationToolbar(self.canvas, self)
            self.layout_plot.addWidget(self.toolbar)
            self.layout_plot.addWidget(self.canvas)
        else:
            self.figure = None
            self.canvas = None
            self.toolbar = None
            # Show warning message about missing matplotlib
            display_message_bar(
                msg=tr(
                    "matplotlib is not available. Graphing features will be disabled."
                ),
                level=Qgis.Warning,
                duration=5,
            )

        self.tab = []

        self.comboBox_blurredLayer.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.comboBox_statsLayer.setFilters(QgsMapLayerProxyModel.PolygonLayer)

    def run_stats(self):
        self.progressBar_stats.setValue(0)
        self.label_progressStats.setText("")
        # noinspection PyArgumentList
        QApplication.processEvents()

        blurred_layer = self.comboBox_blurredLayer.currentLayer()
        stats_layer = self.comboBox_statsLayer.currentLayer()

        try:
            if not blurred_layer or not stats_layer:
                raise NoLayerProvidedException

            crs_blurred_layer = blurred_layer.crs()
            crs_stats_layer = stats_layer.crs()

            if crs_blurred_layer != crs_stats_layer:
                raise DifferentCrsException(
                    epsg1=crs_blurred_layer.authid(), epsg2=crs_stats_layer.authid()
                )

            if blurred_layer == stats_layer:
                raise NoLayerProvidedException

            if not blurred_layer or not stats_layer:
                raise NoLayerProvidedException

            nb_feature_stats = stats_layer.featureCount()
            nb_feature_blurred = blurred_layer.featureCount()
            label_creating = tr("Creating index on the stats layer")
            label_calculating = tr("Calculating")

            if Qgis.QGIS_VERSION_INT < 20700:
                self.label_progressStats.setText("%s 1/2" % label_creating)

                def index_progress(current, total):
                    percent = int(current * 100 / total)
                    self.progressBar_stats.setValue(percent)
                    QApplication.processEvents()

                index = spatial_stats.build_spatial_index(
                    stats_layer,
                    progress_callback=index_progress,
                    use_fast=False,
                )
                self.label_progressStats.setText("%s 2/2" % label_calculating)
            else:
                self.label_progressStats.setText("%s 1/2" % label_creating)
                QApplication.processEvents()
                index = spatial_stats.build_spatial_index(
                    stats_layer,
                    use_fast=True,
                )
                self.label_progressStats.setText("%s 2/2" % label_calculating)

            QApplication.processEvents()

            def calc_progress(current, total):
                percent = int(current * 100 / total)
                self.progressBar_stats.setValue(percent)
                QApplication.processEvents()

            self.tab = spatial_stats.compute_intersection_counts(
                blurred_layer,
                stats_layer,
                index,
                progress_callback=calc_progress,
            )

            items_stats = spatial_stats.build_stats_items(
                self.tab,
                nb_feature_blurred,
                nb_feature_stats,
            )

            self.tableWidget.clear()
            self.tableWidget.setColumnCount(2)
            labels = ["Parameters", "Values"]
            self.tableWidget.setHorizontalHeaderLabels(labels)
            self.tableWidget.setRowCount(len(items_stats))

            for i, (label, value) in enumerate(items_stats):
                self.tableWidget.setItem(i, 0, QTableWidgetItem(label))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(value))
            self.tableWidget.resizeRowsToContents()

            self.draw_plot(self.tab)

        except GeoPublicHealthException as e:
            self.label_progressStats.setText("")
            display_message_bar(msg=e.msg, level=e.level, duration=e.duration)

    def save_table(self):
        if not self.tableWidget.rowCount():
            return False

        csv_string = "parameter,values\n"

        for i in range(self.tableWidget.rowCount()):
            item_param = self.tableWidget.item(i, 0)
            item_value = self.tableWidget.item(i, 1)
            csv_string += str(item_param.text()) + "," + item_value.text() + "\n"

        last_directory = get_last_input_path()

        # noinspection PyArgumentList
        output_file, __ = get_save_file_path(
            parent=self,
            title=tr("Select file"),
            directory=last_directory,
            file_filter="CSV (*.csv)",
            prompt=tr("Output file path (.csv):"),
        )

        if output_file:
            path = dirname(output_file)
            set_last_input_path(path)

            fh = open(output_file, "w")
            fh.write(csv_string)
            fh.close()
            return True

    def save_y_values(self):
        if not self.tableWidget.rowCount():
            return False

        csv_string = "parameter,values\n"

        for value in self.tab:
            csv_string += str(value) + "\n"

        last_directory = get_last_input_path()
        # noinspection PyArgumentList
        output_file, __ = get_save_file_path(
            parent=self,
            title=tr("Select file"),
            directory=last_directory,
            file_filter="CSV (*.csv)",
            prompt=tr("Output file path (.csv):"),
        )

        if output_file:
            path = dirname(output_file)
            set_last_input_path(path)

            fh = open(output_file, "w")
            fh.write(csv_string)
            fh.close()
            return True

    def draw_plot(self, data):
        # Creating the plot
        # create an axis
        ax = self.figure.add_subplot(111)
        # discards the old graph

        # plot data
        ax.plot(data, "*-")

        # ax.set_title('Number of intersections per entity')
        ax.set_xlabel("Blurred entity")
        ax.set_ylabel("Number of intersections")
        ax.grid()

        # refresh canvas
        self.canvas.draw()
