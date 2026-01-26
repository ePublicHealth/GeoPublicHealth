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

from typing import Callable, List, Optional, Tuple

from geopublichealth.src.core.stats import Stats

try:
    from qgis.core import QgsFeatureRequest, QgsSpatialIndex
except ImportError:
    QgsFeatureRequest = None
    QgsSpatialIndex = None


ProgressCallback = Optional[Callable[[int, int], None]]


def build_spatial_index(
    stats_layer,
    progress_callback: ProgressCallback = None,
    use_fast: bool = False,
):
    if QgsSpatialIndex is None:
        raise ImportError("QGIS core is required to build spatial index")

    if use_fast:
        return QgsSpatialIndex(stats_layer.getFeatures())

    features = stats_layer.getFeatures()
    index = QgsSpatialIndex()
    total = stats_layer.featureCount()

    for i, feature in enumerate(features):
        index.insertFeature(feature)
        if progress_callback:
            progress_callback(i + 1, total)

    return index


def compute_intersection_counts(
    blurred_layer,
    stats_layer,
    index,
    progress_callback: ProgressCallback = None,
) -> List[int]:
    if QgsFeatureRequest is None:
        raise ImportError("QGIS core is required to compute intersections")

    counts = []
    total = blurred_layer.featureCount()

    for i, feature in enumerate(blurred_layer.getFeatures()):
        count = 0
        ids = index.intersects(feature.geometry().boundingBox())
        for unique_id in ids:
            request = QgsFeatureRequest().setFilterFid(unique_id)
            f = next(stats_layer.getFeatures(request))
            if f.geometry().intersects(feature.geometry()):
                count += 1
        counts.append(count)

        if progress_callback:
            progress_callback(i + 1, total)

    return counts


def build_stats_items(
    counts: List[int],
    nb_feature_blurred: int,
    nb_feature_stats: int,
) -> List[Tuple[str, str]]:
    stats = Stats(counts)
    return [
        ("Count(blurred)", str(nb_feature_blurred)),
        ("Count(stats)", str(nb_feature_stats)),
        ("Min", str(stats.min())),
        ("Average", "%.6f" % stats.average()),
        ("Max", str(stats.max())),
        ("Median", "%.6f" % stats.median()),
        ("Range", str(stats.range())),
        ("Variance", "%.6f" % stats.variance()),
        ("Standard deviation", "%.6f" % stats.standard_deviation()),
    ]
