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

from src.core.services import accessibility


class TestAccessibility(unittest.TestCase):
    @staticmethod
    def cost_func(start, end):
        return abs(start - end)

    def test_nearest_facility(self):
        result = accessibility.nearest_facility([0, 5], [2, 10], self.cost_func)
        self.assertEqual(result, [2, 3])

    def test_two_step_fca_basic(self):
        demand = [100, 200]
        supply = [1, 1]
        origins = [0, 5]
        facilities = [2, 10]

        result = accessibility.two_step_fca(
            demand,
            supply,
            origins,
            facilities,
            self.cost_func,
            catchment=None,
        )

        self.assertEqual(len(result), 2)
        self.assertAlmostEqual(result[0], result[1], places=6)
