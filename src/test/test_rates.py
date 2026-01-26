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

from src.core.services import rates

try:
    import numpy

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class TestRates(unittest.TestCase):
    def test_incidence_basic(self):
        result = rates.compute_incidence([10, 20, 0], [1000, 2000, 1000], 100000)
        self.assertEqual(result, [1000.0, 1000.0, 0.0])

    def test_density_basic(self):
        result = rates.compute_density([10, 20], [2.0, 4.0], 1)
        self.assertEqual(result, [5.0, 5.0])

    def test_incidence_zero_population(self):
        result = rates.compute_incidence([5], [0], 100000)
        self.assertEqual(result, [None])

    def test_incidence_handles_none(self):
        result = rates.compute_incidence([None, 10], [1000, None], 100000)
        self.assertEqual(result, [None, None])

    @unittest.skipUnless(NUMPY_AVAILABLE, "numpy not available")
    def test_rate_summary_stats_population(self):
        summary = rates.summarize_rates([1.0, 2.0, 3.0], sample_variance=False)
        self.assertEqual(summary["count"], 3)
        self.assertAlmostEqual(summary["mean"], 2.0, places=6)
        self.assertAlmostEqual(summary["median"], 2.0, places=6)
        self.assertAlmostEqual(summary["variance"], 0.6666667, places=6)
        self.assertAlmostEqual(summary["std_dev"], 0.8164966, places=6)
