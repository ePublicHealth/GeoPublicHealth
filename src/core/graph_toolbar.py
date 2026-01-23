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

from geopublichealth.src.core.optional_deps import (
    MATPLOTLIB_AVAILABLE,
    NavigationToolbar,
)


class CustomNavigationToolbar(NavigationToolbar if MATPLOTLIB_AVAILABLE else object):
    """Custom navigation toolbar for matplotlib plots."""

    def __init__(self, *args, **kwargs):
        if not MATPLOTLIB_AVAILABLE:
            super().__init__()
            return
        super().__init__(*args, **kwargs)

    if MATPLOTLIB_AVAILABLE and NavigationToolbar is not None:
        toolitems = [
            t
            for t in NavigationToolbar.toolitems
            if t[0] in ("Home", "Back", "Next", "Pan", "Zoom", "Save")
        ]
