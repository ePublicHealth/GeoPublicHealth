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

from PyQt4.QtGui import QDialog, QTreeWidgetItem, QTabWidget, QIcon
from PyQt4.QtCore import QSize

from GeoPublicHealth.doc.help import *
from GeoPublicHealth.ui.main import Ui_Dialog
from GeoPublicHealth.gui.import_gui.open_shapefile import OpenShapefileWidget
from GeoPublicHealth.gui.import_gui.open_csv import OpenCsv
from GeoPublicHealth.gui.import_gui.raster import OpenRasterWidget
from GeoPublicHealth.gui.import_gui.open_xls_dbf import OpenXlsDbfFileWidget
from GeoPublicHealth.gui.analysis.blur_dialog import BlurWidget
from GeoPublicHealth.gui.analysis.stats_dialog import StatsWidget
from GeoPublicHealth.gui.analysis.composite_index_dialog import CompositeIndexDialog
from GeoPublicHealth.gui.analysis.incidence_dialog import IncidenceDialog
from GeoPublicHealth.gui.analysis.incidence_point_dialog import IncidencePointDialog
from GeoPublicHealth.gui.analysis.density_dialog import DensityDialog
from GeoPublicHealth.gui.analysis.density_point_dialog import DensityPointDialog
from GeoPublicHealth.gui.analysis.autocorrelation_dialog import AutocorrelationDialog
from GeoPublicHealth.gui.export.csv import CsvExport
from GeoPublicHealth.gui.about import AboutWidget


