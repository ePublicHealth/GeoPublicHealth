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

from typing import Dict, Iterable, Optional, Tuple

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    try:
        from geopublichealth.src.core.stats import Stats
    except ImportError:
        from src.core.stats import Stats


def sanitize_value(value) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_indicator_stats(
    values_by_indicator: Dict[str, Iterable],
) -> Dict[str, "Stats"]:
    try:
        from geopublichealth.src.core.stats import Stats
    except ImportError:
        from src.core.stats import Stats

    stats = {}
    for name, values in values_by_indicator.items():
        sanitized = [
            val
            for val in (sanitize_value(value) for value in values)
            if val is not None
        ]
        stats[name] = Stats(sanitized)
    return stats


def compute_zscore(value: Optional[float], stats: "Stats") -> float:
    if value is None:
        return 0.0
    std_dev = stats.standard_deviation()
    if std_dev <= 0:
        return 0.0
    return (value - stats.average()) / std_dev


def compute_composite_index_values(
    feature_values: Dict[str, Optional[float]],
    indicator_directions: Dict[str, str],
    stats_by_indicator: Dict[str, "Stats"],
) -> Tuple[Dict[str, float], float]:
    zscores = {}
    composite = 0.0

    for name, value in feature_values.items():
        stats = stats_by_indicator.get(name)
        if stats is None:
            zscores[name] = 0.0
            continue

        zscore = compute_zscore(value, stats)
        direction = indicator_directions.get(name, "-")
        component = -zscore if direction == "+" else zscore
        zscores[name] = zscore
        composite += component

    return zscores, composite
