# Quick Mac Installation Guide

This is a simplified installation guide specifically for macOS users.

## 🔑 Important: Understanding Python Environments

**QGIS has its own Python** - it's completely separate from any other Python on your Mac.

If you have multiple Python installations (Homebrew, Anaconda, system Python), **don't worry** - they won't interfere. But you need to install the plugin dependencies specifically into **QGIS's Python**, not your other Python installations.

**Where is QGIS's Python?**
- Location: `/Applications/QGIS.app/Contents/MacOS/bin/python3`
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

### Method 1: Automated Script (Easiest - Just Click Run!)

1. Download `install_dependencies_console.py` from this repository
2. Open QGIS
3. Go to **Plugins → Python Console**
4. Click **"Show Editor"** button (📝 icon in toolbar)
5. Click **"Open Script"** (📂 folder icon) and select `install_dependencies_console.py`
6. Click **"Run Script"** (▶️ play button)
7. Watch the progress in the console
8. **⚠️ CRITICAL: Completely close and restart QGIS when complete** (dependencies won't be available until you do!)

**Important:** Use the toolbar buttons to open and run the script. Do NOT type the filename directly in the console.

### Method 2: Manual Console Commands (More Control)

1. Open QGIS
2. Go to **Plugins → Python Console**
3. First, set up a helper function (copy/paste this):

```python
import subprocess, sys
def install(pkg): subprocess.run([sys.executable, "-m", "pip", "install"] + pkg.split())
```

4. Then install each package **one at a time** (copy/paste each line, press Enter):

```python
install("pip --upgrade")
install("numpy")
install("scipy")
install("pandas")
install("numba")
install("libpysal esda --no-build-isolation")
install("matplotlib")
```

**Note:** This uses `subprocess.run()` (not `pip.main()`) which is stable across pip versions.

5. **⚠️ CRITICAL: Completely close and restart QGIS** (dependencies won't be available until you do!)

---

### Alternative Methods (For Advanced Users)

<details>
<summary>Click to expand Terminal-based methods</summary>

**⚠️ Warning:** These require using the exact QGIS Python path. The console methods above are more reliable.

**Terminal One-Liner:**

```bash
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install numpy scipy pandas numba libpysal esda matplotlib --no-build-isolation
```

**Shell Script:**

```bash
cd /path/to/GeoPublicHealth
bash install_mac_dependencies.sh
```

**For automation / CI / QGIS-LTR:**

```bash
# Non-interactive mode with logging
/Applications/QGIS.app/Contents/MacOS/bin/python3 install_mac_dependencies.py --yes --log /tmp/install.log

# Override QGIS path for QGIS-LTR
QGIS_PYTHON="/Applications/QGIS-LTR.app/Contents/MacOS/bin/python3" bash install_mac_dependencies.sh
```

</details>

## Step 3: Install the Plugin

1. Open QGIS
2. Go to **Plugins → Manage and Install Plugins**
3. Go to **Settings** tab
4. **⚠️ CRITICAL:** Check **"Show also experimental plugins"** (plugin won't appear without this!)
5. Click **Add** button:
   - Name: `epublichealth`
   - URL: `https://raw.githubusercontent.com/ePublicHealth/GeoPublicHealth/main/docs/plugins.xml`
6. Go to **All** tab
7. Search for `geopublichealth`
8. Click **Install Plugin**

## Verify Everything Works

Open the QGIS Python Console and run:

```python
import sys
print(f"Python: {sys.executable}")
print("(Should contain 'QGIS.app')\n")

import libpysal, esda, numba
print(f"✓ All dependencies installed!")
print(f"  libpysal {libpysal.__version__}")
print(f"  esda {esda.__version__}")
print(f"  numba {numba.__version__}")
```

**What to check:**
- The Python path should contain `QGIS.app` (confirms you're using QGIS's Python)
- You should see version numbers for all three packages

If you see version numbers, you're ready to go! 🎉

**If it doesn't work:**
- See the Troubleshooting section below
- For detailed technical information: [MAC_INSTALL_TECHNICAL.md](MAC_INSTALL_TECHNICAL.md)

## Troubleshooting

### "ModuleNotFoundError: No module named 'libpysal'"

The dependencies didn't install. Try the Terminal one-liner method above.

### "Permission denied" errors

Add `--user` flag:
```bash
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install --user libpysal esda numba
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
