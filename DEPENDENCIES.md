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

- **Shapely** 2.1.2 or newer
  - Required by libpysal for geometric operations
  - **⚠️ macOS**: QGIS bundles Shapely 2.0.6 which is incompatible - installation script automatically installs 2.1.2 to profile directory
  - Install via: `pip install "shapely>=2.1.2"`

- **Fiona** 1.9.0 or newer
  - Required by GeoPandas for reading/writing geospatial file formats
  - Provides engine for GeoPackage (.gpkg) file support
  - Install via: `pip install fiona`

- **GeoPandas** 0.14.0 or newer
  - Required for GeoPackage (.gpkg) file support in autocorrelation analysis
  - Enables modern spatial weights calculation from non-shapefile formats
  - Falls back to legacy shapefile-only approach if not installed
  - Install via: `pip install geopandas`

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

**RECOMMENDED: Use QGIS Python Console** (most reliable - impossible to use wrong Python)

**Mental model:** The QGIS Python Console runs **Python only**. Terminal commands (anything starting with `/Applications/...` or `QGIS_PYTHON=...`) must be run in Terminal, not in the console.

**Option 1 - QGIS Console Script (Easiest):**

1. Open QGIS → Plugins → Python Console
2. Click "Show Editor" → "Open Script"
3. Select `install_dependencies_console.py` (get it using one of these):
   - Download the GeoPublicHealth repository (ZIP or git clone) and **unzip** it. The script is inside the folder.
   - Or download the script directly: https://raw.githubusercontent.com/ePublicHealth/GeoPublicHealth/refs/heads/main/install_dependencies_console.py
     - Save the file locally as `install_dependencies_console.py` (recommended location: `~/Downloads/`).
   - Or open the link, copy the full script, paste it into the QGIS Python editor, and save it as `install_dependencies_console.py`.
4. Click "Run Script"
5. **🧾 Logs:** Saved to `~/GeoPublicHealth/` (fallback: `/tmp/`)

**Option 2 - Manual Verification (After Automated Script):**

⚠️ **Don't use manual `subprocess.run()` commands** - they don't handle macOS-specific issues (Shapely version conflict, NumPy 2.x compatibility, missing bin directories).

After running the automated script (Option 1), verify the installation:

1. **🔄 Restart QGIS first** (required for new packages to load)
2. Run this verification script in QGIS Python Console:

```python
import sys
import libpysal, esda, numba, shapely, geopandas, fiona

print(f"Python: {sys.executable}")
print("(Should contain 'QGIS.app')\n")
print("✓ All dependencies installed!")
print(f"  libpysal {libpysal.__version__}")
print(f"  esda {esda.__version__}")
print(f"  numba {numba.__version__}")
print(f"  shapely {shapely.__version__} (should be 2.1.2+)")
print(f"  geopandas {geopandas.__version__}")
print(f"  fiona {fiona.__version__}")

# Critical checks
if shapely.__version__.startswith('2.0'):
    print("\n⚠️  ERROR: Shapely is 2.0.x (bundled version)")
    print("Run install_dependencies_console.py to fix")
elif shapely.__version__ >= '2.1.2':
    print("\n✓ Shapely version is correct!")

# Test GeoPackage support
try:
    import geopandas as gpd
    print("\n✓ GeoPackage (.gpkg) support available!")
except ImportError:
    print("\n⚠️  WARNING: GeoPandas not available - GeoPackage support disabled")
```

**Why manual commands don't work on macOS:**
- QGIS bundles Shapely 2.0.6, but libpysal needs 2.1.2+ (API incompatibility)
- Simple `pip install` doesn't override bundled version (wrong sys.path order)
- Must install to profile directory with `--target` flag
- Must use `--no-deps` for numba to avoid NumPy 2.x upgrade
- Automated script handles all these issues correctly

**Alternative: Terminal Methods** (advanced users only)

⚠️ **NOT RECOMMENDED** - Terminal methods don't handle macOS-specific issues correctly. Use the QGIS Console script instead (Option 1).

