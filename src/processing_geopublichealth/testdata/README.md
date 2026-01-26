# Processing algorithm tests

This directory is reserved for QGIS Processing algorithm tests.

Use the QGIS Processing testing workflow to create YAML definitions and
expected outputs. Start by running an algorithm in QGIS, then use the
Processing History to generate a test definition and copy it into
`algorithm_tests.yaml`.

Current test definitions expect output files that must be generated with QGIS.
For example, `blurring_radius_zero` expects:

- `expected/blur_radius0.gpkg`

To generate it:

1) Run the `geopublichealth:blurring` algorithm in QGIS with:
   - INPUT_LAYER: `geohealth_sample_data_en/fictional_cases.shp`
   - RADIUS_FIELD: 0.01 (layer is in WGS84 degrees)
   - RADIUS_EXPORT: false
   - CENTROID_EXPORT: false
   - ENVELOPE_LAYER: (empty)
   - RANDOM_SEED: 42 (ensures deterministic output)
2) Save the output as `expected/blur_radius0.gpkg`.

References:
- https://docs.qgis.org/3.40/en/docs/developers_guide/processingtesting.html
