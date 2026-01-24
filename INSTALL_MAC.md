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

**Mental model:** The QGIS Python Console runs **Python only**. Terminal commands (anything starting with `/Applications/...` or `QGIS_PYTHON=...`) must be run in Terminal, not in the console.

**Tip:** If you see an error like `NameError: name 'QGIS_PYTHON' is not defined`, you pasted a Terminal command into the console.

### Method 1: Automated Script (Easiest - Just Click Run!)

1. Download `install_dependencies_console.py` from this repository
2. Open QGIS
3. Go to **Plugins → Python Console**
4. Click **"Show Editor"** button (toolbar icon)
5. Click **"Open Script"** and select `install_dependencies_console.py`
6. Click **"Run Script"**
7. Watch the progress in the console
8. **🔄 Restart QGIS when complete** (required for new packages to load)

### Method 2: Manual Console Commands (More Control)

1. Open QGIS
2. Go to **Plugins → Python Console**
3. Copy and paste these commands **one at a time** (press Enter after each)
4. **Do not paste Terminal commands here** (only Python works in the console)

```python
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
subprocess.run([sys.executable, "-m", "pip", "install", "numpy"])
subprocess.run([sys.executable, "-m", "pip", "install", "scipy"])
subprocess.run([sys.executable, "-m", "pip", "install", "pandas"])
subprocess.run([sys.executable, "-m", "pip", "install", "numba"])  # Install numba before libpysal/esda
subprocess.run([sys.executable, "-m", "pip", "install", "libpysal", "esda", "--no-build-isolation"])
subprocess.run([sys.executable, "-m", "pip", "install", "matplotlib"])  # Optional
```

**Note:** We use `subprocess.run` with `sys.executable -m pip` (not `pip.main()`) because it's more stable across pip versions.

**If these commands fail:** Use Method 1 (Open Script). It avoids console copy/paste issues.

5. **🔄 Restart QGIS** (required for QGIS to see new packages)

---

### Alternative Methods (For Advanced Users)

**⚠️ These commands are for Terminal, not the QGIS Python Console.** If you paste them into the console, they will fail.

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
4. **🚨 Critical:** Check **"Show also experimental plugins"** (the plugin will not appear without this)
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
import libpysal, esda, numba

print(f"Python: {sys.executable}")
print("(Should contain 'QGIS.app')\n")
print("✓ All dependencies installed!")
print(f"  libpysal {libpysal.__version__}")
print(f"  esda {esda.__version__}")
print(f"  numba {numba.__version__}")
```

**What to check:**
- The Python path should contain `QGIS.app` (confirms you're using QGIS's Python)
- You should see version numbers for all three packages

If you see version numbers, you're ready to go! 🎉

**Why the restart matters:** QGIS loads Python packages only at startup. After installing dependencies, a full restart is the reliable way to make them available (reloading plugins is not enough).

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