**⚠️ These commands are for Terminal, not the QGIS Python Console.** If you paste them into the console, they will fail.

**Why Terminal methods fail:**
- Don't handle Shapely 2.0.6 → 2.1.2 upgrade (bundled version conflict)
- May install NumPy 2.x which breaks QGIS
- Don't create missing `/Applications/QGIS.app/Contents/bin` directory
- No proper error handling or logging

**If you must use Terminal**, see [MAC_INSTALL_TECHNICAL.md](MAC_INSTALL_TECHNICAL.md) for the correct `--target` + `--no-deps` pattern. But the automated console script is **strongly recommended**.

### Linux

```bash
# Using system QGIS Python (path may vary by distribution)
python3 -m pip install --user libpysal numba matplotlib
```

## Checking Installed Dependencies

**🔄 Restart QGIS first** before checking (QGIS only loads packages at startup).

You can check which dependencies are installed by running this in the QGIS Python console:

```python
import sys

# Check required dependencies with versions
required = [
    ('libpysal', '4.12.0'),
    ('esda', '2.6.0'),
    ('numpy', '1.18.0'),
    ('numba', '0.50.0'),
    ('shapely', '2.1.2'),
    ('fiona', '1.9.0'),
    ('geopandas', '0.14.0'),
    ('gdal', '3.0.0'),
]
optional = [('matplotlib', '3.0.0')]

print("Required dependencies:")
for package, min_ver in required:
    try:
        mod = __import__(package)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✓ {package} {version}", end='')
        
        # Special checks
        if package == 'shapely':
            if version.startswith('2.0'):
                print(" ⚠️  WARNING: Using bundled 2.0.x - need 2.1.2+ (run install script)")
            elif version >= min_ver:
                print(" (OK)")
            else:
                print(f" ⚠️  WARNING: Need >={min_ver}")
        elif package == 'numpy':
            if version.startswith('2.'):
                print(" ⚠️  ERROR: NumPy 2.x breaks QGIS - need 1.26.x")
            else:
                print(" (OK)")
        else:
            print()
    except ImportError:
        print(f"✗ {package} NOT installed (REQUIRED: >={min_ver})")

print("\nOptional dependencies:")
for package, min_ver in optional:
    try:
        mod = __import__(package)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✓ {package} {version}")
    except ImportError:
        print(f"○ {package} NOT installed (optional - graphing features disabled)")
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
| Python | 3.x | 3.11-3.12 | Bundled with QGIS |
| GDAL | 3.0 | 3.10.2+ | Usually bundled |
| NumPy | 1.18 | 1.26.4 | **Must stay at 1.x** - NumPy 2.x breaks QGIS |
| Shapely | 2.1.2 | 2.1.2+ | **macOS**: QGIS bundles 2.0.6 (incompatible) |
| Fiona | 1.9 | 1.9.0+ | Required for GeoPackage support |
| GeoPandas | 0.14 | 0.14.0+ | Required for GeoPackage support |
| libpysal | 4.0 | 4.12.0+ | Install separately |
| esda | 2.0 | 2.6.0+ | Install separately |
| numba | 0.50 | 0.60.0+ | Install separately |
| scipy | 1.5 | Latest | Install separately |
| pandas | 1.0 | Latest | Install separately |
| matplotlib | 3.0 | Latest | Optional (for plotting features) |

**Critical Notes:**
- **NumPy**: Must not upgrade to 2.x - QGIS's bundled modules (GDAL, PyQt5) are compiled against NumPy 1.x ABI
- **Shapely (macOS)**: QGIS 3.42-3.44 bundles 2.0.6, but libpysal requires 2.1.2+ (API breaking changes). Automated script installs 2.1.2 to profile directory to override bundled version.
- **GeoPackage Support**: Requires both Fiona and GeoPandas. Without these, the plugin will fall back to shapefile-only mode for autocorrelation analysis. GeoPackage (.gpkg) is the recommended modern format for geospatial data.

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
