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

# Plugin Imports
from GeoPublicHealth.src.gui.analysis.parent_incidence_density_dialog import (
    IncidenceDensityDialog)
from GeoPublicHealth.src.utilities.resources import get_ui_class

# Load UI from .ui file
FORM_CLASS = get_ui_class('analysis', 'incidence.ui')


class IncidenceDialog(IncidenceDensityDialog, FORM_CLASS):
    """
    Dialog for calculating Incidence Rates using a field from a polygon layer.
    Inherits common functionality from IncidenceDensityDialog.
    """
    def __init__(self, parent=None):
        """Constructor."""
        # Call parent __init__ FIRST
        IncidenceDensityDialog.__init__(self, parent)

        # Set specific flags for this dialog mode BEFORE setup_ui
        self.use_area = False        # We use population, not area
        self.use_point_layer = False # We use fields, not a point layer

        # Setup the UI defined in FORM_CLASS (loads widgets from incidence.ui)
        # Make sure 'incidence.ui' exists and is valid
        try:
             FORM_CLASS.setupUi(self, self)
        except Exception as e:
             print(f"Error setting up UI for IncidenceDialog: {e}")
             # Optionally display a message to the user or raise
             # This might happen if incidence.ui is missing or corrupt

        # Call parent's setup_ui AFTER subclass UI is loaded and flags are set
        # This connects signals and configures common widgets
        self.setup_ui()

    # The run_stats method has been removed as the logic is handled
    # by the parent class's start_stats_task and the IncidenceDensityTask