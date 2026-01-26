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

from src.core.services import inequality


class TestInequality(unittest.TestCase):
    def test_gini_simple(self):
        result = inequality.gini([1, 2, 3, 4, 5])
        self.assertAlmostEqual(result, 0.2666667, places=6)

    def test_theil_simple(self):
        result = inequality.theil([1, 1, 1, 1])
        self.assertEqual(result, 0.0)

    def test_atkinson_simple(self):
        result = inequality.atkinson([10, 10, 10, 10], epsilon=0.5)
        self.assertAlmostEqual(result, 0.0, places=6)

    def test_palma_ratio(self):
        result = inequality.palma_ratio([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(result, 1.0)

    def test_ratio_p90_p10(self):
        result = inequality.ratio_p90_p10(list(range(1, 101)))
        self.assertAlmostEqual(result, 9.0, places=6)

    def test_negative_values_error(self):
        with self.assertRaises(ValueError):
            inequality.gini([1, -1, 2])
