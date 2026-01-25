# macOS Installation - Technical Guide

This document provides detailed technical information about installing GeoPublicHealth dependencies on macOS, including Python environment management, troubleshooting, and advanced scenarios.

> **TL;DR - Best Practice:** Use QGIS Python Console to run installation commands. This eliminates all Python environment confusion and is the most reliable method. See [Method 1: QGIS Python Console](#method-1-qgis-python-console-recommended---most-reliable) below.

## Table of Contents

- [Understanding Python Environments](#understanding-python-environments)
- [QGIS Python Environment Details](#qgis-python-environment-details)
- [Installation Methods Explained](#installation-methods-explained)
- [Verifying Installation](#verifying-installation)
- [Troubleshooting](#troubleshooting)
- [Advanced Scenarios](#advanced-scenarios)

---

## Understanding Python Environments

### The Problem: Multiple Python Installations

macOS systems often have multiple Python installations:

1. **System Python** (`/usr/bin/python3`)
   - Built into macOS
   - Should not be modified (protected by System Integrity Protection)
   - Used by macOS system tools

2. **Homebrew Python** (`/opt/homebrew/bin/python3` on Apple Silicon, `/usr/local/bin/python3` on Intel)
   - Installed via `brew install python`
   - User-managed, can install packages freely
   - Common for developers

3. **Anaconda/Miniconda Python**
   - Typically in `~/anaconda3` or `~/miniconda3`
   - Environment-based package management
   - Popular for data science

4. **QGIS Python** (`/Applications/QGIS.app/Contents/MacOS/bin/python3`)
   - **Bundled with QGIS**
   - **Isolated from all other Python installations**
   - **This is where GeoPublicHealth dependencies MUST be installed**

### Why QGIS Has Its Own Python

QGIS bundles its own Python interpreter for several reasons:

- **Version Control**: Ensures compatible Python version for QGIS features
- **Dependency Isolation**: Avoids conflicts with system or user Python packages
- **Portability**: QGIS works regardless of what Python is installed on the system
- **Bundled Libraries**: Includes pre-compiled versions of GDAL, PyQt5, and other dependencies

### The Critical Point

**Installing packages to the wrong Python means QGIS won't find them.**

When you run `pip install libpysal`, it installs to whichever Python's pip you're using:
- `pip install libpysal` → installs to whatever `python3` is in your PATH (usually NOT QGIS)
- `/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install libpysal` → installs to QGIS Python ✓

---

## QGIS Python Environment Details

### Location

```
/Applications/QGIS.app/Contents/MacOS/python3.12
```

**Note:** The exact binary name depends on QGIS version:
- QGIS 3.44: `python3.12`
- QGIS 3.42: `python3.11`
- Older versions may use `bin/python3` symlink

### Version

QGIS typically bundles Python 3.9 - 3.12 depending on the QGIS version:
- QGIS 3.44: Python 3.12.x
- QGIS 3.42: Python 3.11.x

Check your version:
```bash
/Applications/QGIS.app/Contents/MacOS/python3.12 --version
# Or use the symlink if it exists:
/Applications/QGIS.app/Contents/MacOS/bin/python3 --version
```

### Pre-installed Packages

QGIS includes several packages by default:
- `PyQt5` - GUI framework
- `qgis` - PyQGIS libraries
- `numpy` - Often included, but may need upgrade
- `gdal` - Geospatial data abstraction library

### Site-packages Location

QGIS Python packages are installed to:
```
/Applications/QGIS.app/Contents/Resources/python/site-packages/
```

Or when using `--user` flag:
```
~/Library/Python/3.x/lib/python/site-packages/
```

Note: The exact paths may vary slightly between QGIS versions.

---

## Installation Methods Explained

### Method 1: QGIS Python Console (RECOMMENDED - Most Reliable)

**This is the recommended method for all users.**

**Advantages:**
- ✓ **Impossible to use wrong Python** - console is already running in QGIS's Python
- ✓ No Terminal knowledge required
- ✓ No need to know or type QGIS Python path
- ✓ Works even with restrictive permissions
- ✓ Simplest and most foolproof method
- ✓ Consistent across all macOS versions

**How it works:**
When you run code in QGIS Python Console, it uses QGIS's bundled Python interpreter automatically. We use `subprocess.run([sys.executable, "-m", "pip", ...])` to invoke pip, which is more stable than the deprecated `pip.main()` API.

**Two approaches:**

**A. Automated Script** (`install_dependencies_console.py`):
- Direct download link: https://raw.githubusercontent.com/ePublicHealth/GeoPublicHealth/refs/heads/main/install_dependencies_console.py
  - Save the file locally as `install_dependencies_console.py` (recommended location: `~/Downloads/`).
- Alternative: open the link, copy the full script, paste it into the QGIS Python editor, and save it as `install_dependencies_console.py`.
- Opens a script file in QGIS editor
- Click "Run Script"
- Handles all installations automatically using subprocess
- Reloads plugin repositories and installs GeoPublicHealth
- Creates timestamped log file
- Shows progress messages and verifies success

If the plugin is not installed after restarting QGIS, follow the manual fallback steps in `INSTALL_MAC.md`.

**B. Manual Commands:**

⚠️ **WARNING**: These simple commands don't handle all installation complexities (Shapely version conflicts, NumPy 2.x issues, Numba bin directory). **Use the automated script instead** (Option A above).

If you must use manual commands, here's the minimum approach (but it will likely fail due to version conflicts):
```python
import subprocess, sys

# This will fail - Shapely 2.0.6 bundled with QGIS conflicts with libpysal
subprocess.run([sys.executable, "-m", "pip", "install", "libpysal", "esda", "--no-build-isolation"])

# This may pull NumPy 2.x which breaks QGIS
subprocess.run([sys.executable, "-m", "pip", "install", "numba"])
```

**Why manual commands don't work:**
1. **Shapely conflict**: QGIS bundles Shapely 2.0.6, but libpysal needs 2.1.2+. Installing to framework site-packages doesn't override the bundled version.
2. **NumPy 2.x issue**: Installing numba without `--no-deps` pulls NumPy 2.x, breaking QGIS's bundled modules (compiled against NumPy 1.x).
3. **Missing bin directory**: Numba expects `/Applications/QGIS.app/Contents/bin` which doesn't exist by default.

**The automated script solves all these issues** by:
- Installing Shapely 2.1.2 to QGIS profile directory with `--target` (overrides bundled version)
- Installing Numba with `--no-deps` to avoid NumPy upgrade
- Creating missing bin directories
- Using proper subprocess streaming and error handling

**Important:** We use `subprocess` with `sys.executable -m pip` instead of the deprecated `pip.main()` API which can break with pip upgrades.

**Why this is better than Terminal:**
- No risk of typos in Python path
- No confusion about which `python3` command to use
- Works regardless of PATH environment variable
- No need to understand shell syntax

**Why `--no-build-isolation`?**
Some packages (like libpysal and esda) have build-time dependencies that need to be visible. The `--no-build-isolation` flag allows them to use already-installed packages during build, preventing errors.

---

### Understanding macOS-Specific Installation Challenges

**Critical Issues on macOS:**

1. **Shapely Version Conflict**
   - QGIS 3.42-3.44 bundles Shapely 2.0.6 in framework site-packages
   - libpysal requires Shapely 2.1.2+
   - Standard pip install to framework doesn't override bundled version (framework loads first in sys.path)
   - **Solution**: Install Shapely 2.1.2 to QGIS profile directory (`~/Library/Application Support/QGIS/QGIS3/profiles/default/python`)
   - Profile directory appears before framework in sys.path, so 2.1.2 loads instead of 2.0.6

2. **NumPy Compatibility Constraint**
   - QGIS bundles NumPy 1.26.4
   - QGIS's GDAL, PyQt5, and other bundled modules are compiled against NumPy 1.x ABI
   - NumPy 2.0+ has breaking ABI changes
   - Installing NumPy 2.x breaks QGIS's bundled modules with errors like: `RuntimeError: module compiled against API version 0x10 but this version of numpy is 0x11`
   - **Solution**: Use `--no-deps` when installing packages that depend on NumPy (like numba) to prevent automatic NumPy upgrade

3. **Numba Installation Issues**
   - Numba expects `/Applications/QGIS.app/Contents/bin` directory for binaries
   - This directory doesn't exist in default QGIS installation
   - pip install may fail or warn about missing script directory
   - **Solution**: Create the directory before installation, or install to profile directory with `--target`

**Correct Installation Pattern:**

```python
# Framework packages (safe to install normally)
subprocess.run([sys.executable, "-m", "pip", "install", "scipy", "pandas"])

# Shapely - MUST install to profile directory to override bundled 2.0.6
profile_python_dir = Path.home() / "Library/Application Support/QGIS/QGIS3/profiles/default/python"
subprocess.run([sys.executable, "-m", "pip", "install", "shapely>=2.1.2", 
                "--target", str(profile_python_dir), "--upgrade", "--no-deps"])

# Numba - MUST use --no-deps to avoid NumPy 2.x
subprocess.run([sys.executable, "-m", "pip", "install", "numba",
                "--target", str(profile_python_dir), "--no-deps"])

# libpysal/esda - can install normally after Shapely is correct version
subprocess.run([sys.executable, "-m", "pip", "install", "libpysal", "esda", "--no-build-isolation"])
```

**Why this pattern works:**
1. Profile directory is first in `sys.path`, so Shapely 2.1.2 overrides bundled 2.0.6
2. `--no-deps` prevents NumPy upgrade, keeping QGIS stable
3. `--target` avoids bin directory issues and permission problems
4. Framework packages can install normally without conflicts

---

### Method 2: Automated Python Script

**File:** `install_mac_dependencies.py`

**Advantages:**
- ✓ Installs all dependencies automatically
- ✓ CLI arguments for automation (`--yes`, `--timeout`, `--log`, `--python-path`)
- ✓ Full logging to timestamped file
- ✓ Shows progress and verifies installation
- ✓ Handles errors gracefully with detailed logs
- ✓ Warns if using wrong Python
- ✓ Non-interactive mode for CI/CD
- ✓ Exit codes for automation (0=success, 1=failure)

**How it works:**
Uses `subprocess` to call `pip` as a separate process. All output is logged to a file for debugging. Supports overriding QGIS Python path and non-interactive execution.

**Examples:**
```bash
# Basic usage
/Applications/QGIS.app/Contents/MacOS/bin/python3 install_mac_dependencies.py

# Non-interactive with custom log path
/Applications/QGIS.app/Contents/MacOS/bin/python3 install_mac_dependencies.py --yes --log /tmp/install.log

# Override QGIS path for QGIS-LTR
python3 install_mac_dependencies.py --python-path /Applications/QGIS-LTR.app/Contents/MacOS/bin/python3 --yes
```

### Method 3: Shell Script

**File:** `install_mac_dependencies.sh`

**Advantages:**
- ✓ Terminal-based automation
- ✓ Strict error handling (`set -euo pipefail`)
- ✓ Automatic QGIS installation discovery
- ✓ Environment variable override support
- ✓ Full logging to timestamped file
- ✓ Comprehensive error checking
- ✓ Exit codes for automation (0=success, 1=failure)
- ✓ Good for CI/CD and scripted installations

**How it works:**
```bash
# Default path
QGIS_PYTHON="${QGIS_PYTHON:-/Applications/QGIS.app/Contents/MacOS/bin/python3}"

# Auto-discovery if not found
if [ ! -x "$QGIS_PYTHON" ]; then
    # Search for QGIS*.app in /Applications
    ...
fi

$QGIS_PYTHON -m pip install libpysal esda --no-build-isolation
```

The script discovers QGIS automatically or uses env var override. All output is logged to a timestamped file.

**Examples:**
```bash
# Basic usage (auto-discovers QGIS)
bash install_mac_dependencies.sh

# Override QGIS path for QGIS-LTR
QGIS_PYTHON="/Applications/QGIS-LTR.app/Contents/MacOS/bin/python3" bash install_mac_dependencies.sh

# Custom log directory
LOG_DIR=/tmp bash install_mac_dependencies.sh
```

### Method 4: Terminal One-Liner

⚠️ **NOT RECOMMENDED** - This method **does not work correctly** on macOS due to Shapely version conflicts and NumPy compatibility issues. Use the automated script instead.

**Why this fails:**
```bash
# This will install packages but FAIL at runtime
/Applications/QGIS.app/Contents/MacOS/python3.12 -m pip install numpy scipy pandas numba libpysal esda matplotlib --no-build-isolation
```

**Problems:**
1. ❌ Installs to framework site-packages, doesn't override bundled Shapely 2.0.6
2. ❌ May install NumPy 2.x (dependency of numba), breaking QGIS
3. ❌ No handling of missing bin directory for numba
4. ❌ No error handling or logging
5. ❌ Imports will fail: `AttributeError: 'Geometry' object has no attribute 'exterior'` (Shapely 2.0 vs 2.1 API difference)

**If you must use Terminal**, use this pattern (but the automated script is still better):
```bash
QGIS_PYTHON="/Applications/QGIS.app/Contents/MacOS/python3.12"
PROFILE_DIR="$HOME/Library/Application Support/QGIS/QGIS3/profiles/default/python"

# Create profile python directory
mkdir -p "$PROFILE_DIR"

# Install Shapely to profile (overrides bundled 2.0.6)
$QGIS_PYTHON -m pip install "shapely>=2.1.2" --target "$PROFILE_DIR" --upgrade --no-deps

# Install numba to profile (avoids NumPy 2.x)
$QGIS_PYTHON -m pip install numba --target "$PROFILE_DIR" --no-deps

# Install other packages normally
$QGIS_PYTHON -m pip install scipy pandas libpysal esda matplotlib --no-build-isolation
```

**Why `-m pip` instead of just `pip`?**
Using `-m pip` ensures you're using the pip module for that specific Python, not a potentially different pip executable in your PATH.

---

## Verifying Installation

### Check Which Python You're Using

```bash
which python3
# Should show /opt/homebrew/bin/python3 or /usr/bin/python3 (NOT QGIS)

/Applications/QGIS.app/Contents/MacOS/bin/python3 -c "import sys; print(sys.executable)"
# Should show the QGIS Python path
```

### Verify Dependencies in QGIS

**🔄 IMPORTANT: Restart QGIS first!** QGIS only loads Python packages at startup.

Then open QGIS Python Console and run:

```python
import sys
print("Python:", sys.executable)
print()

# Check required dependencies with version requirements
checks = [
    ('libpysal', '4.3.0'),
    ('esda', '2.0.0'),
    ('numba', '0.50.0'),
    ('numpy', '1.18.0'),
    ('shapely', '2.1.2'),  # CRITICAL - must be 2.1.2+, not bundled 2.0.6
    ('geopandas', '0.14.0'),  # Required for GeoPackage support
    ('fiona', '1.9.0'),  # Required by geopandas
]

for module_name, min_version in checks:
    try:
        mod = __import__(module_name)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✓ {module_name} {version}", end='')
        
        # Special check for Shapely version
        if module_name == 'shapely':
            if version.startswith('2.0'):
                print(" ⚠️  WARNING: Using bundled 2.0.x, need 2.1.2+")
            elif version >= '2.1.2':
                print(" ✓ (correct version)")
        else:
            print()
    except ImportError:
        print(f"✗ {module_name} NOT FOUND (required: >={min_version})")

# Test GeoPackage support
print("\nGeoPackage (.gpkg) support:")
try:
    import geopandas as gpd
    import fiona
    print("✓ GeoPandas + Fiona available - GeoPackage files supported")
except ImportError as e:
    print(f"✗ Missing: {e.name} - GeoPackage support disabled (shapefile-only mode)")
```

**Expected output:**
```
✓ libpysal 4.12.2
✓ esda 2.6.0
✓ numba 0.60.0
✓ numpy 1.26.4
✓ shapely 2.1.2 ✓ (correct version)
✓ geopandas 0.14.3
✓ fiona 1.9.6

GeoPackage (.gpkg) support:
✓ GeoPandas + Fiona available - GeoPackage files supported
```

**If you see errors:**
- `shapely 2.0.x` - Installation didn't work, you're using QGIS's bundled version. Run the automated script again.
- `geopandas NOT FOUND` - GeoPackage files won't work in autocorrelation analysis. Run the automated script to install.

### List All Installed Packages

```python
import subprocess
import sys

result = subprocess.run(
    [sys.executable, '-m', 'pip', 'list'],
    capture_output=True,
    text=True
)
print(result.stdout)
```

---

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'libpysal'"

**Diagnosis:**
Dependencies were installed to the wrong Python.

**Solution:**
1. Check where packages were installed:
   ```bash
   # Check system/Homebrew Python
   python3 -c "import libpysal; print(libpysal.__file__)"

   # Check QGIS Python
   /Applications/QGIS.app/Contents/MacOS/bin/python3 -c "import libpysal; print(libpysal.__file__)"
   ```

2. If libpysal is NOT in QGIS Python, reinstall using QGIS Python Console or the automated script.

### Problem: "Permission denied" or "Access is denied"

**Diagnosis:**
Insufficient permissions to write to QGIS Python's site-packages directory.

**Solutions:**

1. Use `--user` flag (installs to user directory):
   ```bash
   /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install --user libpysal esda numba
   ```

2. Use QGIS Python Console instead (usually has correct permissions)

3. Fix permissions (advanced):
   ```bash
   sudo chown -R $(whoami) /Applications/QGIS.app/Contents/Resources/python/
   ```

### Problem: Build errors with libpysal or esda

**Symptoms:**
```
ERROR: Failed building wheel for libpysal
```

**Solution:**
Use `--no-build-isolation` flag:
```bash
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install libpysal esda --no-build-isolation
```

**Why this works:**
These packages need to see build dependencies (like numpy, scipy) during installation. The `--no-build-isolation` flag allows them to use the already-installed versions.

### Problem: Multiple QGIS installations

**Diagnosis:**
You have both QGIS LTR and QGIS Latest installed (or older versions).

**Solution:**
1. Determine which QGIS you're using:
   ```bash
   ls -la /Applications/ | grep -i qgis
   ```

2. Install dependencies to the correct version:
   ```bash
   /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install ...
   # or
   /Applications/QGIS-LTR.app/Contents/MacOS/bin/python3 -m pip install ...
   ```

### Problem: Installation works but QGIS doesn't see packages

**Possible causes:**
1. **User vs system installation conflict**
   - Check both locations: system site-packages and user site-packages
   - Solution: Uninstall from both, reinstall to one location

2. **QGIS Python Console using different Python**
   - Verify in console: `import sys; print(sys.executable)`
   - Should be `/Applications/QGIS.app/Contents/MacOS/bin/python3`

3. **Cached imports**
   - Solution: Fully restart QGIS (not just close/reopen)
   - Clear Python cache: `rm -rf ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/__pycache__`

### Reporting Installation Issues

If you need to report an installation problem, please include the following information:

**Required Information:**
1. **Installation log file** (created automatically by scripts)
   - Location: `./geopublichealth_install_YYYYMMDD_HHMMSS.log`
   - Attach the entire log file to your issue report

2. **QGIS version:**
   ```python
   # Run in QGIS Python Console:
   from qgis.core import QgsApplication
   print(QgsApplication.version())
   ```

3. **macOS version:**
   ```bash
   # Run in Terminal:
   sw_vers
   ```

4. **Python version:**
   ```python
   # Run in QGIS Python Console:
   import sys
   print(sys.version)
   print(sys.executable)
   ```

**Where to report:**
- GitHub Issues: https://github.com/ePublicHealth/GeoPublicHealth/issues

**Issue template:**
```markdown
### Installation Problem

**Environment:**
- macOS version: [output of sw_vers]
- QGIS version: [output from QGIS console]
- Python path: [sys.executable from QGIS console]

**Installation method used:**
- [ ] QGIS Python Console script
- [ ] QGIS Python Console manual commands
- [ ] Terminal Python script
- [ ] Shell script
- [ ] Terminal one-liner

**Problem description:**
[Describe what happened]

**Log file:**
[Attach geopublichealth_install_*.log file]
```

---

## Advanced Scenarios

### Scenario 1: Using Virtual Environments

**Question:** Can I use a virtualenv or conda environment with QGIS?

**Answer:** Not recommended. QGIS expects its bundled Python and pre-installed packages (PyQt5, qgis module). Using a different environment will break QGIS functionality.

**Alternative:** Install packages directly to QGIS Python using the methods above.

### Scenario 2: Development Workflow

If you're developing plugins and want to test with development versions of dependencies:

1. Clone dependency to local directory:
   ```bash
   cd ~/projects
   git clone https://github.com/pysal/libpysal.git
   ```

2. Install in development mode:
   ```bash
   /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install -e ~/projects/libpysal
   ```

3. Changes to the source code are immediately reflected in QGIS (after restart).

### Scenario 3: Reproducible Installations and Version Pinning

**Question:** How do I ensure consistent dependency versions across installations?

**Answer:** Use the provided `requirements-mac.txt` file with pinned versions.

**Why version pinning matters:**
- The automated scripts install **latest versions** of packages
- Latest versions may introduce breaking changes or incompatibilities
- For production deployments or reproducible research, pinned versions are recommended
- Pinned versions are tested and known to work together

**Using pinned versions:**

Option 1 - Terminal:
```bash
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install -r requirements-mac.txt --no-build-isolation
```

Option 2 - QGIS Python Console:
```python
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-mac.txt", "--no-build-isolation"])
```

**Provided file:** `requirements-mac.txt` contains tested, compatible versions.

**When to use:**
- ✅ Production deployments
- ✅ Reproducible research
- ✅ CI/CD pipelines
- ✅ When you need stable, tested versions

**When NOT to use:**
- ❌ Quick testing (use automated scripts instead)
- ❌ Development (may want latest features)
- ❌ When you specifically need newer versions

**Security note:**
For maximum security and reproducibility, you can add hashes to requirements:
```bash
# Generate hashes
pip hash <package-name>==<version>

# Install with hash verification
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install -r requirements-mac.txt --no-build-isolation --require-hashes
```

**Custom requirements file:**
You can create your own based on `requirements-mac.txt`:
1. Copy the file: `cp requirements-mac.txt my-requirements.txt`
2. Modify versions as needed
3. Test thoroughly before deploying
4. Document tested QGIS/macOS versions in comments

### Scenario 4: Completely Clean Reinstall

If you need to start fresh:

1. Uninstall packages:
   ```bash
   /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip uninstall -y libpysal esda numba matplotlib scipy pandas
   ```

2. Clear pip cache:
   ```bash
   /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip cache purge
   ```

3. Reinstall:
   ```bash
   /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install --no-cache-dir numpy scipy pandas numba libpysal esda matplotlib --no-build-isolation
   ```

### Scenario 5: Using Homebrew to Install System Dependencies

Some packages may need system libraries. Example:

```bash
# Install system dependencies via Homebrew
brew install geos proj

# Then install Python packages to QGIS Python
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install libpysal
```

---

## Summary

**Key Takeaways:**

1. ✅ QGIS has its own Python - separate from system/Homebrew/conda Python
2. ✅ Dependencies MUST be installed to QGIS's Python specifically
3. ✅ Use QGIS Python Console or explicit QGIS Python path for all installations
4. ✅ The automated scripts handle this correctly
5. ✅ When in doubt, use the automated script from QGIS Python Console

**Quick Reference:**

| Method | Complexity | Reliability | Environment Safety | Recommended For |
|--------|------------|-------------|-------------------|-----------------|
| **QGIS Console (subprocess.run)** | **Easy** | **Highest** | **100% Safe** | **Everyone - PRIMARY METHOD** |
| QGIS Console Script | Easy | Highest | 100% Safe | Everyone who prefers automation |
| Terminal One-liner | Medium | Medium | Requires exact path | Advanced users comfortable with Terminal |
| Shell Script | Medium | High | Requires exact path (autodiscovery available) | Terminal users, CI/CD, scripted deployments |
| Terminal Python script | Medium | High | Has environment check, CLI args | Automation with logging, non-interactive mode |

**Recommendation Priority:**
1. 🥇 **QGIS Python Console** (manual commands or script) - Use this unless you have a specific reason not to
2. 🥈 Terminal methods - Only for advanced users or automation scenarios
3. 🥉 Other methods - For specific edge cases or troubleshooting

---

## Additional Resources

- [INSTALL_MAC.md](INSTALL_MAC.md) - Quick start guide
- [README.md](README.md) - General installation instructions
- [DEPENDENCIES.md](DEPENDENCIES.md) - Dependency details
- [QGIS Python Cookbook](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/) - Official PyQGIS documentation
