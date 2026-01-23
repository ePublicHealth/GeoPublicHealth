# -*- coding: utf-8 -*-
"""
/***************************************************************************

                                 GeoPublicHealth
                                 A QGIS plugin

                              -------------------
        begin                : 2026-01-22
        copyright            : (C) 2026 by Manuel Vidaurre
        email                : manuel.vidaurre@gmail.com
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

"""
Optional dependencies handler for GeoPublicHealth plugin.

This module provides lazy loading and graceful fallback for optional
dependencies like matplotlib that are not strictly required for basic
plugin functionality.
"""

# Check for matplotlib availability
try:
    import matplotlib
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import (
        NavigationToolbar2QT as NavigationToolbar,
    )

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    Figure = None
    FigureCanvas = None
    NavigationToolbar = None


def require_matplotlib(feature_name="This feature"):
    """
    Decorator to check if matplotlib is available before running a function.

    :param feature_name: Name of the feature requiring matplotlib
    :return: Decorator function
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            if not MATPLOTLIB_AVAILABLE:
                from geopublichealth.src.core.tools import display_message_bar, tr
                from qgis.core import Qgis

                message = tr(
                    f"{feature_name} requires matplotlib. "
                    f"Please install matplotlib in your QGIS Python environment."
                )
                display_message_bar(message, Qgis.Warning, duration=10)
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def check_matplotlib():
    """
    Check if matplotlib is available and return status message.

    :return: Tuple of (is_available: bool, message: str)
    """
    if MATPLOTLIB_AVAILABLE:
        return True, "matplotlib is available"
    else:
        return False, (
            "matplotlib is not installed. "
            "Graphing and plotting features will be disabled. "
            "To enable these features, please install matplotlib in your QGIS Python environment."
        )
