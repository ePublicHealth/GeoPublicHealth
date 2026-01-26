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

try:
    import libpysal
    from esda.moran import (
        Moran,
        Moran_BV,
        Moran_Local,
        Moran_Local_BV,
        Moran_Rate,
        Moran_Local_Rate,
    )
    from esda.getisord import G_Local
    from esda.geary_local import Geary_Local
    from esda.join_counts import Join_Counts
    from esda.join_counts_local import Join_Counts_Local

    PYSAL_AVAILABLE = True
except ImportError:
    PYSAL_AVAILABLE = False


def local_moran(
    values: Iterable[float],
    neighbors: Dict[int, Iterable[int]],
    permutations: int = 0,
) -> Dict[str, Optional[list]]:
    """Compute Local Moran's I using a neighbor dictionary."""
    if not PYSAL_AVAILABLE:
        raise ImportError("PySAL (libpysal/esda) is not available.")
    if not isinstance(neighbors, dict) or not neighbors:
        raise ValueError("Neighbors must be a non-empty dict.")
    if not any(neighbors.values()):
        raise ValueError("Neighbors must include at least one connection.")

    weights = libpysal.weights.W(neighbors)
    weights.transform = "r"

    local = Moran_Local(list(values), weights, permutations=permutations)
    p_values = local.p_sim.tolist() if permutations else None

    return {
        "local_stat": local.Is.tolist(),
        "p_values": p_values,
    }


def moran_local(values, weights, permutations: int = 999, transformation: str = "r"):
    if not PYSAL_AVAILABLE:
        raise ImportError("PySAL (libpysal/esda) is not available.")
    return Moran_Local(
        values, weights, transformation=transformation, permutations=permutations
    )


def moran_global(values, weights, permutations: int = 999, transformation: str = "r"):
    if not PYSAL_AVAILABLE:
        raise ImportError("PySAL (libpysal/esda) is not available.")
    return Moran(
        values, weights, transformation=transformation, permutations=permutations
    )


def moran_bv_global(x, y, weights, permutations: int = 999, transformation: str = "r"):
    if not PYSAL_AVAILABLE:
        raise ImportError("PySAL (libpysal/esda) is not available.")
    return Moran_BV(
        x, y, weights, transformation=transformation, permutations=permutations
    )


def moran_bv_local(x, y, weights, permutations: int = 999, transformation: str = "r"):
    if not PYSAL_AVAILABLE:
        raise ImportError("PySAL (libpysal/esda) is not available.")
    return Moran_Local_BV(
        x, y, weights, transformation=transformation, permutations=permutations
    )


def join_counts_global(values, weights, permutations: int = 999):
    if not PYSAL_AVAILABLE:
        raise ImportError("PySAL (libpysal/esda) is not available.")
    return Join_Counts(values, weights, permutations=permutations)


def join_counts_local(values, weights, permutations: int = 999, n_jobs: int = 1):
    if not PYSAL_AVAILABLE:
        raise ImportError("PySAL (libpysal/esda) is not available.")
    return Join_Counts_Local(
        connectivity=weights,
        permutations=permutations,
        n_jobs=n_jobs,
        keep_simulations=False,
    ).fit(values)


def geary_local(values, weights, permutations: int = 999, n_jobs: int = 1):
    if not PYSAL_AVAILABLE:
        raise ImportError("PySAL (libpysal/esda) is not available.")
    return Geary_Local(
        connectivity=weights,
        permutations=permutations,
        n_jobs=n_jobs,
        keep_simulations=False,
    ).fit(values)


def g_local(values, weights, permutations: int = 999, n_jobs: int = 1):
    if not PYSAL_AVAILABLE:
        raise ImportError("PySAL (libpysal/esda) is not available.")
    return G_Local(
        values,
        weights,
        transform="R",
        permutations=permutations,
        n_jobs=n_jobs,
        keep_simulations=False,
    )


def moran_rate(
    events,
    population,
    weights,
    permutations: int = 999,
) -> Tuple[object, object]:
    if not PYSAL_AVAILABLE:
        raise ImportError("PySAL (libpysal/esda) is not available.")
    global_rate = Moran_Rate(events, population, weights, permutations=permutations)
    local_rate = Moran_Local_Rate(
        events, population, weights, permutations=permutations
    )
    return global_rate, local_rate
