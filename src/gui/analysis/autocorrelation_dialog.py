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

import os.path
import warnings
import traceback
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional, Union, Any, Tuple

from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QApplication
from qgis.PyQt.QtCore import QVariant, Qt, pyqtSignal, QSettings
from qgis.PyQt.QtGui import QColor

from qgis.utils import Qgis
from qgis.core import (
    QgsField,
    QgsRendererCategory,
    QgsCategorizedSymbolRenderer,
    QgsGradientColorRamp,
    QgsGraduatedSymbolRenderer,
    QgsSymbol,
    QgsVectorFileWriter,
    QgsFeature,
    QgsVectorLayer,
    QgsProject,
    QgsGeometry,
    QgsMapLayerProxyModel,
    QgsFieldProxyModel,
    QgsWkbTypes,
    QgsApplication,
    QgsClassificationMethod,
    QgsCoordinateTransformContext,
    QgsMessageLog,
)
from qgis.gui import QgsFieldComboBox, QgsMapLayerComboBox

import numpy as np
import pandas as pd


def _ensure_proj_data_dir():
    prefix_path = QgsApplication.prefixPath()
    candidate_paths = [
        os.path.join(prefix_path, "Resources", "proj"),
        os.path.join(os.path.dirname(prefix_path), "Resources", "proj"),
        os.path.join(prefix_path, "share", "proj"),
        os.path.join(os.path.dirname(prefix_path), "share", "proj"),
    ]

    if not (os.environ.get("PROJ_DATA") or os.environ.get("PROJ_LIB")):
        for candidate in candidate_paths:
            if os.path.exists(candidate):
                os.environ["PROJ_DATA"] = candidate
                os.environ["PROJ_LIB"] = candidate
                break

    try:
        from pyproj import datadir
    except ImportError:
        return

    try:
        current_dir = datadir.get_data_dir()
    except Exception:
        current_dir = None

    if current_dir and os.path.exists(current_dir):
        return

    for candidate in candidate_paths:
        if os.path.exists(candidate):
            datadir.set_data_dir(candidate)
            QgsMessageLog.logMessage(
                f"Set PROJ data directory to {candidate}",
                "GeoPublicHealth",
                Qgis.Info,
            )
            return


# Ensure PROJ data is available before importing GeoPandas/libpysal
_ensure_proj_data_dir()

# Import PySAL libraries with fallbacks
try:
    # Filter out specific PySAL deprecation warnings
    warnings.filterwarnings(
        "ignore",
        category=FutureWarning,
        message="Objects based on the `Geometry` class will deprecated",
    )
    warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed file")

    import libpysal
    from libpysal.weights import Queen, Rook
    from esda.moran import (
        Moran,
        Moran_BV,
        Moran_Local,
        Moran_Local_BV,
        Moran_Rate,
        Moran_Local_Rate,
    )
    from esda.getisord import G_Local
    from esda.geary_local import Geary_Local
    from esda.join_counts import Join_Counts
    from esda.join_counts_local import Join_Counts_Local

    # Check if geopandas is available for modern approach
    try:
        import geopandas as gpd

        GEOPANDAS_AVAILABLE = True
    except ImportError:
        GEOPANDAS_AVAILABLE = False

    PYSAL_AVAILABLE = True
except ImportError:
    PYSAL_AVAILABLE = False
    GEOPANDAS_AVAILABLE = False

from geopublichealth.src.core.graph_toolbar import CustomNavigationToolbar
from geopublichealth.src.core.tools import (
    display_message_bar,
    get_save_file_path,
    tr,
)
from geopublichealth.src.core.exceptions import (
    GeoPublicHealthException,
    NoLayerProvidedException,
    FieldExistingException,
    NotANumberException,
)
from geopublichealth.src.core.stats import Stats
from geopublichealth.src.doc.help import help_autocorrelation
from geopublichealth.src.utilities.resources import get_ui_class

FORM_CLASS = get_ui_class("analysis", "autocorrelation.ui")

STAT_MORAN = "moran"
STAT_GEARY = "geary"
STAT_G_LOCAL = "g_local"
STAT_MORAN_RATE = "moran_rate"
STAT_MORAN_GLOBAL = "moran_global"
STAT_MORAN_BV_GLOBAL = "moran_bv_global"
STAT_MORAN_BV_LOCAL = "moran_bv_local"
STAT_JOIN_COUNTS_GLOBAL = "join_counts_global"
STAT_JOIN_COUNTS_LOCAL = "join_counts_local"


