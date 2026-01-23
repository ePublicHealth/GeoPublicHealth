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

from geopublichealth.src.gui.analysis.parent_incidence_density_dialog import \
    IncidenceDensityDialog
from geopublichealth.src.utilities.resources import get_ui_class

FORM_CLASS = get_ui_class('analysis', 'incidence_with_point.ui')


class IncidencePointDialog(IncidenceDensityDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        IncidenceDensityDialog.__init__(self, parent)
        self.use_area = False
        self.use_point_layer = True
        FORM_CLASS.setupUi(self, self)
        self.setup_ui()