class MainDialog(QDialog, Ui_Dialog):

    def __init__(self, parent=None):
        """Constructor."""
        QDialog.__init__(self)
        self.parent = parent
        self.setupUi(self)

        # noinspection PyUnresolvedReferences
        self.menu.clicked.connect(self.expand)
        # noinspection PyUnresolvedReferences
        self.menu.clicked.connect(self.display_content)

        self.tree_menu = [
            {
                'label': 'Import',
                'icon': ':/plugins/GeoPublicHealth/resources/import.png',
                'content': [
                    {
                        'label': 'Shapefile',
                        'icon': ':/plugins/GeoPublicHealth/resources/shp.png',
                        'content': {
                            'widget': OpenShapefileWidget(),
                            'help': help_open_shapefile()
                        }
                    }, {
                        'label': 'Raster',
                        'icon': ':/plugins/GeoPublicHealth/resources/raster.png',
                        'content': {
                            'widget': OpenRasterWidget(),
                            'help': help_open_raster()
                        }
                    }, {
                        'label': 'Table XLS/DBF',
                        'icon': ':/plugins/GeoPublicHealth/resources/xls.png',
                        'content': {
                            'widget': OpenXlsDbfFileWidget(),
                            'help': help_open_table()
                        }
                    }, {
                        'label': 'Table CSV',
                        'icon': ':/plugins/GeoPublicHealth/resources/csv.png',
                        'content': {
                            'widget': OpenCsv(),
                            'help': help_open_csv()
                        }
                    }, {
                        'label': 'XY to map',
                        'icon': ':/plugins/GeoPublicHealth/resources/xy.png',
                        'content': {
                            'widget': OpenCsv(),
                            'help': help_open_csv()
                        }
                    }
                ]
            }, {
                'label': 'Analyze',
                'icon': ':/plugins/GeoPublicHealth/resources/gears.png',
                'content': [
                    {
                        'label': 'Composite Index',
                        'icon': ':/plugins/GeoPublicHealth/resources/composite_index.png',
                        'content': [
                            {
                                'label': 'Polygon layer only',
                                'icon': ':/plugins/GeoPublicHealth/resources/composite_index.png',
                                'content': {
                                    'widget': CompositeIndexDialog(),
                                    'help': help_composite_index()
                                }
                            }
                        ]
                    }, {
                        'label': 'Incidence',
                        'icon': ':/plugins/GeoPublicHealth/resources/incidence.png',
                        'content': [
                            {
                                'label': 'Polygon layer only',
                                'icon': ':/plugins/GeoPublicHealth/resources/incidence.png',
                                'content': {
                                    'widget': IncidenceDialog(),
                                    'help': help_incidence()
                                }
                            }, {
                                'label': 'Case and aggregation layers',
                                'icon': ':/plugins/GeoPublicHealth/resources/incidence.png',
                                'content': {
                                    'widget': IncidencePointDialog(),
                                    'help': help_incidence_point()
                                }
                            }
                        ]
                    }, {
                        'label': 'Density',
                        'icon': ':/plugins/GeoPublicHealth/resources/incidence.png',
                        'content': [
                            {
                                'label': 'Polygon layer only',
                                'icon': ':/plugins/GeoPublicHealth/resources/incidence.png',
                                'content': {
                                    'widget': DensityDialog(),
                                    'help': help_density()
                                }
                            }, {
                                'label': 'Case and aggregation layers',
                                'icon': ':/plugins/GeoPublicHealth/resources/incidence.png',
                                'content': {
                                    'widget': DensityPointDialog(),
                                    'help': help_density_point()
                                }
                            }
                        ]
                    }, {
                        'label': 'Autocorrelation',
                        'icon': ':/plugins/GeoPublicHealth/resources/autocorrelation.png',
                        'content': [
                            {
                                'label': 'Polygon layer only',
                                'icon': ':/plugins/GeoPublicHealth/resources/autocorrelation.png',
                                'content': {
                                    'widget': AutocorrelationDialog(),
                                    'help': help_autocorrelation()
                                }
                            }
                        ]
                    }, {
                        'label': 'Blur',
                        'icon': ':/plugins/GeoPublicHealth/resources/blur.png',
                        'content': [
                            {
                                'label': 'Blur',
                                'icon': ':/plugins/GeoPublicHealth/resources/blur.png',
                                'content': {
                                    'widget': BlurWidget(),
                                    'help': help_blur()
                                }
                            }, {
                                'label': 'Stats',
                                'icon': ':/plugins/GeoPublicHealth/resources/sigma.png',
                                'content': {
                                    'widget': StatsWidget(),
                                    'help': help_stats_blurring()
                                }
                            }
                        ]
                    }, 
                ]
            },
            {
                'label': 'Export',
                'icon': ':/plugins/GeoPublicHealth/resources/export.png',
                'content': [
                    {
                        'label': 'Attribute table',
                        'icon': ':/plugins/GeoPublicHealth/resources/csv.png',
                        'content': {
                            'widget': CsvExport(),
                            'help': help_attribute_table()
                        }
                    }
                ]
            }
        ]

        self.stack.addWidget(AboutWidget())

        self.help_list = []

        # A category is import, process and export.
        for category_def in self.tree_menu:
            category_menu = QTreeWidgetItem(self.menu)
            category_menu.setIcon(0, QIcon(category_def['icon']))
            category_menu.setText(0, category_def['label'])

            # Sub item
            for sub_category_def in category_def['content']:
                menu_entry = QTreeWidgetItem(category_menu)
                menu_entry.setIcon(0, QIcon(sub_category_def['icon']))
                menu_entry.setText(0, sub_category_def['label'])

                # Add widget or add tab
                if isinstance(sub_category_def['content'], dict):
                    widget = sub_category_def['content']['widget']
                    self.stack.addWidget(widget)
                    self.help_list.append(sub_category_def['content']['help'])
                else:
                    tab = QTabWidget(self.stack)
                    tab.setIconSize(QSize(32, 32))
                    self.stack.addWidget(tab)

                    tab_help = []
                    tab_bar = sub_category_def['content']
                    for item in tab_bar:
                        label = item['label']
                        icon = QIcon(item['icon'])
                        widget = item['content']['widget']
                        help_widget = item['content']['help']
                        tab_help.append(help_widget)
                        tab.addTab(widget, icon, label)
                    self.help_list.append(tab_help)

        self.stack.setCurrentIndex(1)

    def display_help_tab(self, tab_index):
        index = self.stack.currentIndex() - 2
        content = self.help_list[index]
        self.help.setHtml(content[tab_index])

    def show_status(self, level, message):
        self.messageBar.pushMessage('', message, level, 5)

    def expand(self, i):
        """Auto expand item on single click."""
        self.menu.setExpanded(i, not self.menu.isExpanded(i))

    def _fetch_widget_index(self, parent_item, current_item):
        if parent_item.row() == -1:
            return None

        row = 0
        for i in range(0, parent_item.row()):
            cat = self.menu.topLevelItem(i)
            count_in_category = cat.childCount()
            row += count_in_category

        row += current_item.row()

        return row

    def display_content(self):
        """Return the row number"""
        current_item = self.menu.currentIndex()
        parent = current_item.parent()

        index = self._fetch_widget_index(parent, current_item)

        if index is None:
            self.stack.setCurrentIndex(1)
        else:
            # Index start from FIXME
            self.stack.setCurrentIndex(index + 2)
            current_widget = self.stack.currentWidget()
            if isinstance(current_widget, QTabWidget):
                current_widget.setCurrentIndex(0)
                # noinspection PyUnresolvedReferences
                current_widget.currentChanged.connect(self.display_help_tab)
            else:
                try:
                    current_widget.currentChanged.disconnect(self.display_help_tab)
                except AttributeError:
                    pass

        # Set th help
        try:
            if index is None:
                raise IndexError
            content = self.help_list[index]
            if isinstance(content, list):
                self.help.setHtml(content[0])
            else:
                self.help.setHtml(content)
            self.help.show()
        except IndexError:
            self.help.hide()