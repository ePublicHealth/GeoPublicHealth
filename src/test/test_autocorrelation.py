# -*- coding: utf-8 -*-
"""
/***************************************************************************

                                 GeoPublicHealth
                                 A QGIS plugin

                              -------------------
        begin                : 2026-01-26
        copyright            : (C) 2026 by GeoPublicHealth Team
        email                : info@geopublichealth.org
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

import unittest

from src.core.services import autocorrelation

try:
    import libpysal

    LIBPYSAL_AVAILABLE = True
except ImportError:
    LIBPYSAL_AVAILABLE = False


class TestAutocorrelation(unittest.TestCase):
    @unittest.skipUnless(autocorrelation.PYSAL_AVAILABLE, "PySAL not available")
    def test_local_moran_basic(self):
        values = [10, 20, 30]
        neighbors = {0: [1], 1: [0, 2], 2: [1]}
        result = autocorrelation.local_moran(values, neighbors, permutations=0)
        self.assertEqual(len(result["local_stat"]), 3)
        for value in result["local_stat"]:
            self.assertTrue(value == value)

    @unittest.skipUnless(autocorrelation.PYSAL_AVAILABLE, "PySAL not available")
    def test_invalid_weights_empty_neighbors(self):
        values = [1, 2]
        neighbors = {0: [], 1: []}
        with self.assertRaises(ValueError):
            autocorrelation.local_moran(values, neighbors, permutations=0)

    @unittest.skipUnless(
        autocorrelation.PYSAL_AVAILABLE and LIBPYSAL_AVAILABLE,
        "PySAL not available",
    )
    def test_global_and_local_stats(self):
        values = [1, 2, 3, 4]
        weights = libpysal.weights.lat2W(2, 2)
        weights.transform = "r"

        moran_global = autocorrelation.moran_global(values, weights, permutations=0)
        self.assertTrue(hasattr(moran_global, "I"))

        moran_local = autocorrelation.moran_local(values, weights, permutations=0)
        self.assertEqual(len(moran_local.Is), 4)

        geary_local = autocorrelation.geary_local(values, weights, permutations=0)
        self.assertEqual(len(geary_local.localG), 4)

        g_local = autocorrelation.g_local(values, weights, permutations=0)
        self.assertEqual(len(g_local.Gs), 4)

    @unittest.skipUnless(
        autocorrelation.PYSAL_AVAILABLE and LIBPYSAL_AVAILABLE,
        "PySAL not available",
    )
    def test_join_counts(self):
        values = [1, 0, 1, 0]
        weights = libpysal.weights.lat2W(2, 2)
        weights.transform = "r"

        join_global = autocorrelation.join_counts_global(
            values, weights, permutations=0
        )
        self.assertTrue(hasattr(join_global, "bb"))

        join_local = autocorrelation.join_counts_local(values, weights, permutations=0)
        self.assertEqual(len(join_local.p_sim), 4)

    @unittest.skipUnless(
        autocorrelation.PYSAL_AVAILABLE and LIBPYSAL_AVAILABLE,
        "PySAL not available",
    )
    def test_moran_rate(self):
        events = [1, 2, 3, 4]
        population = [10, 10, 10, 10]
        weights = libpysal.weights.lat2W(2, 2)
        weights.transform = "r"

        global_rate, local_rate = autocorrelation.moran_rate(
            events,
            population,
            weights,
            permutations=0,
        )
        self.assertTrue(hasattr(global_rate, "I"))
        self.assertEqual(len(local_rate.Is), 4)
