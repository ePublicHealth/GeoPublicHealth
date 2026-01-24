# GeoPublicHealth Dependencies

This document describes the dependencies required for the GeoPublicHealth QGIS plugin.

## Required Dependencies

These dependencies are **required** for the plugin to load and function:

### Python Standard Library
- Built-in with Python 3.x (included with QGIS)

### QGIS and PyQGIS
- **QGIS 3.0 or newer** (tested with 3.42.x - 3.44.x)
- PyQGIS libraries (automatically included with QGIS installation)
- PyQt5 (automatically included with QGIS installation)

### Geospatial Libraries
- **GDAL** ~3.10.2 or newer (usually bundled with QGIS)
  - Used for geospatial data reading/writing operations

### Spatial Analysis Libraries  
- **libpysal** ~4.3.0 or newer
  - Required for spatial statistics and analysis features
  - Install via: `pip install libpysal`

### Numerical Computing
- **NumPy** (latest compatible version)
  - Required for numerical operations
  - Usually included with QGIS, but can be installed via: `pip install numpy`

- **numba** (latest compatible version)
  - Required for performance optimization of spatial algorithms
  - Install via: `pip install numba`

## Optional Dependencies

These dependencies enable additional features but are **not required** for basic plugin functionality:

### Plotting and Visualization
- **matplotlib** (any recent version compatible with your Python version)
  - Enables graphing and plotting features in analysis dialogs
  - Features affected:
    - Statistics dialog histogram plotting
    - Composite index plots
    - Incidence/density plots
  - Install via: `pip install matplotlib`
  
**Note:** If matplotlib is not installed, the plugin will still load and work, but graphing features will be disabled with a warning message.

## Installing Dependencies

### Windows (OSGeo4W)

The recommended method is to use the OSGeo4W installer which handles most dependencies:

```cmd
# Open OSGeo4W Shell as Administrator
python3 -m pip install libpysal numba matplotlib
```

### macOS

**Option 1 - Automated Script (Recommended):**

Run `install_mac_dependencies.py` from QGIS Python Console (see README for details) or:

```bash
/Applications/QGIS.app/Contents/MacOS/bin/python3 install_mac_dependencies.py
```

**Option 2 - Shell Script:**

```bash
bash install_mac_dependencies.sh
```

**Option 3 - Single Command (All dependencies):**

```bash
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install numpy scipy pandas libpysal esda numba matplotlib --no-build-isolation
```

**Option 4 - Manual (Individual packages):**

```bash
# Using QGIS Python
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install numpy
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install scipy
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install pandas
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install libpysal esda --no-build-isolation
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install numba
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install matplotlib  # Optional
```

### Linux

```bash
# Using system QGIS Python (path may vary by distribution)
python3 -m pip install --user libpysal numba matplotlib
```

## Checking Installed Dependencies

You can check which dependencies are installed by running this in the QGIS Python console:

```python
import sys

# Check required dependencies
required = ['libpysal', 'numpy', 'numba', 'gdal']
optional = ['matplotlib']

for package in required:
    try:
        __import__(package)
        print(f"✓ {package} is installed")
    except ImportError:
        print(f"✗ {package} is NOT installed (REQUIRED)")

for package in optional:
    try:
        __import__(package)
        print(f"✓ {package} is installed")
    except ImportError:
        print(f"○ {package} is NOT installed (optional - graphing features disabled)")
```

## Troubleshooting

### libpysal Import Errors

If you see warnings about FutureWarning or ResourceWarning from libpysal, these can be safely ignored. The plugin includes filters to suppress these warnings.

### matplotlib Not Found

If matplotlib is not installed:
- The plugin will load successfully
- Basic functionality will work normally  
- Plotting/graphing features will be disabled
- You'll see a warning message when opening dialogs that use plotting
- To enable plotting features, install matplotlib using the instructions above

### GDAL Version Conflicts

If you experience GDAL-related errors:
1. Ensure you're using QGIS 3.42 or newer
2. Check your GDAL version: `python3 -c "import osgeo; print(osgeo.__version__)"`
3. GDAL 3.10.2 or newer is recommended

### NumPy/Numba Conflicts

If you experience numba errors:
1. Ensure NumPy is installed and up-to-date
2. Try reinstalling numba: `pip install --upgrade --force-reinstall numba`
3. Check compatibility: numba requires NumPy 1.18 or newer

## Version Compatibility

| Component | Minimum Version | Recommended Version | Notes |
|-----------|----------------|---------------------|-------|
| QGIS | 3.0 | 3.42.x - 3.44.x | Tested on 3.42-3.44 |
| Python | 3.x | 3.12.x | Bundled with QGIS |
| GDAL | 3.0 | 3.10.2+ | Usually bundled |
| libpysal | 4.0 | 4.3.0+ | Install separately |
| NumPy | 1.18 | Latest | Usually bundled |
| numba | 0.50 | Latest | Install separately |
| matplotlib | 3.0 | Latest | Optional |

## For Plugin Developers

If you're contributing to the plugin and need to add new dependencies:

1. **Required dependencies** should be added to this list and to the installation documentation
2. **Optional dependencies** should use the pattern in `src/core/optional_deps.py`:
   ```python
   try:
       import optional_module
       OPTIONAL_MODULE_AVAILABLE = True
   except ImportError:
       OPTIONAL_MODULE_AVAILABLE = False
       optional_module = None
   ```
3. Check the availability flag before using optional features
4. Provide graceful fallback behavior when optional dependencies are missing
5. Update this documentation with the new dependency information
