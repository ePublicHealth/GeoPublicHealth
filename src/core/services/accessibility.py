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

from typing import Callable, Iterable, List, Optional


def nearest_facility(
    origins: Iterable,
    facilities: Iterable,
    cost_func: Callable,
) -> List[Optional[float]]:
    """Compute nearest facility cost for each origin."""
    origins_list = list(origins)
    facilities_list = list(facilities)

    if not facilities_list:
        return [None for _ in origins_list]

    results = []
    for origin in origins_list:
        costs = [cost_func(origin, facility) for facility in facilities_list]
        costs = [cost for cost in costs if cost is not None]
        results.append(min(costs) if costs else None)
    return results


def two_step_fca(
    demand: Iterable[float],
    supply: Iterable[float],
    origins: Iterable,
    facilities: Iterable,
    cost_func: Callable,
    catchment: Optional[float] = None,
) -> List[Optional[float]]:
    """Compute Two-Step Floating Catchment Area (2SFCA) accessibility."""
    demand_list = list(demand)
    supply_list = list(supply)
    origins_list = list(origins)
    facilities_list = list(facilities)

    if len(demand_list) != len(origins_list):
        raise ValueError("Demand and origins lengths must match.")
    if len(supply_list) != len(facilities_list):
        raise ValueError("Supply and facilities lengths must match.")

    facility_ratios = []
    for facility, facility_supply in zip(facilities_list, supply_list):
        eligible_demand = 0.0
        for origin, origin_demand in zip(origins_list, demand_list):
            cost = cost_func(origin, facility)
            if cost is None:
                continue
            if catchment is None or cost <= catchment:
                eligible_demand += origin_demand
        if eligible_demand > 0:
            facility_ratios.append(facility_supply / eligible_demand)
        else:
            facility_ratios.append(None)

    accessibility = []
    for origin in origins_list:
        score = 0.0
        has_ratio = False
        for facility, ratio in zip(facilities_list, facility_ratios):
            if ratio is None:
                continue
            cost = cost_func(origin, facility)
            if cost is None:
                continue
            if catchment is None or cost <= catchment:
                score += ratio
                has_ratio = True
        accessibility.append(score if has_ratio else None)

    return accessibility
