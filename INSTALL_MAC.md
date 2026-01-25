# Quick Mac Installation Guide

This is a simplified installation guide specifically for macOS users.

## 🔑 Important: Understanding Python Environments

**QGIS has its own Python** - it's completely separate from any other Python on your Mac.

If you have multiple Python installations (Homebrew, Anaconda, system Python), **don't worry** - they won't interfere. But you need to install the plugin dependencies specifically into **QGIS's Python**, not your other Python installations.

**Where is QGIS's Python?**
- Location: `/Applications/QGIS.app/Contents/MacOS/python3.12` (or `python3.11` depending on QGIS version)
- This is different from `/usr/bin/python3` (macOS system Python)
- This is different from `/opt/homebrew/bin/python3` (Homebrew Python)
- This is different from conda/anaconda Python

**Why does this matter?**
If you accidentally install dependencies to the wrong Python, QGIS won't be able to find them and the plugin won't work.

**The good news:** The installation methods below automatically use the correct Python, so you don't have to worry about it! Just follow the steps. 🎉

---

## Step 1: Install QGIS

1. Download: [QGIS for macOS](https://download.qgis.org/downloads/macos/qgis-macos-pr.dmg)
2. Open the `.dmg` file and drag QGIS to Applications
3. **First launch:** Right-click QGIS → Open (to bypass security warning)

## Step 2: Install Dependencies

**✅ RECOMMENDED: Use QGIS Python Console**

This is the most reliable method because QGIS Python Console automatically uses the correct Python environment - there's no way to accidentally use the wrong Python!

**Mental model:** The QGIS Python Console runs **Python only**. Terminal commands (anything starting with `/Applications/...` or `QGIS_PYTHON=...`) must be run in Terminal, not in the console.

**Tip:** If you see an error like `NameError: name 'QGIS_PYTHON' is not defined`, you pasted a Terminal command into the console.

### Method 1: Automated Script (Easiest - Just Click Run!)

1. Get the script (choose one):
   - Download the GeoPublicHealth repository (ZIP or git clone) and **unzip** it. The script is inside the folder: `install_dependencies_console.py`.
   - Or download the script directly: https://raw.githubusercontent.com/ePublicHealth/GeoPublicHealth/refs/heads/main/install_dependencies_console.py
     - Save the file locally as `install_dependencies_console.py` (recommended location: `~/Downloads/`).
   - Or open the link, copy the full script, paste it into the QGIS Python editor, and save it as `install_dependencies_console.py`.
2. Open QGIS
3. Go to **Plugins → Python Console**
4. Click **"Show Editor"** button (toolbar icon)
5. Click **"Open Script"** and select `install_dependencies_console.py`
   - If you can’t find it, use **Cmd+Shift+G** and paste the folder path (e.g. `~/Downloads/GeoPublicHealth`)
   - You can also use Finder search for `install_dependencies_console.py`
6. Click **"Run Script"**
7. Watch progress messages in the console
8. The script automatically:
   - Enables "Show also experimental plugins" setting
   - Adds GeoPublicHealth plugin repository
   - Reloads plugin repositories from the network
   - Installs required dependencies (libpysal, esda, numba)
   - Installs the GeoPublicHealth plugin
9. **🔄 Restart QGIS when complete** (required for new packages and plugin to load)
10. **🧾 Logs:** Saved to `~/GeoPublicHealth/` (fallback: `/tmp/`)

### Method 2: Manual Verification (After Automated Script)

After running the automated script (Method 1), verify the installation worked:

1. **🔄 Restart QGIS first** (required for new packages to load)
2. Open QGIS
3. Go to **Plugins → Python Console**
4. Run this verification script:

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
```

**What to check:**
- Python path should contain `QGIS.app` (confirms you're using QGIS's Python)
- Shapely version should be 2.1.2 or newer (required for libpysal compatibility)
- GeoPandas and Fiona are installed (required for GeoPackage .gpkg file support)
- You should see version numbers for all packages

**If verification fails:** See Troubleshooting section below or use the automated script's restart prompt.

---

### Alternative Methods (For Advanced Users)

**⚠️ These commands are for Terminal, not the QGIS Python Console.** If you paste them into the console, they will fail.

<details>
<summary>Click to expand Terminal-based methods</summary>

**⚠️ Warning:** These require using the exact QGIS Python path. The console methods above are more reliable.

**Terminal One-Liner:**

⚠️ **Not recommended** - use the automated console script instead (Method 1). The script handles Shapely/Numba installation correctly with `--target` and `--no-deps` to avoid NumPy 2.x conflicts.

If you must use Terminal:
```bash
# This installs to framework site-packages and may cause version conflicts
/Applications/QGIS.app/Contents/MacOS/python3.12 -m pip install numpy scipy pandas libpysal esda matplotlib --no-build-isolation
```

**Shell Script:**

⚠️ **Deprecated** - use `install_dependencies_console.py` from QGIS Python Console instead.

```bash
cd /path/to/GeoPublicHealth
bash install_mac_dependencies.sh
```

**For automation / CI / QGIS-LTR:**

```bash
# Non-interactive mode with logging
/Applications/QGIS.app/Contents/MacOS/python3.12 install_mac_dependencies.py --yes --log /tmp/install.log

# Override QGIS path for QGIS-LTR
QGIS_PYTHON="/Applications/QGIS-LTR.app/Contents/MacOS/python3.11" bash install_mac_dependencies.sh
```

</details>

## Fallback: Install the Plugin Manually

Use these steps only if the automated script did not install the plugin after restarting QGIS.

1. Open QGIS
2. Go to **Plugins → Manage and Install Plugins**
3. Go to **Settings** tab
4. **🚨 Critical:** Check **"Show also experimental plugins"** (the plugin will not appear without this)
5. Click **Add** button:
   - Name: `GeoPublicHealth`
   - URL: `https://raw.githubusercontent.com/ePublicHealth/GeoPublicHealth/main/docs/plugins.xml`
6. Go to **All** tab
7. Search for `geopublichealth`
8. Click **Install Plugin**

## Verify Everything Works

**🔄 IMPORTANT: Restart QGIS first!** (QGIS only loads packages at startup)

Then open the QGIS Python Console and run:

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
```

**What to check:**
- The Python path should contain `QGIS.app` (confirms you're using QGIS's Python)
- Shapely version should be **2.1.2 or newer** (QGIS bundles 2.0.6 which is incompatible)
- GeoPandas and Fiona are installed (enables GeoPackage .gpkg file support in autocorrelation)
- You should see version numbers for all packages

If you see version numbers, you're ready to go! 🎉

**Why the restart matters:** QGIS loads Python packages only at startup. After installing dependencies, a full restart is the reliable way to make them available (reloading plugins is not enough).

**Why these packages matter:**
- **Shapely 2.1.2**: QGIS bundles 2.0.6, but libpysal requires 2.1.2+ (API breaking changes). The automated script installs 2.1.2 to your QGIS profile directory which overrides the bundled version.
- **GeoPandas + Fiona**: Required for GeoPackage (.gpkg) file support in autocorrelation analysis. Without these, the plugin falls back to shapefile-only mode.

**If it doesn't work:**
- See the Troubleshooting section below
- For detailed technical information: [MAC_INSTALL_TECHNICAL.md](MAC_INSTALL_TECHNICAL.md)
## Troubleshooting

### "ModuleNotFoundError: No module named 'libpysal'"

**Solutions:**
1. **Did you restart QGIS?** This is the most common issue - restart first, then try verification again
2. Run the automated script (Method 1) - it handles installation correctly
3. Check the installation log file in `~/GeoPublicHealth/` for errors

### "ImportError: Shapely version 2.1.2+ required"

The automated script installs Shapely 2.1.2 to override QGIS's bundled 2.0.6. If you see this error:
1. Ensure you ran `install_dependencies_console.py` (not manual Terminal commands)
2. Restart QGIS after installation
3. Check Shapely version: `import shapely; print(shapely.__version__)`

### "Permission denied" errors

The automated script handles permissions correctly. If you see this:
1. Use Method 1 (automated script) instead of Terminal commands
2. Or use `--user` flag if using Terminal:
```bash
/Applications/QGIS.app/Contents/MacOS/python3.12 -m pip install --user libpysal esda numba
```

### Plugin doesn't appear

1. Check experimental plugins are enabled (see Step 3)
2. Clear cache: `rm -rf ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/cache`
3. Restart QGIS

### Library loading errors

Install XQuartz: https://www.xquartz.org/

## Need More Help?

- **Technical details and advanced troubleshooting**: [MAC_INSTALL_TECHNICAL.md](MAC_INSTALL_TECHNICAL.md)
- See full documentation: [README.md](README.md)
- Dependency details: [DEPENDENCIES.md](DEPENDENCIES.md)
- Report issues: [GitHub Issues](https://github.com/ePublicHealth/GeoPublicHealth/issues)

---

## For Advanced Users

If you want to understand:
- Why QGIS has its own Python
- How Python environments work on Mac
- Detailed installation methods and troubleshooting
- Development workflows

See the complete technical guide: **[MAC_INSTALL_TECHNICAL.md](MAC_INSTALL_TECHNICAL.md)**
