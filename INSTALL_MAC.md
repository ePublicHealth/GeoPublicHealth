# 📍 Quick Mac Installation Guide

**Simple, step-by-step instructions for macOS users.** No technical background needed!

> 📘 **For technical users:** See [MAC_INSTALL_TECHNICAL.md](MAC_INSTALL_TECHNICAL.md) for detailed explanations, advanced methods, and troubleshooting.

---

## 🧠 Understanding the Basics (Read This First!)

### The Key Concept: QGIS Has Its Own Python

Think of QGIS as a self-contained app that brings its own Python interpreter - just like it brings its own GIS tools. This Python is completely separate from any other Python you might have on your Mac.

**The Mental Model:**
```
Your Mac may have:
  📦 System Python       (built into macOS)
  📦 Homebrew Python     (if you installed it)
  📦 Anaconda Python     (if you use it for data science)
  📦 QGIS Python         ← This is the one we need!
```

**Why this matters:**
- When you install libraries for GeoPublicHealth, they MUST go into QGIS's Python
- Installing to the wrong Python = QGIS won't see the libraries = plugin won't work
- It's like delivering a package to the wrong house - even if it's on the same street!

**The good news:**
The installation methods below automatically use the correct Python. Just follow the steps and you'll be fine! 🎉

**Where is QGIS's Python?**
- Hidden inside the QGIS app at: `/Applications/QGIS.app/Contents/MacOS/bin/python3`
- You don't need to memorize this - the console method handles it automatically!

---

## 📥 Step 1: Install QGIS

**What we're doing:** Installing the main QGIS application.

