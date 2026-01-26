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

from typing import Iterable, List, Optional, Dict


def _as_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _validate_series(series: Iterable) -> List[Optional[float]]:
    return [_as_float(value) for value in series]


def _compute_rate(
    numerator: Iterable,
    denominator: Iterable,
    ratio: float,
) -> List[Optional[float]]:
    num_values = _validate_series(numerator)
    den_values = _validate_series(denominator)

    if len(num_values) != len(den_values):
        raise ValueError("Numerator and denominator lengths must match.")

    results = []
    for num, den in zip(num_values, den_values):
        if num is None or den is None:
            results.append(None)
            continue
        if den <= 0 or num < 0:
            results.append(None)
            continue
        results.append((num / den) * ratio)

    return results


def compute_incidence(
    cases: Iterable,
    population: Iterable,
    ratio: float = 1.0,
) -> List[Optional[float]]:
    """Compute incidence rates.

    :param cases: Case counts per unit.
    :type cases: Iterable

    :param population: Population counts per unit.
    :type population: Iterable

    :param ratio: Scaling ratio (e.g., 100000).
    :type ratio: float

    :return: Incidence values or None when invalid.
    :rtype: List[Optional[float]]
    """
    return _compute_rate(cases, population, ratio)


def compute_density(
    cases: Iterable,
    area: Iterable,
    ratio: float = 1.0,
) -> List[Optional[float]]:
    """Compute density rates.

    :param cases: Case counts per unit.
    :type cases: Iterable

    :param area: Area values per unit.
    :type area: Iterable

    :param ratio: Scaling ratio.
    :type ratio: float

    :return: Density values or None when invalid.
    :rtype: List[Optional[float]]
    """
    return _compute_rate(cases, area, ratio)


def summarize_rates(
    values: Iterable,
    sample_variance: bool = False,
) -> Dict[str, Optional[float]]:
    """Summarize rate values.

    :param values: Rate values (None ignored).
    :type values: Iterable

    :param sample_variance: Use sample variance (ddof=1) if True.
    :type sample_variance: bool

    :return: Summary statistics.
    :rtype: Dict[str, Optional[float]]
    """
    valid_values = [value for value in _validate_series(values) if value is not None]

    if not valid_values:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "variance": None,
            "std_dev": None,
        }

    try:
        import numpy as np
    except ImportError as exc:
        raise ImportError("numpy is required for rate summaries") from exc

    ddof = 1 if sample_variance else 0
    if ddof == 1 and len(valid_values) < 2:
        variance = None
        std_dev = None
    else:
        variance = float(np.var(valid_values, ddof=ddof))
        std_dev = float(np.std(valid_values, ddof=ddof))

    return {
        "count": len(valid_values),
        "mean": float(np.mean(valid_values)),
        "median": float(np.median(valid_values)),
        "variance": variance,
        "std_dev": std_dev,
    }