class CommonAutocorrelationDialog(QDialog):
    """
    Common dialog class for Autocorrelation analysis.
    """

    signalAskCloseWindow = pyqtSignal(int, name="signalAskCloseWindow")
    signalStatus = pyqtSignal(int, str, name="signalStatus")
    signalHelpChanged = pyqtSignal(str, name="signalHelpChanged")

    def __init__(self, parent=None):
        """
        Constructor for the Autocorrelation dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.parent = parent
        self.name_field = None
        self.admin_layer = None
        self.figure = None
        self.canvas = None
        self.toolbar = None
        self.output_file_path = None
        self.output_layer = None
        self.use_area = None
        self.layer = None

        # Log dependency availability
        QgsMessageLog.logMessage(
            f"PySAL available: {PYSAL_AVAILABLE}, GeoPandas available: {GEOPANDAS_AVAILABLE}",
            "GeoPublicHealth",
            Qgis.Info,
        )

        # Check if PySAL is available
        if not PYSAL_AVAILABLE:
            display_message_bar(
                tr(
                    "PySAL library is required for spatial autocorrelation analysis. "
                    "Please install libpysal and esda packages."
                ),
                level=Qgis.Critical,
                duration=10,
            )

    def setup_ui(self):
        """Set up the UI components."""
        try:
            # Connect signals to slots
            if hasattr(self, "button_browse"):
                self.button_browse.clicked.connect(self.open_file_browser)

            if hasattr(self, "button_box_ok"):
                ok_button = self.button_box_ok.button(QDialogButtonBox.Ok)
                cancel_button = self.button_box_ok.button(QDialogButtonBox.Cancel)

                if ok_button:
                    ok_button.clicked.connect(self.run_stats)
                if cancel_button:
                    cancel_button.clicked.connect(self.hide)
                    cancel_button.clicked.connect(
                        lambda: self.signalAskCloseWindow.emit(0)
                    )

            # Set up layer and field selectors
            if hasattr(self, "cbx_aggregation_layer"):
                self.cbx_aggregation_layer.setFilters(
                    QgsMapLayerProxyModel.PolygonLayer
                )

            if hasattr(self, "cbx_indicator_field") and hasattr(
                self, "cbx_aggregation_layer"
            ):
                self.cbx_indicator_field.setFilters(QgsFieldProxyModel.Numeric)
                self.cbx_indicator_field.setLayer(
                    self.cbx_aggregation_layer.currentLayer()
                )
                self.cbx_aggregation_layer.layerChanged.connect(
                    self.cbx_indicator_field.setLayer
                )

            if hasattr(self, "cbx_population_field") and hasattr(
                self, "cbx_aggregation_layer"
            ):
                self.cbx_population_field.setFilters(QgsFieldProxyModel.Numeric)
                self.cbx_population_field.setLayer(
                    self.cbx_aggregation_layer.currentLayer()
                )
                self.cbx_aggregation_layer.layerChanged.connect(
                    self.cbx_population_field.setLayer
                )

            if hasattr(self, "cbx_secondary_field") and hasattr(
                self, "cbx_aggregation_layer"
            ):
                self.cbx_secondary_field.setFilters(QgsFieldProxyModel.Numeric)
                self.cbx_secondary_field.setLayer(
                    self.cbx_aggregation_layer.currentLayer()
                )
                self.cbx_aggregation_layer.layerChanged.connect(
                    self.cbx_secondary_field.setLayer
                )

            if hasattr(self, "cbx_statistic"):
                self.cbx_statistic.currentIndexChanged.connect(
                    self.update_statistic_controls
                )
                self.cbx_statistic.currentIndexChanged.connect(self.update_help_text)

            if hasattr(self, "cbx_binary_auto"):
                self.cbx_binary_auto.toggled.connect(self.update_statistic_controls)

            # LISA categories with colors and labels
            self.lisa = {
                1: ("#b92815", "High - High"),
                2: ("#3f70df", "Low - High"),
                3: ("#aecbdd", "Low - Low"),
                4: ("#e79e2c", "High - Low"),
            }

            # Display information about available libraries
            if hasattr(self, "label_library_info"):
                if GEOPANDAS_AVAILABLE:
                    self.label_library_info.setText(
                        tr("Using modern GeoPandas approach")
                    )
                elif PYSAL_AVAILABLE:
                    self.label_library_info.setText(tr("Using legacy PySAL approach"))
                else:
                    self.label_library_info.setText(
                        tr("Required libraries not available")
                    )

            self.update_statistic_controls()
            self.update_help_text()
            self.set_summary_text(tr("Summary will appear after running."))

            if hasattr(self, "cbx_aggregation_layer"):
                self.cbx_aggregation_layer.setToolTip(
                    tr("Polygon layer with the indicator field.")
                )
            if hasattr(self, "cbx_indicator_field"):
                self.cbx_indicator_field.setToolTip(
                    tr("Primary numeric field used in the statistic.")
                )
            if hasattr(self, "cbx_population_field"):
                self.cbx_population_field.setToolTip(
                    tr("Population field used for Moran Rate.")
                )
            if hasattr(self, "cbx_secondary_field"):
                self.cbx_secondary_field.setToolTip(
                    tr("Secondary field used for bivariate statistics.")
                )
            if hasattr(self, "cbx_statistic"):
                self.cbx_statistic.setToolTip(
                    tr("Select the autocorrelation statistic to run.")
                )
            if hasattr(self, "cbx_contiguity"):
                self.cbx_contiguity.setToolTip(
                    tr("Define spatial neighbors: Queen or Rook.")
                )
            if hasattr(self, "sbx_binary_threshold"):
                self.sbx_binary_threshold.setToolTip(
                    tr("Threshold for binarizing values for Join Counts.")
                )
            if hasattr(self, "cbx_binary_auto"):
                self.cbx_binary_auto.setToolTip(
                    tr("Auto-detect 0/1 binary fields for Join Counts.")
                )

        except Exception as e:
            display_message_bar(
                f"{tr('Error setting up UI:')} {str(e)}", level=Qgis.Critical
            )
            traceback.print_exc()

    def open_file_browser(self):
        """Method to open file browser and get output file path."""
        if not hasattr(self, "le_output_filepath"):
            return

        # Get the last directory from QSettings if available
        last_dir = QSettings().value("GeoPublicHealth/lastDir", os.path.expanduser("~"))

        output_file, selected_filter = get_save_file_path(
            self.parent,
            tr("Save Output Layer"),
            last_dir,
            tr("ESRI Shapefile (*.shp);;GeoPackage (*.gpkg)"),
            prompt=tr("Output file path (.shp or .gpkg):"),
        )

        if output_file:
            # Apply correct extension based on filter
            is_shp = "(*.shp)" in selected_filter or output_file.lower().endswith(
                ".shp"
            )
            is_gpkg = "(*.gpkg)" in selected_filter or output_file.lower().endswith(
                ".gpkg"
            )
            base, ext = os.path.splitext(output_file)

            if is_shp and not ext.lower() == ".shp":
                output_file = base + ".shp"
            elif is_gpkg and not ext.lower() == ".gpkg":
                output_file = base + ".gpkg"
            elif not ext:  # Default to Shapefile if no extension
                output_file += ".shp"

            self.le_output_filepath.setText(output_file)

            # Save the directory for next time
            QSettings().setValue(
                "GeoPublicHealth/lastDir", os.path.dirname(output_file)
            )

    def run_stats(self):
        """Main analysis function."""
        if not PYSAL_AVAILABLE:
            display_message_bar(
                tr(
                    "PySAL library is required for spatial autocorrelation analysis. "
                    "Please install libpysal and esda packages."
                ),
                level=Qgis.Critical,
            )
            return

        try:
            # Prepare UI for processing
            self.prepare_run()
            self.set_summary_text(tr("Running analysis..."))

            # Get input parameters
            self.admin_layer = self.cbx_aggregation_layer.currentLayer()
            input_name = self.admin_layer.name()
            field = self.cbx_indicator_field.currentField()
            self.statistic_type = self.get_statistic_type()
            population_field = None
            secondary_field = None
            if self.statistic_type == STAT_MORAN_RATE:
                if hasattr(self, "cbx_population_field"):
                    population_field = self.cbx_population_field.currentField()
                if not population_field:
                    raise GeoPublicHealthException(
                        msg=tr("Population field is required for Moran Rate.")
                    )
            if self.statistic_type in (STAT_MORAN_BV_GLOBAL, STAT_MORAN_BV_LOCAL):
                if hasattr(self, "cbx_secondary_field"):
                    secondary_field = self.cbx_secondary_field.currentField()
                if not secondary_field:
                    raise GeoPublicHealthException(
                        msg=tr("Second field is required for bivariate Moran.")
                    )

            # Get the layer from the project
            self.layer = QgsProject.instance().mapLayersByName(input_name)[0]
            self.output_file_path = self.le_output_filepath.text()

            # Validate input parameters
            self.check_layer_and_file_path()
            crs_admin_layer = self.admin_layer.crs()

            # Get field structure and add new fields
            admin_layer_provider = self.layer.dataProvider()
            fields = admin_layer_provider.fields()
            self.check_existing_field(fields)
            self.append_new_fields(fields)

            # Prepare file writer
            file_writer = self.prepare_file_writer(fields, crs_admin_layer)

            # Calculate spatial weights and local Moran's I
            # Use modern approach if available, fall back to legacy approach
            if GEOPANDAS_AVAILABLE:
                QgsMessageLog.logMessage(
                    "Using modern GeoPandas approach for spatial weights",
                    "GeoPublicHealth",
                    Qgis.Info,
                )
                w = self.get_weights_modern()
                y = self.get_indicator_values_modern(field)
            else:
                QgsMessageLog.logMessage(
                    "Using legacy PySAL approach for spatial weights",
                    "GeoPublicHealth",
                    Qgis.Info,
                )
                w = self.get_weights_legacy()
                y = self.get_indicator_values_legacy(field)

            # Calculate statistics based on selection
            if self.statistic_type == STAT_MORAN:
                lm = self.calculate_moran_local(y, w)
                sig_q = lm.q * (lm.p_sim <= 0.05)
                self.create_output_features(file_writer, lm, sig_q)
                self.set_summary_text(tr("Local statistic; see output layer fields."))
            elif self.statistic_type == STAT_GEARY:
                geary = self.calculate_geary_local(y, w)
                self.create_output_features(file_writer, geary)
                self.set_summary_text(tr("Local statistic; see output layer fields."))
            elif self.statistic_type == STAT_G_LOCAL:
                g_local = self.calculate_g_local(y, w)
                self.create_output_features(file_writer, g_local)
                self.set_summary_text(tr("Local statistic; see output layer fields."))
            elif self.statistic_type == STAT_MORAN_RATE:
                if GEOPANDAS_AVAILABLE:
                    population = self.get_indicator_values_modern(population_field)
                else:
                    population = self.get_indicator_values_legacy(population_field)
                rate_global, rate_local = self.calculate_moran_rate(y, population, w)
                QgsMessageLog.logMessage(
                    f"Moran Rate I: {rate_global.I:.4f}, p={rate_global.p_sim:.4f}",
                    "GeoPublicHealth",
                    Qgis.Info,
                )
                sig_q = rate_local.q * (rate_local.p_sim <= 0.05)
                self.create_output_features(file_writer, rate_local, sig_q)
                self.set_summary_text(
                    tr("Moran Rate (Global)")
                    + f"\nI={rate_global.I:.4f}"
                    + f"\nZ={rate_global.z_sim:.4f}"
                    + f"\nP={rate_global.p_sim:.4f}"
                )
            elif self.statistic_type == STAT_MORAN_GLOBAL:
                moran_global = self.calculate_moran_global(y, w)
                QgsMessageLog.logMessage(
                    f"Moran I: {moran_global.I:.4f}, p={moran_global.p_sim:.4f}",
                    "GeoPublicHealth",
                    Qgis.Info,
                )
                self.create_output_features(file_writer, moran_global)
                self.set_summary_text(
                    tr("Moran (Global)")
                    + f"\nI={moran_global.I:.4f}"
                    + f"\nZ={moran_global.z_sim:.4f}"
                    + f"\nP={moran_global.p_sim:.4f}"
                )
            elif self.statistic_type == STAT_MORAN_BV_GLOBAL:
                if GEOPANDAS_AVAILABLE:
                    y_secondary = self.get_indicator_values_modern(secondary_field)
                else:
                    y_secondary = self.get_indicator_values_legacy(secondary_field)
                moran_bv = self.calculate_moran_bv_global(y, y_secondary, w)
                QgsMessageLog.logMessage(
                    f"Moran BV I: {moran_bv.I:.4f}, p={moran_bv.p_sim:.4f}",
                    "GeoPublicHealth",
                    Qgis.Info,
                )
                self.create_output_features(file_writer, moran_bv)
                self.set_summary_text(
                    tr("Moran BV (Global)")
                    + f"\nI={moran_bv.I:.4f}"
                    + f"\nZ={moran_bv.z_sim:.4f}"
                    + f"\nP={moran_bv.p_sim:.4f}"
                )
            elif self.statistic_type == STAT_MORAN_BV_LOCAL:
                if GEOPANDAS_AVAILABLE:
                    y_secondary = self.get_indicator_values_modern(secondary_field)
                else:
                    y_secondary = self.get_indicator_values_legacy(secondary_field)
                moran_bv_local = self.calculate_moran_bv_local(y, y_secondary, w)
                sig_q = moran_bv_local.q * (moran_bv_local.p_sim <= 0.05)
                self.create_output_features(file_writer, moran_bv_local, sig_q)
                self.set_summary_text(tr("Local statistic; see output layer fields."))
            elif self.statistic_type == STAT_JOIN_COUNTS_GLOBAL:
                y_binary = self.binarize_values(y)
                jc = self.calculate_join_counts_global(y_binary, w)
                QgsMessageLog.logMessage(
                    f"Join Counts BB: {jc.bb:.4f}, p={jc.p_sim_bb:.4f}",
                    "GeoPublicHealth",
                    Qgis.Info,
                )
                self.create_output_features(file_writer, jc)
                self.set_summary_text(
                    tr("Join Counts (Global)")
                    + f"\nBB={jc.bb:.4f} (p={jc.p_sim_bb:.4f})"
                    + f"\nWW={jc.ww:.4f}"
                    + f"\nBW={jc.bw:.4f} (p={jc.p_sim_bw:.4f})"
                )
            elif self.statistic_type == STAT_JOIN_COUNTS_LOCAL:
                y_binary = self.binarize_values(y)
                jc_local = self.calculate_join_counts_local(y_binary, w)
                self.create_output_features(file_writer, jc_local)
                self.set_summary_text(tr("Local statistic; see output layer fields."))
            del file_writer

            # Create output layer and add symbology
            self.output_layer = self.create_output_layer(field)
            QgsProject.instance().addMapLayer(self.output_layer)
            self.add_symbology()

            # Success message
            self.signalStatus.emit(3, tr("Successful process"))

        except GeoPublicHealthException as e:
            display_message_bar(msg=e.msg, level=e.level, duration=e.duration)
        except Exception as e:
            display_message_bar(
                f"{tr('Error processing autocorrelation:')} {str(e)}",
                level=Qgis.Critical,
            )
            traceback.print_exc()
        finally:
            self.end_run()

    def prepare_run(self):
        """Prepare UI for processing."""
        if hasattr(self, "button_box_ok"):
            self.button_box_ok.setDisabled(True)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()

    def end_run(self):
        """Reset UI after processing."""
        if hasattr(self, "button_box_ok"):
            self.button_box_ok.setDisabled(False)
        QApplication.restoreOverrideCursor()
        QApplication.processEvents()

    def check_layer_and_file_path(self):
        """Validate layer and output path."""
        if not self.admin_layer:
            raise NoLayerProvidedException

        # Create temporary file if no output path specified
        if not self.output_file_path:
            with NamedTemporaryFile(
                delete=False, suffix="-geopublichealth.shp"
            ) as temp_file:
                self.output_file_path = temp_file.name
        else:
            # Check if file exists and create unique name if needed
            if os.path.exists(self.output_file_path):
                base, extension = os.path.splitext(self.output_file_path)
                counter = 1
                while os.path.exists(self.output_file_path):
                    self.output_file_path = f"{base}_{counter}{extension}"
                    counter += 1

    def get_statistic_type(self):
        if hasattr(self, "cbx_statistic"):
            stat_text = self.cbx_statistic.currentText().strip().lower()
            if "geary" in stat_text:
                return STAT_GEARY
            if "getis" in stat_text or "g (local)" in stat_text:
                return STAT_G_LOCAL
            if "rate" in stat_text:
                return STAT_MORAN_RATE
            if "join" in stat_text and "global" in stat_text:
                return STAT_JOIN_COUNTS_GLOBAL
            if "join" in stat_text and "local" in stat_text:
                return STAT_JOIN_COUNTS_LOCAL
            if "bivariate" in stat_text and "global" in stat_text:
                return STAT_MORAN_BV_GLOBAL
            if "bivariate" in stat_text and "local" in stat_text:
                return STAT_MORAN_BV_LOCAL
            if "global" in stat_text:
                return STAT_MORAN_GLOBAL
        return STAT_MORAN

    def get_output_field_names(self):
        if self.statistic_type == STAT_MORAN:
            return ["LISA_P", "LISA_Z", "LISA_Q", "LISA_I", "LISA_C"]
        if self.statistic_type == STAT_MORAN_RATE:
            return ["RATE_P", "RATE_Z", "RATE_Q", "RATE_I", "RATE_C"]
        if self.statistic_type == STAT_GEARY:
            return ["GEARY_G", "GEARY_P", "GEARY_S"]
        if self.statistic_type == STAT_G_LOCAL:
            return ["G_LOC", "G_Z", "G_P", "G_HOT"]
        if self.statistic_type == STAT_MORAN_GLOBAL:
            return ["MORAN_I", "MORAN_Z", "MORAN_P", "MORAN_S"]
        if self.statistic_type == STAT_MORAN_BV_GLOBAL:
            return ["MBV_I", "MBV_Z", "MBV_P", "MBV_S"]
        if self.statistic_type == STAT_MORAN_BV_LOCAL:
            return ["MBV_P", "MBV_Z", "MBV_Q", "MBV_I", "MBV_C"]
        if self.statistic_type == STAT_JOIN_COUNTS_GLOBAL:
            return ["JC_BB", "JC_WW", "JC_BW", "JC_PBB", "JC_PBW", "JC_S"]
        if self.statistic_type == STAT_JOIN_COUNTS_LOCAL:
            return ["LJC", "LJC_P", "LJC_S"]
        return ["LISA_P", "LISA_Z", "LISA_Q", "LISA_I", "LISA_C"]

    def get_output_layer_prefix(self):
        if self.statistic_type == STAT_MORAN:
            return "LISA"
        if self.statistic_type == STAT_MORAN_RATE:
            return "RATE"
        if self.statistic_type == STAT_GEARY:
            return "GEARY"
        if self.statistic_type == STAT_G_LOCAL:
            return "GLOCAL"
        if self.statistic_type == STAT_MORAN_GLOBAL:
            return "MORAN"
        if self.statistic_type == STAT_MORAN_BV_GLOBAL:
            return "MBV"
        if self.statistic_type == STAT_MORAN_BV_LOCAL:
            return "MBVL"
        if self.statistic_type == STAT_JOIN_COUNTS_GLOBAL:
            return "JC"
        if self.statistic_type == STAT_JOIN_COUNTS_LOCAL:
            return "LJC"
        return "LISA"

    def get_output_layer_title(self, field):
        if self.statistic_type == STAT_MORAN:
            return f"LISA Moran's I - {field}"
        if self.statistic_type == STAT_MORAN_RATE:
            return f"Moran Rate - {field}"
        if self.statistic_type == STAT_GEARY:
            return f"Local Geary - {field}"
        if self.statistic_type == STAT_G_LOCAL:
            return f"Getis-Ord G - {field}"
        if self.statistic_type == STAT_MORAN_GLOBAL:
            return f"Moran Global - {field}"
        if self.statistic_type == STAT_MORAN_BV_GLOBAL:
            return f"Moran BV Global - {field}"
        if self.statistic_type == STAT_MORAN_BV_LOCAL:
            return f"Moran BV Local - {field}"
        if self.statistic_type == STAT_JOIN_COUNTS_GLOBAL:
            return f"Join Counts Global - {field}"
        if self.statistic_type == STAT_JOIN_COUNTS_LOCAL:
            return f"Join Counts Local - {field}"
        return f"LISA Moran's I - {field}"

    def update_statistic_controls(self):
        stat_type = self.get_statistic_type()
        is_rate = stat_type == STAT_MORAN_RATE
        is_bivariate = stat_type in (STAT_MORAN_BV_GLOBAL, STAT_MORAN_BV_LOCAL)
        is_join = stat_type in (STAT_JOIN_COUNTS_GLOBAL, STAT_JOIN_COUNTS_LOCAL)
        auto_binary = False
        if hasattr(self, "cbx_binary_auto"):
            auto_binary = self.cbx_binary_auto.isChecked()

        if hasattr(self, "cbx_population_field"):
            self.cbx_population_field.setEnabled(is_rate)
        if hasattr(self, "label_population"):
            self.label_population.setEnabled(is_rate)

        if hasattr(self, "cbx_secondary_field"):
            self.cbx_secondary_field.setEnabled(is_bivariate)
        if hasattr(self, "label_secondary_field"):
            self.label_secondary_field.setEnabled(is_bivariate)

        if hasattr(self, "label_statistic_hint"):
            hint = tr("(Local)")
            if stat_type in (STAT_MORAN_GLOBAL, STAT_MORAN_BV_GLOBAL):
                hint = tr("(Global)")
            self.label_statistic_hint.setText(hint)

        if hasattr(self, "sbx_binary_threshold"):
            self.sbx_binary_threshold.setEnabled(is_join and not auto_binary)
        if hasattr(self, "label_binary_threshold"):
            self.label_binary_threshold.setEnabled(is_join and not auto_binary)
        if hasattr(self, "cbx_binary_auto"):
            self.cbx_binary_auto.setEnabled(is_join)
        if hasattr(self, "label_binary_auto"):
            self.label_binary_auto.setEnabled(is_join)

    def update_help_text(self):
        stat_type = self.get_statistic_type()
        help_map = {
            STAT_MORAN: "moran",
            STAT_GEARY: "geary",
            STAT_G_LOCAL: "g_local",
            STAT_MORAN_RATE: "moran_rate",
            STAT_MORAN_GLOBAL: "moran_global",
            STAT_MORAN_BV_GLOBAL: "moran_bv_global",
            STAT_MORAN_BV_LOCAL: "moran_bv_local",
            STAT_JOIN_COUNTS_GLOBAL: "join_counts_global",
            STAT_JOIN_COUNTS_LOCAL: "join_counts_local",
        }
        help_key = help_map.get(stat_type, "moran")
        if hasattr(self, "label_stat_help"):
            short_help = {
                "moran": tr("Moran (LISA): local clusters."),
                "geary": tr("Local Geary: local dissimilarity."),
                "g_local": tr("Getis-Ord G: hot/cold spots."),
                "moran_rate": tr("Moran Rate: case/population."),
                "moran_global": tr("Moran (Global): overall autocorrelation."),
                "moran_bv_global": tr("Moran BV (Global): two-field association."),
                "moran_bv_local": tr("Moran BV (Local): co-location clusters."),
                "join_counts_global": tr("Join Counts: global binary clustering."),
                "join_counts_local": tr("Join Counts (Local): binary clusters."),
            }
            self.label_stat_help.setText(short_help.get(help_key, ""))

        help_html = help_autocorrelation(help_key)
        self.signalHelpChanged.emit(help_html)

    def set_summary_text(self, text):
        if hasattr(self, "te_summary"):
            self.te_summary.setPlainText(text)

    def binarize_values(self, values):
        auto_binary = False
        if hasattr(self, "cbx_binary_auto"):
            auto_binary = self.cbx_binary_auto.isChecked()

        if auto_binary:
            values_array = np.asarray(values)
            valid = values_array[np.isfinite(values_array)]
            unique_values = np.unique(valid)
            if set(unique_values.tolist()).issubset({0, 1}):
                return (values_array == 1).astype(int)

            QgsMessageLog.logMessage(
                tr("Binary auto-detect failed; using threshold."),
                "GeoPublicHealth",
                Qgis.Warning,
            )

        if not hasattr(self, "sbx_binary_threshold"):
            return (values > 0).astype(int)

        threshold = self.sbx_binary_threshold.value()
        return (values >= threshold).astype(int)

    @staticmethod
    def _hotspot_class(z_value, p_value):
        if p_value > 0.05:
            return 0
        return 1 if z_value > 0 else -1

    def check_existing_field(self, fields):
        """Check if output fields already exist in the layer."""
        for field_name in self.get_output_field_names():
            if fields.indexOf(field_name) != -1:
                raise FieldExistingException(field=field_name)

    def append_new_fields(self, fields):
        """Add new fields for LISA results."""
        if self.statistic_type == STAT_MORAN:
            fields.append(QgsField("LISA_P", 6, "Real", 10, 6))
            fields.append(QgsField("LISA_Z", 6, "Real", 10, 6))
            fields.append(QgsField("LISA_Q", 2, "Integer", 1, 0))
            fields.append(QgsField("LISA_I", 6, "Real", 10, 6))
            fields.append(QgsField("LISA_C", 2, "Integer", 1, 0))
        elif self.statistic_type == STAT_MORAN_RATE:
            fields.append(QgsField("RATE_P", 6, "Real", 10, 6))
            fields.append(QgsField("RATE_Z", 6, "Real", 10, 6))
            fields.append(QgsField("RATE_Q", 2, "Integer", 1, 0))
            fields.append(QgsField("RATE_I", 6, "Real", 10, 6))
            fields.append(QgsField("RATE_C", 2, "Integer", 1, 0))
        elif self.statistic_type == STAT_GEARY:
            fields.append(QgsField("GEARY_G", 6, "Real", 10, 6))
            fields.append(QgsField("GEARY_P", 6, "Real", 10, 6))
            fields.append(QgsField("GEARY_S", 2, "Integer", 1, 0))
        elif self.statistic_type == STAT_G_LOCAL:
            fields.append(QgsField("G_LOC", 6, "Real", 10, 6))
            fields.append(QgsField("G_Z", 6, "Real", 10, 6))
            fields.append(QgsField("G_P", 6, "Real", 10, 6))
            fields.append(QgsField("G_HOT", 2, "Integer", 1, 0))
        elif self.statistic_type == STAT_MORAN_GLOBAL:
            fields.append(QgsField("MORAN_I", 6, "Real", 10, 6))
            fields.append(QgsField("MORAN_Z", 6, "Real", 10, 6))
            fields.append(QgsField("MORAN_P", 6, "Real", 10, 6))
            fields.append(QgsField("MORAN_S", 2, "Integer", 1, 0))
        elif self.statistic_type == STAT_MORAN_BV_GLOBAL:
            fields.append(QgsField("MBV_I", 6, "Real", 10, 6))
            fields.append(QgsField("MBV_Z", 6, "Real", 10, 6))
            fields.append(QgsField("MBV_P", 6, "Real", 10, 6))
            fields.append(QgsField("MBV_S", 2, "Integer", 1, 0))
        elif self.statistic_type == STAT_MORAN_BV_LOCAL:
            fields.append(QgsField("MBV_P", 6, "Real", 10, 6))
            fields.append(QgsField("MBV_Z", 6, "Real", 10, 6))
            fields.append(QgsField("MBV_Q", 2, "Integer", 1, 0))
            fields.append(QgsField("MBV_I", 6, "Real", 10, 6))
            fields.append(QgsField("MBV_C", 2, "Integer", 1, 0))
        elif self.statistic_type == STAT_JOIN_COUNTS_GLOBAL:
            fields.append(QgsField("JC_BB", 6, "Real", 10, 6))
            fields.append(QgsField("JC_WW", 6, "Real", 10, 6))
            fields.append(QgsField("JC_BW", 6, "Real", 10, 6))
            fields.append(QgsField("JC_PBB", 6, "Real", 10, 6))
            fields.append(QgsField("JC_PBW", 6, "Real", 10, 6))
            fields.append(QgsField("JC_S", 2, "Integer", 1, 0))
        elif self.statistic_type == STAT_JOIN_COUNTS_LOCAL:
            fields.append(QgsField("LJC", 6, "Real", 10, 6))
            fields.append(QgsField("LJC_P", 6, "Real", 10, 6))
            fields.append(QgsField("LJC_S", 2, "Integer", 1, 0))

    def prepare_file_writer(self, fields, crs_admin_layer):
        """Prepare the output file writer."""
        # Determine output format based on file extension
        output_ext = os.path.splitext(self.output_file_path)[1].lower()
        driver_name = "GPKG" if output_ext == ".gpkg" else "ESRI Shapefile"

        # Setup save options
        save_options = QgsVectorFileWriter.SaveVectorOptions()
        save_options.driverName = driver_name
        save_options.encoding = "UTF-8"

        # If it's a GPKG, set the layer name
        if driver_name == "GPKG":
            field_name = self.cbx_indicator_field.currentField()
            layer_prefix = self.get_output_layer_prefix()
            save_options.layerName = f"{layer_prefix}_{field_name}".replace(" ", "_")

        # Create the vector file writer
        file_writer = QgsVectorFileWriter.create(
            self.output_file_path,
            fields,
            QgsWkbTypes.Polygon,
            crs_admin_layer,
            QgsProject.instance().transformContext(),
            save_options,
        )

        if file_writer.hasError():
            error_message = file_writer.errorMessage()
            raise GeoPublicHealthException(
                msg=f"Error creating output file: {error_message}"
            )

        return file_writer

    def get_weights_modern(self):
        """
        Get spatial weights matrix using GeoPandas (modern approach).

        Returns:
            libpysal.weights: Spatial weights matrix
        """
        try:
            contiguity_index = 0  # Default to Queen
            if hasattr(self, "cbx_contiguity"):
                contiguity_index = self.cbx_contiguity.currentIndex()

            source = self.admin_layer.source()
            gdf = self._read_geopandas_layer(source)

            # Create weights matrix
            if contiguity_index == 0:  # queen
                # Explicitly set use_index parameter to silence the warning
                w = Queen.from_dataframe(gdf, use_index=True)
            else:  # rook
                # Also update the Rook method for consistency
                w = Rook.from_dataframe(gdf, use_index=True)

            return w

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Modern weights approach failed, falling back to legacy: {str(e)}",
                "GeoPublicHealth",
                Qgis.Warning,
            )
            return self.get_weights_legacy()

    def _read_geopandas_layer(self, source):
        """Read a layer with GeoPandas, with fallback engine support."""
        if "|layername=" in source:
            parts = source.split("|layername=")
            layer_path = parts[0]
            layer_name = parts[1] if len(parts) > 1 else None
        else:
            layer_path = source
            layer_name = None

        read_kwargs = {}
        if layer_name:
            read_kwargs["layer"] = layer_name

        try:
            gdf = gpd.read_file(layer_path, **read_kwargs)
            return self._ensure_geopandas_geometry(gdf)
        except Exception as exc:
            if "expected bytes, str found" not in str(exc):
                raise

            QgsMessageLog.logMessage(
                "GeoPandas read_file failed with pyogrio; retrying with Fiona.",
                "GeoPublicHealth",
                Qgis.Warning,
            )

        try:
            gdf = gpd.read_file(layer_path, engine="fiona", **read_kwargs)
            return self._ensure_geopandas_geometry(gdf)
        except ValueError as exc:
            if "without a geometry column" not in str(exc):
                raise

            return self._read_fiona_without_geometry(layer_path, layer_name)

    def _ensure_geopandas_geometry(self, gdf):
        if getattr(gdf, "geometry", None) is not None and not gdf.geometry.isna().all():
            return gdf

        geometry_column = None
        for candidate in (
            "geometry",
            "geom",
            "wkt_geom",
            "wkt",
            "geom_wkt",
            "geometry_wkt",
        ):
            if candidate in gdf.columns:
                geometry_column = candidate
                break

        if geometry_column:
            gdf = gdf.copy()
            gdf.set_geometry(
                gpd.GeoSeries.from_wkt(gdf[geometry_column]),
                inplace=True,
            )

        if gdf.crs is None:
            layer_crs = self.admin_layer.crs()
            if layer_crs and layer_crs.isValid():
                crs_value = layer_crs.authid() or layer_crs.toWkt()
                self._set_geopandas_crs(gdf, crs_value)

        return gdf

    def _set_geopandas_crs(self, gdf, crs_value):
        if not crs_value:
            return

        try:
            gdf.set_crs(crs_value, inplace=True)
            return
        except TypeError:
            if isinstance(crs_value, str):
                try:
                    gdf.set_crs(crs_value.encode("utf-8"), inplace=True)
                    return
                except Exception:
                    pass

        QgsMessageLog.logMessage(
            "Unable to set CRS for GeoPandas data.",
            "GeoPublicHealth",
            Qgis.Warning,
        )

    def _read_fiona_without_geometry(self, layer_path, layer_name):
        try:
            import fiona
            from shapely.geometry import shape
        except ImportError as exc:
            raise ImportError(
                "Fiona is required to read GeoPackage layers without geometry."
            ) from exc

        rows = []
        geometries = []
        with fiona.open(layer_path, layer=layer_name) as source:
            for feature in source:
                rows.append(feature.get("properties") or {})
                geom = feature.get("geometry")
                geometries.append(shape(geom) if geom else None)

            crs_value = source.crs_wkt or source.crs

        gdf = gpd.GeoDataFrame(pd.DataFrame(rows), geometry=geometries)
        gdf = self._ensure_geopandas_geometry(gdf)

        if gdf.crs is None:
            layer_crs = self.admin_layer.crs()
            if layer_crs and layer_crs.isValid():
                crs_value = layer_crs.authid() or layer_crs.toWkt()

            self._set_geopandas_crs(gdf, crs_value)

        return gdf

    def get_weights_legacy(self):
        """
        Get spatial weights matrix using legacy PySAL approach.

        Note: This only works with shapefiles, not GeoPackage layers.

        Returns:
            libpysal.weights: Spatial weights matrix
        """
        try:
            contiguity_index = 0  # Default to Queen
            if hasattr(self, "cbx_contiguity"):
                contiguity_index = self.cbx_contiguity.currentIndex()

            source = self.admin_layer.source()

            # Legacy approach only works with shapefiles
            if not source.lower().endswith(".shp"):
                raise ValueError(
                    "Legacy PySAL approach requires shapefile format. "
                    "Please ensure GeoPandas is installed for GeoPackage support."
                )

            # Create weights from shapefile (no context manager - not supported)
            if contiguity_index == 0:  # queen
                w = Queen.from_shapefile(source)
            else:  # rook
                w = Rook.from_shapefile(source)

            return w

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error in legacy weights approach: {str(e)}",
                "GeoPublicHealth",
                Qgis.Critical,
            )
            raise

    def get_indicator_values_modern(self, field):
        """
        Get indicator values using GeoPandas (modern approach).

        Args:
            field: Field name containing indicator values

        Returns:
            numpy.ndarray: Array of indicator values
        """
        try:
            source = self.admin_layer.source()
            gdf = self._read_geopandas_layer(source)

            # Get values of the specified field
            if field in gdf.columns:
                y = np.array(gdf[field])
                return y
            else:
                QgsMessageLog.logMessage(
                    f"Field '{field}' not found in GeoDataFrame, falling back to legacy method",
                    "GeoPublicHealth",
                    Qgis.Warning,
                )
                return self.get_indicator_values_legacy(field)

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Modern indicator approach failed, falling back to legacy: {str(e)}",
                "GeoPublicHealth",
                Qgis.Warning,
            )
            return self.get_indicator_values_legacy(field)

    def get_indicator_values_legacy(self, field):
        """
        Get indicator values using legacy PySAL approach.

        Note: This only works with shapefiles, not GeoPackage layers.

        Args:
            field: Field name containing indicator values

        Returns:
            numpy.ndarray: Array of indicator values
        """
        try:
            source = self.admin_layer.source()

            # Legacy approach only works with shapefiles
            if not source.lower().endswith(".shp"):
                raise ValueError(
                    "Legacy PySAL approach requires shapefile format. "
                    "Please ensure GeoPandas is installed for GeoPackage support."
                )

            # Read from DBF file (no context manager - not supported by PurePyShpWrapper)
            dbf_path = source.replace(".shp", ".dbf")
            f = libpysal.io.open(dbf_path)
            y = np.array(f.by_col[str(field)])
            f.close()

            return y

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error in legacy indicator approach: {str(e)}",
                "GeoPublicHealth",
                Qgis.Critical,
            )
            raise

    def calculate_moran_local(self, y, w):
        """
        Calculate Local Moran's I statistics.

        Args:
            y: Array of indicator values
            w: Spatial weights matrix

        Returns:
            esda.moran.Moran_Local: Local Moran's I statistics
        """
        try:
            return Moran_Local(y, w, transformation="r", permutations=999)
        except Exception as e:
            error_msg = tr("Error calculating Local Moran's I:")
            display_message_bar(f"{error_msg} {str(e)}", level=Qgis.Critical)
            raise

    def calculate_moran_global(self, y, w):
        try:
            return Moran(y, w, transformation="r", permutations=999)
        except Exception as e:
            error_msg = tr("Error calculating Global Moran's I:")
            display_message_bar(f"{error_msg} {str(e)}", level=Qgis.Critical)
            raise

    def calculate_moran_bv_global(self, x, y, w):
        try:
            return Moran_BV(x, y, w, transformation="r", permutations=999)
        except Exception as e:
            error_msg = tr("Error calculating Bivariate Moran's I:")
            display_message_bar(f"{error_msg} {str(e)}", level=Qgis.Critical)
            raise

    def calculate_moran_bv_local(self, x, y, w):
        try:
            return Moran_Local_BV(x, y, w, transformation="r", permutations=999)
        except Exception as e:
            error_msg = tr("Error calculating Bivariate Local Moran's I:")
            display_message_bar(f"{error_msg} {str(e)}", level=Qgis.Critical)
            raise

    def calculate_join_counts_global(self, y, w):
        try:
            return Join_Counts(y, w, permutations=999)
        except Exception as e:
            error_msg = tr("Error calculating Join Counts:")
            display_message_bar(f"{error_msg} {str(e)}", level=Qgis.Critical)
            raise

    def calculate_join_counts_local(self, y, w):
        try:
            return Join_Counts_Local(
                connectivity=w,
                permutations=999,
                n_jobs=1,
                keep_simulations=False,
            ).fit(y)
        except Exception as e:
            error_msg = tr("Error calculating Local Join Counts:")
            display_message_bar(f"{error_msg} {str(e)}", level=Qgis.Critical)
            raise

    def calculate_geary_local(self, y, w):
        try:
            return Geary_Local(
                connectivity=w,
                permutations=999,
                n_jobs=1,
                keep_simulations=False,
            ).fit(y)
        except Exception as e:
            error_msg = tr("Error calculating Local Geary:")
            display_message_bar(f"{error_msg} {str(e)}", level=Qgis.Critical)
            raise

    def calculate_g_local(self, y, w):
        try:
            return G_Local(
                y,
                w,
                transform="R",
                permutations=999,
                n_jobs=1,
                keep_simulations=False,
            )
        except Exception as e:
            error_msg = tr("Error calculating Getis-Ord G:")
            display_message_bar(f"{error_msg} {str(e)}", level=Qgis.Critical)
            raise

    def calculate_moran_rate(self, events, population, w):
        try:
            global_rate = Moran_Rate(events, population, w, permutations=999)
            local_rate = Moran_Local_Rate(events, population, w, permutations=999)
            return global_rate, local_rate
        except Exception as e:
            error_msg = tr("Error calculating Moran Rate:")
            display_message_bar(f"{error_msg} {str(e)}", level=Qgis.Critical)
            raise

    def create_output_features(self, file_writer, stats, sig_q=None):
        """
        Create output features with LISA statistics.

        Args:
            file_writer: QgsVectorFileWriter
            lm: Local Moran's I statistics
            sig_q: Significant quadrants
        """
        try:
            for i, feature in enumerate(self.admin_layer.getFeatures()):
                attributes = feature.attributes()

                if self.statistic_type == STAT_MORAN:
                    attributes.append(float(stats.p_sim[i]))
                    attributes.append(float(stats.z_sim[i]))
                    attributes.append(int(stats.q[i]))
                    attributes.append(float(stats.Is[i]))
                    attributes.append(int(sig_q[i]))
                elif self.statistic_type == STAT_MORAN_RATE:
                    attributes.append(float(stats.p_sim[i]))
                    attributes.append(float(stats.z_sim[i]))
                    attributes.append(int(stats.q[i]))
                    attributes.append(float(stats.Is[i]))
                    attributes.append(int(sig_q[i]))
                elif self.statistic_type == STAT_GEARY:
                    attributes.append(float(stats.localG[i]))
                    attributes.append(float(stats.p_sim[i]))
                    attributes.append(int(stats.p_sim[i] <= 0.05))
                elif self.statistic_type == STAT_G_LOCAL:
                    attributes.append(float(stats.Gs[i]))
                    attributes.append(float(stats.Zs[i]))
                    attributes.append(float(stats.p_sim[i]))
                    attributes.append(self._hotspot_class(stats.Zs[i], stats.p_sim[i]))
                elif self.statistic_type == STAT_MORAN_GLOBAL:
                    attributes.append(float(stats.I))
                    attributes.append(float(stats.z_sim))
                    attributes.append(float(stats.p_sim))
                    attributes.append(int(stats.p_sim <= 0.05))
                elif self.statistic_type == STAT_MORAN_BV_GLOBAL:
                    attributes.append(float(stats.I))
                    attributes.append(float(stats.z_sim))
                    attributes.append(float(stats.p_sim))
                    attributes.append(int(stats.p_sim <= 0.05))
                elif self.statistic_type == STAT_MORAN_BV_LOCAL:
                    attributes.append(float(stats.p_sim[i]))
                    attributes.append(float(stats.z_sim[i]))
                    attributes.append(int(stats.q[i]))
                    attributes.append(float(stats.Is[i]))
                    attributes.append(int(sig_q[i]))
                elif self.statistic_type == STAT_JOIN_COUNTS_GLOBAL:
                    attributes.append(float(stats.bb))
                    attributes.append(float(stats.ww))
                    attributes.append(float(stats.bw))
                    attributes.append(float(stats.p_sim_bb))
                    attributes.append(float(stats.p_sim_bw))
                    attributes.append(int(stats.p_sim_bb <= 0.05))
                elif self.statistic_type == STAT_JOIN_COUNTS_LOCAL:
                    attributes.append(float(stats.LJC[i]))
                    attributes.append(float(stats.p_sim[i]))
                    attributes.append(int(stats.p_sim[i] <= 0.05))

                new_feature = QgsFeature()
                new_geom = QgsGeometry(feature.geometry())
                new_feature.setAttributes(attributes)
                new_feature.setGeometry(new_geom)

                file_writer.addFeature(new_feature)
        except Exception as e:
            display_message_bar(
                f"{tr('Error creating output features:')} {str(e)}", level=Qgis.Critical
            )
            raise

    def create_output_layer(self, field):
        """
        Create output layer from the output file.

        Args:
            field: Field name for layer naming

        Returns:
            QgsVectorLayer: Output layer
        """
        if not self.output_file_path:
            return

        # Determine if GeoPackage or Shapefile
        is_gpkg = self.output_file_path.lower().endswith(".gpkg")

        # Construct layer URI
        if is_gpkg:
            layer_prefix = self.get_output_layer_prefix()
            layer_name = f"{layer_prefix}_{field}".replace(" ", "_")
            layer_uri = f"{self.output_file_path}|layername={layer_name}"
        else:
            layer_uri = self.output_file_path

        # Create vector layer
        output_layer = QgsVectorLayer(
            layer_uri, self.get_output_layer_title(field), "ogr"
        )

        if not output_layer.isValid():
            display_message_bar(tr("Output layer invalid"), level=Qgis.Critical)
            raise GeoPublicHealthException(
                msg=tr("Failed to create valid output layer")
            )

        return output_layer

    def add_symbology(self):
        """Add symbology to the output layer."""
        try:
            if self.statistic_type in (STAT_MORAN_GLOBAL, STAT_MORAN_BV_GLOBAL):
                categories = []
                for value, (color, label) in {
                    1: ("#b92815", tr("Significant")),
                    0: ("#c0c0c0", tr("Not significant")),
                }.items():
                    sym = QgsSymbol.defaultSymbol(self.output_layer.geometryType())
                    sym.setColor(QColor(color))
                    categories.append(QgsRendererCategory(value, sym, label))

                field_name = "MORAN_S"
                if self.statistic_type == STAT_MORAN_BV_GLOBAL:
                    field_name = "MBV_S"
                renderer = QgsCategorizedSymbolRenderer(field_name, categories)
                self.output_layer.setRenderer(renderer)
                return

            if self.statistic_type == STAT_JOIN_COUNTS_GLOBAL:
                categories = []
                for value, (color, label) in {
                    1: ("#b92815", tr("Significant")),
                    0: ("#c0c0c0", tr("Not significant")),
                }.items():
                    sym = QgsSymbol.defaultSymbol(self.output_layer.geometryType())
                    sym.setColor(QColor(color))
                    categories.append(QgsRendererCategory(value, sym, label))

                renderer = QgsCategorizedSymbolRenderer("JC_S", categories)
                self.output_layer.setRenderer(renderer)
                return

            if self.statistic_type == STAT_GEARY:
                categories = []
                for value, (color, label) in {
                    1: ("#b92815", tr("Significant")),
                    0: ("#c0c0c0", tr("Not significant")),
                }.items():
                    sym = QgsSymbol.defaultSymbol(self.output_layer.geometryType())
                    sym.setColor(QColor(color))
                    categories.append(QgsRendererCategory(value, sym, label))

                renderer = QgsCategorizedSymbolRenderer("GEARY_S", categories)
                self.output_layer.setRenderer(renderer)
                self.output_layer.triggerRepaint()
                return

            if self.statistic_type == STAT_G_LOCAL:
                categories = []
                for value, (color, label) in {
                    1: ("#b92815", tr("Hotspot")),
                    -1: ("#3f70df", tr("Coldspot")),
                    0: ("#c0c0c0", tr("Not significant")),
                }.items():
                    sym = QgsSymbol.defaultSymbol(self.output_layer.geometryType())
                    sym.setColor(QColor(color))
                    categories.append(QgsRendererCategory(value, sym, label))

                renderer = QgsCategorizedSymbolRenderer("G_HOT", categories)
                self.output_layer.setRenderer(renderer)
                self.output_layer.triggerRepaint()
                return

            if self.statistic_type == STAT_JOIN_COUNTS_LOCAL:
                categories = []
                for value, (color, label) in {
                    1: ("#b92815", tr("Significant")),
                    0: ("#c0c0c0", tr("Not significant")),
                }.items():
                    sym = QgsSymbol.defaultSymbol(self.output_layer.geometryType())
                    sym.setColor(QColor(color))
                    categories.append(QgsRendererCategory(value, sym, label))

                renderer = QgsCategorizedSymbolRenderer("LJC_S", categories)
                self.output_layer.setRenderer(renderer)
                self.output_layer.triggerRepaint()
                return

            # Create categories for LISA quadrants
            categories = []
            for lisaCategory, (color, label) in self.lisa.items():
                sym = QgsSymbol.defaultSymbol(self.output_layer.geometryType())
                sym.setColor(QColor(color))
                category = QgsRendererCategory(lisaCategory, sym, label)
                categories.append(category)

            # Create a new layer for significance
            # Determine if GeoPackage or Shapefile
            is_gpkg = self.output_file_path.lower().endswith(".gpkg")

            # Create a new layer
            if is_gpkg:
                # For GeoPackage, clone the original layer
                field_name = self.cbx_indicator_field.currentField()
                layer_prefix = self.get_output_layer_prefix()
                new_layer_name = f"{layer_prefix}_{field_name}_sig".replace(" ", "_")

                # Need to create a new copy in the GeoPackage
                options = QgsVectorFileWriter.SaveVectorOptions()
                options.driverName = "GPKG"
                options.layerName = new_layer_name
                options.actionOnExistingFile = (
                    QgsVectorFileWriter.CreateOrOverwriteLayer
                )

                # Create the new layer
                result = QgsVectorFileWriter.writeAsVectorFormat(
                    self.output_layer, self.output_file_path, options
                )

                if result[0] != QgsVectorFileWriter.NoError:
                    display_message_bar(
                        tr("Failed to create significance layer"), level=Qgis.Warning
                    )
                    return

                # Load the new layer
                layer_uri = f"{self.output_file_path}|layername={new_layer_name}"
                new_layer = QgsVectorLayer(
                    layer_uri, self.output_layer.name() + " significance test", "ogr"
                )
            else:
                # For Shapefile, just create a new layer with the same source
                new_layer = QgsVectorLayer(
                    self.output_layer.source(),
                    self.output_layer.name() + " significance test",
                    self.output_layer.providerType(),
                )

            # Set layer opacity
            self.output_layer.setOpacity(1.0)
            QgsProject.instance().addMapLayer(new_layer)

            # Set categorized renderer for LISA quadrants
            quadrant_field = "LISA_Q"
            sig_field = "LISA_C"
            if self.statistic_type == STAT_MORAN_RATE:
                quadrant_field = "RATE_Q"
                sig_field = "RATE_C"
            if self.statistic_type == STAT_MORAN_BV_LOCAL:
                quadrant_field = "MBV_Q"
                sig_field = "MBV_C"

            renderer = QgsCategorizedSymbolRenderer(quadrant_field, categories)
            self.output_layer.setRenderer(renderer)

            # Set graduated renderer for significance
            symbol = QgsSymbol.defaultSymbol(new_layer.geometryType())
            color_ramp = QgsGradientColorRamp(QColor(0, 0, 0), QColor(255, 0, 0))

            # Get registry and method for classification
            registry = QgsApplication.classificationMethodRegistry()
            method_id = "Jenks"  # Natural breaks
            classification_method = registry.method(method_id)

            if classification_method:
                # Set method and create renderer
                renderer = QgsGraduatedSymbolRenderer(sig_field)
                renderer.setSourceSymbol(symbol.clone())
                renderer.setSourceColorRamp(color_ramp.clone())
                renderer.setClassificationMethod(classification_method.clone())
                renderer.updateClasses(new_layer, 4)

                # Apply renderer
                new_layer.setRenderer(renderer)
                new_layer.setOpacity(0.4)
                new_layer.triggerRepaint()

                # Refresh layer tree
                root = QgsProject.instance().layerTreeRoot()
                if root:
                    layer_node = root.findLayer(new_layer.id())
                    if layer_node:
                        layer_node.setCustomProperty("refreshLegend", 1)
            else:
                # Fallback to older method if classification method not available
                renderer = QgsGraduatedSymbolRenderer.createRenderer(
                    new_layer,
                    sig_field,
                    4,
                    QgsGraduatedSymbolRenderer.Jenks,
                    symbol,
                    color_ramp,
                )
                new_layer.setRenderer(renderer)
                new_layer.setOpacity(0.4)
                new_layer.triggerRepaint()

        except Exception as e:
            display_message_bar(
                f"{tr('Error applying symbology:')} {str(e)}", level=Qgis.Critical
            )
            traceback.print_exc()


class AutocorrelationDialog(CommonAutocorrelationDialog, FORM_CLASS):
    """
    Dialog implementation for Autocorrelation analysis.
    """

    def __init__(self, parent=None):
        """
        Constructor for the Autocorrelation dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        FORM_CLASS.setupUi(self, self)

        # Set NULL constant for comparison
        global NULL
        NULL = QVariant()

        self.use_area = False
        self.setup_ui()

    def run_stats(self):
        """Main function which do the process."""
        super().run_stats()