1. **Download QGIS:** [Get QGIS for macOS](https://download.qgis.org/downloads/macos/qgis-macos-pr.dmg)
2. **Install:** Open the `.dmg` file and drag QGIS to your Applications folder
3. **First launch:** Right-click QGIS in Applications → choose "Open"

   💡 **Why?** macOS security blocks apps from unidentified developers. Right-clicking bypasses this (one-time only).

## 🔧 Step 2: Install Python Dependencies

**What we're doing:** Installing the mathematical and GIS libraries that GeoPublicHealth needs.

**Why we use QGIS Python Console:**
- ✅ Automatically uses the correct Python (impossible to make a mistake!)
- ✅ No Terminal or command-line knowledge needed
- ✅ Works the same on every Mac
- ✅ Can't accidentally install to the wrong Python

---

### 🎯 Method 1: Automated Script (Easiest!)

**Perfect for:** First-time users, anyone who wants the simplest approach.

**Steps:**

1. **📥 Download the installer:** Get `install_dependencies_console.py` from [this repository](https://github.com/ePublicHealth/GeoPublicHealth)

2. **🚀 Open QGIS**

3. **🐍 Open Python Console:** Go to menu `Plugins → Python Console`

   💡 A new panel appears at the bottom - this is Python running inside QGIS!

4. **📝 Open the editor:** Click the **"Show Editor"** button (notepad icon in console toolbar)

5. **📂 Load the script:** Click **"Open Script"** (folder icon) and select `install_dependencies_console.py`

6. **▶️ Run it:** Click the **"Run Script"** button (play icon)

7. **⏳ Wait:** Watch the progress in the console (takes 2-5 minutes)

8. **🔄 CRITICAL STEP - Restart QGIS:**
   - **Completely close** QGIS (Cmd+Q or QGIS → Quit)
   - **Wait 2-3 seconds**
   - **Reopen** QGIS

   ⚠️ **Why?** Python loads libraries when it starts. The new libraries won't be available until you restart!

**⚠️ Common Mistake:** Don't type the filename in the console! Use the toolbar buttons to open and run the script.

---

### 🎛️ Method 2: Manual Console Commands

**Perfect for:** Users who want to see each step, or if the script method doesn't work.

**Steps:**

1. **🚀 Open QGIS**

2. **🐍 Open Python Console:** `Plugins → Python Console`

3. **🔨 Set up a helper function:**

   Copy this entire block and paste into the console, then press Enter:

   ```python
   import subprocess, sys
   def install(pkg): subprocess.run([sys.executable, "-m", "pip", "install"] + pkg.split())
   ```

   💡 **What this does:** Creates a simple command that installs packages to the correct Python.

4. **📦 Install each package one at a time:**

   Copy/paste each line below, press Enter after each, wait for it to finish:

   ```python
   install("pip --upgrade")
   install("numpy")
   install("scipy")
   install("pandas")
   install("numba")
   install("libpysal esda --no-build-isolation")
   install("matplotlib")
   ```

   💡 **What's happening:** Each command downloads and installs a library. Takes 30-60 seconds per package.

5. **🔄 CRITICAL STEP - Restart QGIS:**
   - **Completely quit** QGIS (Cmd+Q or QGIS → Quit)
   - **Wait 2-3 seconds**
   - **Reopen** QGIS

   ⚠️ **Why?** The libraries won't work until QGIS reloads Python with the new packages!

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

## 🔌 Step 3: Install the GeoPublicHealth Plugin

**What we're doing:** Adding the GeoPublicHealth plugin to QGIS.

**Steps:**

1. **🚀 Open QGIS** (make sure you restarted after Step 2!)

2. **🔌 Open Plugin Manager:** Go to `Plugins → Manage and Install Plugins`

3. **⚙️ Go to Settings tab**

4. **⚠️ CRITICAL - Enable experimental plugins:**

   Check the box: **☑️ Show also experimental plugins**

   💡 **Why?** GeoPublicHealth is marked as "experimental" during development. Without this, it won't show up in the list!

5. **➕ Add the plugin repository:**

   Click the **Add** button and enter:
   - **Name:** `epublichealth` (or anything you like)
   - **URL:** `https://raw.githubusercontent.com/ePublicHealth/GeoPublicHealth/main/docs/plugins.xml`

   Click **OK**

   💡 **What this does:** Tells QGIS where to find the GeoPublicHealth plugin.

6. **🔍 Find the plugin:**

   - Go to the **All** tab
   - In the search box, type: `geopublichealth`
   - The plugin should appear in the list

7. **📥 Install:**

   - Click on **GeoPublicHealth** in the list
   - Click **Install Plugin**
   - Wait for the installation to complete

8. **✅ Verify:**

   Check that **GeoPublicHealth** now appears in the `Plugins` menu in QGIS!

## ✅ Verify Everything Works

**Let's make sure all the dependencies are correctly installed!**

1. **🐍 Open QGIS Python Console:** `Plugins → Python Console`

2. **📋 Copy and paste this test code:**

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

3. **🔍 Check the results:**

   **✅ Success looks like:**
   ```
   Python: /Applications/QGIS.app/Contents/MacOS/bin/python3
   (Should contain 'QGIS.app')

   ✓ All dependencies installed!
     libpysal 4.9.2
     esda 2.5.1
     numba 0.59.0
   ```

   - Python path contains `QGIS.app` ✓
   - All three packages show version numbers ✓

   **🎉 You're ready to use GeoPublicHealth!**

   **❌ Problem signs:**
   - `ModuleNotFoundError` - Dependencies not installed, see Troubleshooting below
   - Python path doesn't contain `QGIS.app` - Wrong Python, see Troubleshooting below

## 🔧 Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'libpysal'"

**Problem:** Dependencies didn't install correctly.

**Solutions to try (in order):**

1. **Did you restart QGIS?** This is the #1 most common cause!
   - Quit QGIS completely (Cmd+Q)
   - Wait 2-3 seconds
   - Reopen QGIS
   - Try the verification again

2. **Try the manual method:** Use Method 2 (Manual Console Commands) above

3. **Check the log file:** The installer creates a log file in your current directory:
   - Look for `geopublichealth_install_YYYYMMDD_HHMMSS.log`
   - Check for error messages
   - Include this file if reporting an issue

### ❌ Plugin doesn't appear in the list

**Problem:** Can't find GeoPublicHealth in the plugin manager.

**Solutions:**

1. **Check experimental plugins:** Did you enable "Show also experimental plugins" in Step 3.4?

2. **Clear QGIS cache:**
   - Quit QGIS
   - Run in Terminal:
     ```bash
     rm -rf ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/cache
     ```
   - Restart QGIS
   - Try again

3. **Repository URL correct?** Double-check you entered:
   ```
   https://raw.githubusercontent.com/ePublicHealth/GeoPublicHealth/main/docs/plugins.xml
   ```

### ❌ "Permission denied" errors during installation

**Problem:** Don't have permission to install to QGIS's Python directory.

**Solution:** Add the `--user` flag:

In QGIS Python Console:
```python
import subprocess, sys
def install(pkg): subprocess.run([sys.executable, "-m", "pip", "install", "--user"] + pkg.split())
# Then run install commands as in Method 2
```

### ❌ Library loading errors / matplotlib warnings

**Problem:** Some graphical libraries missing (rare on modern macOS).

**Solution:** Install XQuartz: https://www.xquartz.org/

## 📚 Need More Help?

### 🆘 Still having problems?

1. **📖 Read the technical guide:** [MAC_INSTALL_TECHNICAL.md](MAC_INSTALL_TECHNICAL.md)
   - Detailed explanations of each method
   - Advanced troubleshooting scenarios
   - Understanding Python environments on Mac

2. **🐛 Report an issue:** [GitHub Issues](https://github.com/ePublicHealth/GeoPublicHealth/issues)
   - Include your log file (`geopublichealth_install_*.log`)
   - Mention your macOS and QGIS versions
   - Describe what you tried

3. **📋 Check other documentation:**
   - [README.md](README.md) - Main documentation
   - [DEPENDENCIES.md](DEPENDENCIES.md) - Detailed dependency information

---

## 🎓 For Technical Users

**Want to understand how this works under the hood?**

See the complete technical guide: **[MAC_INSTALL_TECHNICAL.md](MAC_INSTALL_TECHNICAL.md)**

Topics covered:
- Why QGIS has its own Python and how it's isolated
- Detailed explanation of each installation method
- Advanced scenarios (virtual environments, development, version pinning)
- Terminal-based installation methods
- CI/CD and automation approaches

---

## 📝 Quick Summary

**What you did:**
1. ✅ Installed QGIS
2. ✅ Installed Python libraries into QGIS's Python (using console)
3. ✅ Added the GeoPublicHealth plugin repository
4. ✅ Installed the GeoPublicHealth plugin
5. ✅ Verified everything works

**Key takeaway:** Always use QGIS Python Console for installation - it's impossible to use the wrong Python that way!

**Now go make some maps!** 🗺️
