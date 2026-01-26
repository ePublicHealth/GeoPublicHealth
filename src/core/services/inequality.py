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

from math import exp, log, ceil
from typing import Iterable, List, Optional


def _validate_non_negative(values: Iterable) -> List[float]:
    cleaned = []
    for value in values:
        if value is None:
            raise ValueError("Values must not contain None.")
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            raise ValueError("Values must be numeric.")
        if numeric < 0:
            raise ValueError("Values must be non-negative.")
        cleaned.append(numeric)
    return cleaned


def _nearest_rank_percentile(values: List[float], percentile: float) -> float:
    if not values:
        raise ValueError("Values must not be empty.")
    if percentile <= 0 or percentile > 100:
        raise ValueError("Percentile must be in (0, 100].")
    sorted_values = sorted(values)
    rank = int(ceil((percentile / 100.0) * len(sorted_values)))
    rank = max(1, min(rank, len(sorted_values)))
    return float(sorted_values[rank - 1])


def gini(values: Iterable) -> float:
    """Compute the Gini coefficient."""
    cleaned = _validate_non_negative(values)
    if not cleaned:
        raise ValueError("Values must not be empty.")
    total = sum(cleaned)
    if total == 0:
        return 0.0
    sorted_values = sorted(cleaned)
    n = len(sorted_values)
    weighted_sum = sum((index + 1) * value for index, value in enumerate(sorted_values))
    return (2.0 * weighted_sum) / (n * total) - (n + 1.0) / n


def theil(values: Iterable) -> float:
    """Compute the Theil index."""
    cleaned = _validate_non_negative(values)
    if not cleaned:
        raise ValueError("Values must not be empty.")
    total = sum(cleaned)
    if total == 0:
        return 0.0
    mean = total / len(cleaned)
    terms = []
    for value in cleaned:
        if value == 0:
            terms.append(0.0)
        else:
            ratio = value / mean
            terms.append(ratio * log(ratio))
    return sum(terms) / len(cleaned)


def atkinson(values: Iterable, epsilon: float = 0.5) -> float:
    """Compute the Atkinson index."""
    cleaned = _validate_non_negative(values)
    if not cleaned:
        raise ValueError("Values must not be empty.")
    if epsilon < 0:
        raise ValueError("Epsilon must be non-negative.")
    total = sum(cleaned)
    if total == 0:
        return 0.0
    mean = total / len(cleaned)

    if epsilon == 1:
        if any(value <= 0 for value in cleaned):
            raise ValueError("Values must be positive when epsilon is 1.")
        mean_log = sum(log(value) for value in cleaned) / len(cleaned)
        return 1.0 - exp(mean_log) / mean

    exponent = 1.0 - epsilon
    mean_power = sum(value**exponent for value in cleaned) / len(cleaned)
    return 1.0 - (mean_power ** (1.0 / exponent)) / mean


def palma_ratio(values: Iterable) -> Optional[float]:
    """Compute the Palma ratio (top 10% / bottom 40%)."""
    cleaned = _validate_non_negative(values)
    if not cleaned:
        raise ValueError("Values must not be empty.")
    sorted_values = sorted(cleaned)
    n = len(sorted_values)
    top_count = max(1, int(ceil(0.10 * n)))
    bottom_count = max(1, int(ceil(0.40 * n)))
    top_sum = sum(sorted_values[-top_count:])
    bottom_sum = sum(sorted_values[:bottom_count])
    if bottom_sum == 0:
        return None
    return top_sum / bottom_sum


def ratio_p90_p10(values: Iterable) -> Optional[float]:
    """Compute the p90/p10 ratio using nearest-rank percentiles."""
    cleaned = _validate_non_negative(values)
    if not cleaned:
        raise ValueError("Values must not be empty.")
    p90 = _nearest_rank_percentile(cleaned, 90)
    p10 = _nearest_rank_percentile(cleaned, 10)
    if p10 == 0:
        return None
    return p90 / p10
