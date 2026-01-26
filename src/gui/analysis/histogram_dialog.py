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

from __future__ import print_function

from builtins import str
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox
from qgis.PyQt.QtCore import QSize, pyqtSignal

from geopublichealth.src.core.optional_deps import (
    MATPLOTLIB_AVAILABLE,
    Figure,
    FigureCanvas,
)
from geopublichealth.src.core.graph_toolbar import CustomNavigationToolbar
from geopublichealth.src.core.services import histogram as histogram_service
from geopublichealth.src.utilities.resources import get_ui_class

FORM_CLASS = get_ui_class("analysis", "histogram.ui")


class HistogramDialog(QDialog, FORM_CLASS):
    signalAskCloseWindow = pyqtSignal(int, name="signalAskCloseWindow")

    def __init__(self, parent=None):
        """Constructor."""
        QDialog.__init__(self, parent)
        self.setupUi(self)

        # Connect slot.
        self.button_box.button(QDialogButtonBox.Ok).clicked.connect(self.draw_plot)
        self.button_box.button(QDialogButtonBox.Cancel).clicked.connect(self.hide)
        self.button_box.button(QDialogButtonBox.Cancel).clicked.connect(
            self.signalAskCloseWindow.emit
        )

        # Setup the graph.
        if MATPLOTLIB_AVAILABLE:
            self.figure = Figure()
            self.ax = self.figure.add_subplot(1, 1, 1)
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setMinimumSize(QSize(300, 0))
            self.toolbar = CustomNavigationToolbar(self.canvas, self)
            self.layout_plot.addWidget(self.toolbar)
            self.layout_plot.addWidget(self.canvas)
        else:
            self.figure = None
            self.ax = None
            self.canvas = None
            self.toolbar = None

    def draw_plot(self):
        """Function to draw the plot and display it in the canvas."""

        index = self.cbx_layer.currentIndex()
        layer = self.cbx_layer.itemData(index)
        if not layer or not self.ax:
            return
        render = layer.rendererV2()
        ranges = histogram_service.renderer_ranges(render)
        if not ranges:
            return

        self.ax.clear()
        positions = list(range(1, len(ranges) + 1))
        heights = [upper - lower for lower, upper, __, ___ in ranges]
        bar_list = self.ax.bar(positions, heights)

        for bar, (_, __, ___, symbol) in zip(bar_list, ranges):
            if symbol is not None:
                color = symbol.color()
                bar.set_color(color.name())

        self.canvas.draw()
