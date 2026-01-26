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

from src.core.services import composite_index

try:
    import numpy

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class TestCompositeIndex(unittest.TestCase):
    def test_sanitize_value(self):
        self.assertEqual(composite_index.sanitize_value("3.5"), 3.5)
        self.assertIsNone(composite_index.sanitize_value(None))
        self.assertIsNone(composite_index.sanitize_value("bad"))

    @unittest.skipUnless(NUMPY_AVAILABLE, "numpy not available")
    def test_compute_composite_index_values(self):
        values_by_indicator = {
            "A": [1.0, 2.0, 3.0],
            "B": [2.0, 2.0, 2.0],
        }
        stats = composite_index.build_indicator_stats(values_by_indicator)
        feature_values = {"A": 3.0, "B": 2.0}
        directions = {"A": "+", "B": "-"}

        zscores, composite = composite_index.compute_composite_index_values(
            feature_values,
            directions,
            stats,
        )

        self.assertAlmostEqual(zscores["A"], 1.2247449, places=6)
        self.assertAlmostEqual(zscores["B"], 0.0, places=6)
        self.assertAlmostEqual(composite, -1.2247449, places=6)
