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

Choose the method that works best for you:

### 🌟 Easiest: Automated Script (Recommended)

1. Download this repository (or just `install_mac_dependencies.py`)
2. Open QGIS
3. Go to **Plugins → Python Console**
4. Click **"Show Editor"** button (toolbar icon)
5. Click **"Open Script"** and select `install_mac_dependencies.py`
6. Click **"Run Script"**
7. Wait for completion
8. Restart QGIS

### ⚡ Fastest: Terminal One-Liner

Open Terminal and paste:

```bash
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install numpy scipy pandas libpysal esda numba matplotlib --no-build-isolation
```

Then restart QGIS.

### 🔧 Alternative: Shell Script

1. Download this repository
2. Open Terminal
3. Navigate to the folder: `cd /path/to/GeoPublicHealth`
4. Run: `bash install_mac_dependencies.sh`
5. Restart QGIS

## Step 3: Install the Plugin

1. Open QGIS
2. Go to **Plugins → Manage and Install Plugins**
3. Go to **Settings** tab
4. Check **"Show also experimental plugins"**
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
