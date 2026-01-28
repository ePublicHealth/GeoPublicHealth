# Future Directions for GeoPublicHealth

This document captures potential future directions for the GeoPublicHealth QGIS plugin. It is intended for discussion, prioritization, and roadmap planning.

Each item is described using:

- WHY: The public health or user value.
- WHAT: The capability or feature scope.
- HOW: A practical implementation approach aligned with current architecture.

## References

- PySAL ESDA: https://pysal.org/esda/
- PySAL Giddy: https://pysal.org/giddy/
- PySAL Segregation: https://pysal.org/segregation/
- PySAL Spaghetti: https://pysal.org/spaghetti/
- GeoDa capabilities overview: https://geodacenter.github.io/
- QGIS Processing algorithms: https://docs.qgis.org/3.40/en/docs/user_manual/processing_algs/qgis/index.html
- QGIS temporal controller and animation: https://docs.qgis.org/3.40/en/docs/user_manual/map_views/map_view.html
- SaTScan (Kulldorff scan statistics): https://www.satscan.org/

## Autocorrelation and ESDA expansion

WHY: Broaden the analytical coverage beyond current Moran/Geary/Gi tools and support richer exploratory spatial data analysis used in epidemiology.

WHAT: Add LOSH, correlograms, multivariable Moran, local join counts, and diagnostic measures like geosilhouettes and boundary strength summaries.

HOW: Implement new analysis logic in `src/core/services/` using PySAL ESDA and surface results in the existing autocorrelation dialog and processing algorithms.

## Spatiotemporal dynamics and surveillance

WHY: Support longitudinal disease monitoring and change detection for surveillance workflows.

WHAT: Directional LISA, spatial Markov transitions, and temporal mobility summaries with map outputs and optional charts.

HOW: Use PySAL Giddy for computation, expose time-enabled layers in UI, and connect to QGIS temporal controller for animation export.

## Inequality and segregation analytics

WHY: Quantify and map health inequities across populations and geographies.

WHAT: Multigroup and local segregation indices, inference tests, and optional network-based variants for access inequities.

HOW: Use PySAL Segregation in a dedicated service, add new dialogs and Processing tools that output index fields and summary reports.

## Spatially constrained clustering

WHY: Identify coherent health regions and clusters while respecting spatial contiguity and administrative boundaries.

WHAT: Implement SKATER, REDCAP, Max-P, and spectral clustering; keep k-means and DBSCAN with public health presets.

HOW: Use GeoDa-style algorithms where available in PySAL or reimplement in `src/core/services/`; add clustering outputs as new layers and reports.

## Kulldorff spatial scan statistics

WHY: Detect statistically significant disease clusters in space, time, and space-time.

WHAT: Integrate a scan statistics workflow for Poisson, Bernoulli, and space-time permutation models.

HOW: Wrap SaTScan or a compatible open-source implementation; add a data preparation wizard, run engine externally, and import results as layers.

## Health services accessibility and coverage

WHY: Measure access gaps, service deserts, and spatial equity in healthcare provision.

WHAT: Service areas, catchments, travel-time thresholds, and facility location options, plus equity overlays.

HOW: Use QGIS network algorithms for routing/service areas and extend with PySAL Spaghetti for network-based metrics; integrate in services and dialogs.

## Visualization and communication

WHY: Improve interpretation and communication of results for public health stakeholders.

WHAT: Small multiples for time steps, narrative map templates, and automated spatiotemporal animations for surveillance reporting.

HOW: Provide layout presets and scripts that drive QGIS temporal controller and atlas export; offer standardized symbology for common metrics.

## Processing parity and automation

WHY: Ensure reproducibility and batch processing for large workflows.

WHAT: Full parity between GUI tools and QGIS Processing algorithms, including standardized output schemas.

HOW: Centralize logic in `src/core/services/` and wrap each service in both GUI dialogs and Processing algorithms.

## Testing and documentation

WHY: Keep analytics trustworthy and maintainable as feature surface grows.

WHAT: Unit tests for new metrics, regression tests for bugs, and concise user-facing docs.

HOW: Add tests under `src/test/` following existing patterns, keep test data small, and update docs in `docs/` and `README.md` as needed.

## Prioritization (for discussion)

Short term (high value, low integration risk):

- Spatiotemporal dynamics and surveillance (issue #16)
- Inequality and segregation analytics (issue #17)

Mid term (moderate integration effort, high impact):

- Spatially constrained clustering (issue #19)
- Health services accessibility and coverage (issue #20)
- Visualization and communication (issue #21)

Longer term (external dependencies, heavier workflows):

- Kulldorff spatial scan statistics (issue #18)
- Processing parity and automation

## Issue backlog (proposed)

- https://github.com/ePublicHealth/GeoPublicHealth/issues/16
- https://github.com/ePublicHealth/GeoPublicHealth/issues/17
- https://github.com/ePublicHealth/GeoPublicHealth/issues/18
- https://github.com/ePublicHealth/GeoPublicHealth/issues/19
- https://github.com/ePublicHealth/GeoPublicHealth/issues/20
- https://github.com/ePublicHealth/GeoPublicHealth/issues/21
