# Processing algorithm tests

This directory is reserved for QGIS Processing algorithm tests.

Use the QGIS Processing testing workflow to create YAML definitions and
expected outputs. Start by running an algorithm in QGIS, then use the
Processing History to generate a test definition and copy it into
`algorithm_tests.yaml`.

Current test definitions expect output files that must be generated with QGIS.
For example, `blurring_radius_001` expects:

- `expected/blur_radius001.gpkg`

To generate it:

1) Run the `geopublichealth:blurring` algorithm in QGIS with:
   - Point layer: `geohealth_sample_data_en/fictional_cases.shp`
   - Radius (map's unit): 0.01 (layer is in WGS84 degrees)
   - Use only selected features: unchecked
   - Add result to canvas: optional
   - Add to the attribute table: unchecked
     - the radius: unchecked
     - X and Y of centroid: unchecked
   - Use envelope: unchecked
   - Random seed (optional): 42 (ensures deterministic output)
2) Save the output as `expected/blur_radius001.gpkg`.

Notes:
- The radius is in layer units; this sample is WGS84 (degrees).
- If no output is produced, pick a non-zero radius and ensure the output path
  is writable.

References:
- https://docs.qgis.org/3.40/en/docs/developers_guide/processingtesting.html
