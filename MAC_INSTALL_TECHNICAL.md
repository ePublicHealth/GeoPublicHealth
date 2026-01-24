# macOS Installation - Technical Guide

This document provides detailed technical information about installing GeoPublicHealth dependencies on macOS, including Python environment management, troubleshooting, and advanced scenarios.

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
/Applications/QGIS.app/Contents/MacOS/bin/python3
```

### Version

QGIS typically bundles Python 3.9 - 3.12 depending on the QGIS version:
- QGIS 3.44: Python 3.12.x
- QGIS 3.42: Python 3.11.x

Check your version:
```bash
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

### Method 1: QGIS Python Console (Recommended)

**Advantages:**
- ✓ Always uses correct Python
- ✓ No Terminal knowledge required
- ✓ Can't accidentally use wrong Python
- ✓ Works even with restrictive permissions

**How it works:**
When you run code in QGIS Python Console, it uses QGIS's bundled Python interpreter automatically. The `pip.main()` function calls pip within the same Python environment.

**Commands:**
```python
import pip
pip.main(['install', 'libpysal', 'esda', '--no-build-isolation'])
pip.main(['install', 'numba'])
```

**Why `--no-build-isolation`?**
Some packages (like libpysal and esda) have build-time dependencies that need to be visible. The `--no-build-isolation` flag allows them to use already-installed packages during build, preventing errors.

### Method 2: Automated Python Script

**File:** `install_mac_dependencies.py`

**Advantages:**
- ✓ Installs all dependencies automatically
- ✓ Shows progress and verifies installation
- ✓ Handles errors gracefully
- ✓ Warns if using wrong Python

**How it works:**
Uses `subprocess` to call `pip` as a separate process, ensuring proper installation even in complex environments.

### Method 3: Shell Script

**File:** `install_mac_dependencies.sh`

**Advantages:**
- ✓ Terminal-based automation
- ✓ Explicitly uses QGIS Python path
- ✓ Comprehensive error checking
- ✓ Good for scripted installations

**How it works:**
```bash
QGIS_PYTHON="/Applications/QGIS.app/Contents/MacOS/bin/python3"
$QGIS_PYTHON -m pip install libpysal esda --no-build-isolation
```

The script sets a variable to the QGIS Python path and uses it explicitly.

### Method 4: Terminal One-Liner

**Command:**
```bash
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install numpy scipy pandas libpysal esda numba matplotlib --no-build-isolation
```

**Advantages:**
- ✓ Fast and simple
- ✓ Good for re-installation or updates
- ✓ Explicitly targets QGIS Python

**Disadvantages:**
- ✗ Easy to typo the Python path
- ✗ No error handling
- ✗ Requires Terminal knowledge

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

Open QGIS Python Console and run:

```python
import sys
print("Python:", sys.executable)
print()

# Check required dependencies
for module in ['libpysal', 'esda', 'numba', 'numpy']:
    try:
        mod = __import__(module)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✓ {module} {version}")
    except ImportError:
        print(f"✗ {module} NOT FOUND")
```

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

### Scenario 3: Automating for Multiple Machines

Create a requirements.txt file:

```txt
numpy>=1.20
scipy>=1.7
pandas>=1.3
libpysal>=4.3.0
esda>=2.4.0
numba>=0.54
matplotlib>=3.4
```

Install on each machine:
```bash
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install -r requirements.txt --no-build-isolation
```

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
   /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install --no-cache-dir numpy scipy pandas libpysal esda numba matplotlib --no-build-isolation
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

| Method | Complexity | Reliability | Recommended For |
|--------|------------|-------------|-----------------|
| QGIS Python Console | Easy | Highest | Everyone, especially beginners |
| Automated Script | Easy | High | Users who want automation |
| Shell Script | Medium | High | Terminal users, automation |
| One-liner | Medium | Medium | Advanced users, quick reinstall |
| Manual | Hard | Medium | Troubleshooting, specific control |

---

## Additional Resources

- [INSTALL_MAC.md](INSTALL_MAC.md) - Quick start guide
- [README.md](README.md) - General installation instructions
- [DEPENDENCIES.md](DEPENDENCIES.md) - Dependency details
- [QGIS Python Cookbook](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/) - Official PyQGIS documentation
