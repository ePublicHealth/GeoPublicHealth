# GeoPublicHealth

[![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)](https://github.com/ePublicHealth/GeoPublicHealth/releases/tag/v0.3.0)
[![QGIS](https://img.shields.io/badge/QGIS-3.42%2B-green.svg)](https://qgis.org)
[![License](https://img.shields.io/badge/license-GPL--2.0-orange.svg)](LICENSE)
[![Test Status](https://github.com/ePublicHealth/GeoPublicHealth/actions/workflows/test.yml/badge.svg)](https://github.com/ePublicHealth/GeoPublicHealth/actions)

**A QGIS Plugin for Epidemiology and Public Health GIS Analysis**

## 📚 Table of Contents

- [✨ Overview](#overview)
- [✅ Prerequisites](#prerequisites)
- [🚀 Quick Start](#quick-start)
- [🧭 Installation](#installation)
- [🧪 Verification](#verification)
- [🛠️ Troubleshooting](#troubleshooting)
- [🧭 Usage](#usage)
- [👩‍💻 Development](#development)
- [🤝 Contributing](#contributing)
- [🐛 Reporting Issues](#reporting-issues)
- [🙏 Credits and Authorship](#credits-and-authorship)
- [🗓️ Changelog](#changelog)
- [📖 Documentation](#documentation)
- [💬 Support](#support)
- [📄 License](#license)

## ✨ Overview

GeoPublicHealth provides a simplified interface within QGIS, tailored for users in epidemiology and public health. It builds upon the foundation laid by the [GeoHealth Plugin](https://github.com/Gustry/GeoHealth) (developed by Etienne Trimaille) and incorporates additional methods highly relevant for applying GIS in public health research and practice.

This plugin aims to integrate and enhance methods similar to those found in the pioneering SIGEpi software, leveraging the power and flexibility of the modern QGIS platform.

Key analysis tools include:
- Spatial autocorrelation: Moran (local/global), Moran rate, bivariate Moran, Join Counts, Local Geary, Getis-Ord G
- Incidence and density mapping workflows
- Composite index building and data blurring utilities
- Autocorrelation UI with dynamic help text and summary output panel

## ✅ Prerequisites

Before installing the GeoPublicHealth plugin, you need:

1.  **QGIS:** Version **3.42.x or newer** is required. Tested with:
    * [QGIS 3.44.6 'Solothurn'](https://download.qgis.org/downloads/QGIS-OSGeo4W-3.44.6-1.msi) (Latest Release) - [macOS](https://download.qgis.org/downloads/macos/qgis-macos-pr.dmg)
    * [QGIS 3.40.14 'Bratislava'](https://download.qgis.org/downloads/QGIS-OSGeo4W-3.40.14-1.msi) (Long Term Release) - Windows only
    * QGIS 3.42.x 'Münster' (minimum supported version)
2.  **Python Dependencies:** The plugin relies on specific Python libraries that must be correctly installed within your QGIS environment:
    * `gdal` (usually included with QGIS/OSGeo4W, version ~3.10.2 or newer) - **Required**
    * `libpysal` (version ~4.3.0) - **Required**
    * `numba` (latest compatible version) - **Required**
    * `matplotlib` (latest compatible version) - **Optional** (enables graphing/plotting features)

**Note:** The installation methods below are designed to help ensure these dependencies are met. See [DEPENDENCIES.md](DEPENDENCIES.md) for detailed dependency information.

## 🚀 Quick Start

1. Install QGIS 3.42+ for your platform.
2. Run `install_dependencies_console.py` from the QGIS Python Console.
3. Restart QGIS.
4. Open **Plugins → GeoPublicHealth**.

**Latest Version:** v0.3.0 (2026-01-25) - LISA map clarity and installer automation

## 🧭 Installation

Installation has two steps: install QGIS, then run the dependency installer script.

### Step 1: Install QGIS

| Version | Release Type | Windows | macOS | Linux |
|---------|--------------|---------|-------|-------|
| **3.44.6 'Solothurn'** | Latest Release (Recommended) | [Download](https://download.qgis.org/downloads/QGIS-OSGeo4W-3.44.6-1.msi) | [Download](https://download.qgis.org/downloads/macos/qgis-macos-pr.dmg) | [See distro links](#linux) |
| **3.40.14 'Bratislava'** | Long Term Release (LTR) | [Download](https://download.qgis.org/downloads/QGIS-OSGeo4W-3.40.14-1.msi) | Not Available* | [See distro links](#linux) |
| **OSGeo4W Installer** | Network Installer (All versions) | [Download](https://download.osgeo.org/osgeo4w/v2/osgeo4w-setup.exe) | - | - |

\* *macOS users should use QGIS 3.44, which is stable and recommended for macOS.*

#### 🪟 Windows (OSGeo4W recommended)

1. Download and run the [OSGeo4W installer](https://download.osgeo.org/osgeo4w/v2/osgeo4w-setup.exe).
2. Choose **Advanced Install** → **Install from Internet**.
3. Select packages:
   - `qgis` (Desktop)
   - `gdal` (Libs)
   - `python3-libpysal` (Libs)
4. Complete installation and launch QGIS once.

*Video walkthrough:* [OSGeo4W install](videos/install.qgis.gdal.pysal.win.2022.06.mp4).

#### 🍎 macOS

1. Install QGIS from the [macOS installer](https://download.qgis.org/downloads/macos/qgis-macos-pr.dmg).
2. Open QGIS once (right‑click → Open on first run).
3. Use the QGIS Python Console for dependencies (do not use system Python).

For the full macOS walkthrough and advanced troubleshooting, see:
- [INSTALL_MAC.md](INSTALL_MAC.md)
- [MAC_INSTALL_TECHNICAL.md](MAC_INSTALL_TECHNICAL.md)

#### 🐧 Linux

Install QGIS from your distro packages and ensure `python3-gdal`, `python3-libpysal` (or `python3-pysal`), and `python3-numba` are available to QGIS.

- [Debian/Ubuntu](https://qgis.org/resources/installation-guide/#debian--ubuntu)
- [Fedora](https://qgis.org/resources/installation-guide/#fedora)
- [Arch](https://qgis.org/resources/installation-guide/#arch-linux)
- [Flatpak](https://qgis.org/resources/installation-guide/#flatpak)

### Step 2: Run the Dependency Installer Script

Run the same script on all platforms:

1. Download `install_dependencies_console.py` from the repo or [direct link](https://raw.githubusercontent.com/ePublicHealth/GeoPublicHealth/refs/heads/main/install_dependencies_console.py).
2. Open **Plugins → Python Console**.
3. Click **Show Editor** → **Open Script** → select `install_dependencies_console.py`.
4. Click **Run Script** and watch progress messages.
5. Restart QGIS.

The script will:
- Enable experimental plugins.
- Add the GeoPublicHealth repository.
- Reload repositories from the network.
- Install required dependencies (`libpysal`, `esda`, `numba`).
- Install the GeoPublicHealth plugin.

Logs are written to `~/GeoPublicHealth/` (Windows: `%TEMP%`).

### Step 3: Install the Plugin (Fallback Only)

Use these steps only if the script did not install the plugin after restart.

**Option A: Repository**
1. Open **Plugins → Manage and Install Plugins… → Settings**.
2. Enable **Show also experimental plugins**.
3. Add repository:
   - Name: `GeoPublicHealth`
   - URL: `https://raw.githubusercontent.com/ePublicHealth/GeoPublicHealth/main/docs/plugins.xml`
4. Search for `geopublichealth` and install.

**Option B: ZIP**
1. Download the latest release from [GitHub Releases](https://github.com/ePublicHealth/GeoPublicHealth/releases/latest).
2. **Plugins → Install from ZIP** → select `geopublichealth.zip`.

### 🧪 Verification

After restarting QGIS, run this in the Python Console:

```python
import libpysal, esda, numba
print(f"✓ libpysal {libpysal.__version__}, esda {esda.__version__}, numba {numba.__version__}")
```

### 🎨 Optional: Matplotlib

Matplotlib enables plots in analysis dialogs.

```python
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "matplotlib"])
```

See [DEPENDENCIES.md](DEPENDENCIES.md) and [UNINSTALL_INSTRUCTIONS.md](UNINSTALL_INSTRUCTIONS.md) for advanced scenarios and cleanup.

## 🛠️ Troubleshooting

### 🧩 Plugin Not Appearing After Installation

If the plugin doesn't appear after installation:

1. **Restart QGIS first:**
   - Settings changes (experimental plugins, repositories) require a full QGIS restart
   - After running `install_dependencies_console.py`, always restart QGIS completely

2. **Check experimental plugins are enabled:**
   - Go to **Plugins** → **Manage and Install Plugins** → **Settings**
   - Ensure **[x] Show also experimental plugins** is checked

3. **Clear cache and reinstall:**
   ```bash
   # macOS
   rm -rf ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/geopublichealth
   rm -rf ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/cache
   
   # Linux
   rm -rf ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/geopublichealth
   rm -rf ~/.local/share/QGIS/QGIS3/profiles/default/cache
   
   # Windows
   rmdir /s /q "%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\geopublichealth"
   rmdir /s /q "%APPDATA%\QGIS\QGIS3\profiles\default\cache"
   ```

4. **Restart QGIS** and reinstall the plugin

### 🧪 ModuleNotFoundError

If you see errors about missing modules:

- **matplotlib**: Optional - see [installation instructions above](#optional-install-matplotlib-for-plotting-features)
- **libpysal, esda, numba**: Required - see [Step 1: Install QGIS and Dependencies](#step-1-install-qgis-and-dependencies)

### 🧰 Python Console Installation Issues

**Important:** When using the QGIS Python Console:
- Run commands **one line at a time** (press Enter after each line)
- Do NOT paste multiple lines at once - this will cause `SyntaxError: multiple statements found`
- Wait for each command to complete before running the next one
- If installation fails with build errors, use the `--no-build-isolation` flag:
  ```python
  import subprocess, sys
  subprocess.run([sys.executable, "-m", "pip", "install", "libpysal", "esda", "--no-build-isolation"])
  ```

### 📌 Other Issues

- Check the [QGIS Python Console](https://docs.qgis.org/latest/en/docs/user_manual/plugins/python_console.html) for detailed error messages
- See [UNINSTALL_INSTRUCTIONS.md](UNINSTALL_INSTRUCTIONS.md) for complete reinstallation guide
- See [DEPENDENCIES.md](DEPENDENCIES.md) for dependency troubleshooting
- Report issues on [GitHub Issues](https://github.com/ePublicHealth/GeoPublicHealth/issues)

## 🧭 Usage

Once installed, the GeoPublicHealth plugin tools and algorithms can typically be accessed via:

* The **Plugins Menu -> GeoPublicHealth**.
* A dedicated **GeoPublicHealth Toolbar** (check View Menu -> Toolbars).
* The **QGIS Processing Toolbox** (under Plugins or GeoPublicHealth).

Refer to specific documentation or tutorials for detailed workflows using the plugin's features.

## 👩‍💻 Development

### 🧑‍💻 For Developers

See [AGENTS.md](AGENTS.md) for development guidelines and coding standards.

See [RELEASE.md](RELEASE.md) for information on the release process.

### ✅ Running Tests

```bash
# Run all tests
python test_suite.py

# Run a single test
python -m unittest src.test.test_pep8.TestPep8.test_pep8

# Run PEP8 style check
make pep8
```

### Building the Plugin

The plugin is automatically built and released using GitHub Actions. To manually build:

```bash
# See RELEASE.md for detailed build instructions
```

## 🤝 Contributing

Contributions are welcome! Please review the [Contribution Guidelines](CONTRIBUTING.md) before starting.

1.  **Fork** the repository on GitHub.
2.  Create your feature branch: `git checkout -b my-new-feature`
3.  Make your changes following the [code style guidelines](AGENTS.md)
4.  Run tests: `python test_suite.py` and `make pep8`
5.  Commit your changes: `git commit -am 'Add some feature'`
6.  Push to the branch: `git push origin my-new-feature`
7.  Open a **Pull Request**

## 🐛 Reporting Issues

Found a bug? Please help us fix it by submitting a detailed issue report.

### Before Submitting A Bug Report

* **Search existing issues:** Check if the problem has already been reported: [GeoPublicHealth Issues](https://github.com/ePublicHealth/GeoPublicHealth/issues)
* If you find a similar issue, add comments there instead of creating a new one.

### How to Submit a Good Bug Report

Create an issue on the [repository issues page](https://github.com/ePublicHealth/GeoPublicHealth/issues) and provide as much detail as possible:

* **Clear Title:** Use a descriptive title summarizing the problem.
* **Steps to Reproduce:** Provide exact steps to reliably reproduce the bug. Include sample data or simplified examples if possible.
* **Observed Behavior:** Describe what actually happened after following the steps.
* **Expected Behavior:** Explain what you expected to happen instead.
* **Screenshots/GIFs:** Visual aids are extremely helpful. Use tools like [LiceCap](http://www.cockos.com/licecap/), [Peek](https://github.com/phw/peek), or similar to record GIFs if possible.
* **Crash Reports/Logs:** If QGIS or the plugin crashed, include the relevant error messages or log output from the QGIS Log Messages Panel (View -> Panels -> Log Messages). Paste logs inside Markdown code blocks or link to a Gist.
* **Context:**
    * Can you consistently reproduce the problem?
    * When did it start happening (e.g., after an update)?
    * Does it happen with specific data, projects, or file types?
* **Your Environment:**
    * QGIS Version (e.g., `QGIS 3.42.2-Münster`)
    * Operating System (e.g., `Windows 11`, `macOS Sonoma 14.4`, `Ubuntu 22.04`)
    * GeoPublicHealth Plugin Version

## 🙏 Credits and Authorship

**GeoPublicHealth Plugin:**

* Conceptual Design and Extension: Dr. Carlos Castillo-Salgado, Johns Hopkins Bloomberg School of Public Health [Global Public Health Observatory](http://gpho.info/)
* Development Lead: [Manuel Vidaurre](https://github.com/mvidaurre), ePublicHealth
* QGIS 3 Migration: [Pai (Supharerk Thawillarp)](https://github.com/raynus)
* Project Support: ePublicHealth

**Based on the original GeoHealth Plugin:**

* Original Author: Etienne Trimaille
* Original Design: UMR Espace-DEV (IRD, UAG, UM2, UR)

## 🗓️ Changelog

### v0.3.0 (2026-01-25)
- Remove unintended transparency on LISA Moran's I layer
- Reload plugin repositories and auto-install GeoPublicHealth in installer
- Add clearer progress feedback during dependency installation

### v0.2.24 (2026-01-25)
- **Critical Fix**: Incidence dialog field comboboxes now populate correctly
- Fixed Case field and Population field combobox initialization
- Automated plugin repository configuration in dependency installer
- Dependency installer now automatically enables experimental plugins
- Improved user experience with clear restart instructions

### v0.2.22 (2026-01-23)
- Autocorrelation UI summary panel and updated layout
- Tooltips for statistic, fields, and join counts inputs

### v0.2.21 (2026-01-23)
- Added significance flags and symbology for global stats

### v0.2.20 (2026-01-23)
- Join counts auto-detect for binary fields

### v0.2.19 (2026-01-23)
- Join counts global/local statistics with thresholding

### v0.2.18 (2026-01-23)
- Moran global and bivariate statistics
- Dynamic help panel updates based on statistic

### v0.2.17–0.2.3 (2026-01-22 to 2026-01-23)
- GeoPackage autocorrelation fixes and CRS handling
- macOS file dialog fallbacks and output path validation
- Output geometry recovery and exception handling fixes

### v0.2.2 (2026-01-22)
- **Critical Bug Fixes**:
  - Fixed spatial autocorrelation for GeoPackage layers
  - Fixed GeoPandas layer reading with `|layername=` parameter
  - Removed unsupported context manager in legacy PySAL code
  - Fixed "No such file or directory" error when reading GeoPackage
  - Fixed UI validation warnings when no layers loaded
- **Installation & Dependencies**:
  - Updated macOS installation instructions with working commands
  - Fixed dependency installation with `--no-build-isolation` flag
  - Added step-by-step libpysal, esda, and matplotlib installation
  - Documented one-line-at-a-time Python Console requirement
- **Improvements**:
  - Full GeoPackage and Shapefile format support
  - Better error messages for format compatibility
  - Enhanced documentation with verified installation methods

### v0.2.1 (2026-01-22)
- **Critical Fixes**: 
  - Fixed plugins.xml configuration for proper QGIS plugin repository integration
  - Fixed module import paths (GeoPublicHealth → geopublichealth) throughout codebase
  - Fixed plugin directory name mismatch issue
  - Fixed display_message_bar API compatibility with QGIS 3.x
  - Made matplotlib dependency optional - plugin now loads without it
- **Improvements**:
  - Added optional_deps.py module for graceful handling of optional dependencies
  - Graphing features now disable gracefully when matplotlib unavailable
  - Updated all 89 import statements for correct module paths
- **Documentation**:
  - Added DEPENDENCIES.md with complete dependency information
  - Added UNINSTALL_INSTRUCTIONS.md for troubleshooting installation issues
  - Added install_matplotlib_in_qgis.py script for easy matplotlib installation
  - Updated README with troubleshooting section
- **Bug Fixes**: 
  - Fixed f-string syntax error in autocorrelation dialog that prevented plugin loading on macOS
  - Fixed TypeError when displaying message bar warnings
- **Development**:
  - Added AGENTS.md for AI coding agent guidance
  - Added RELEASE.md for release process documentation
  - Set up GitHub Actions for automated testing and releases
  - Fixed indentation errors in test files

### v0.2.0 (2025-05-01)
- QGIS 3.42 support and autocorrelation improvements
- Updated dependencies and compatibility

See [all releases](https://github.com/ePublicHealth/GeoPublicHealth/releases) for complete version history.

## 📖 Documentation

### 🧭 Installation Guides
- [INSTALL_MAC.md](INSTALL_MAC.md) - Quick Mac installation guide
- [MAC_INSTALL_TECHNICAL.md](MAC_INSTALL_TECHNICAL.md) - Technical guide: Python environments, advanced troubleshooting
- [DEPENDENCIES.md](DEPENDENCIES.md) - Detailed dependency information and troubleshooting
- [UNINSTALL_INSTRUCTIONS.md](UNINSTALL_INSTRUCTIONS.md) - Complete plugin reinstallation guide

**Installation Scripts:**
- [install_dependencies_console.py](install_dependencies_console.py) - **RECOMMENDED:** Console-first installer (paste/run in QGIS)
- [install_mac_dependencies.py](install_mac_dependencies.py) - Advanced: Terminal/Console hybrid installer
- [install_mac_dependencies.sh](install_mac_dependencies.sh) - Advanced: Shell script for Terminal
- [install_matplotlib_in_qgis.py](install_matplotlib_in_qgis.py) - Optional: Install matplotlib only

### 👩‍💻 Development
- [AGENTS.md](AGENTS.md) - Development guide for AI coding agents
- [RELEASE.md](RELEASE.md) - Release process and versioning
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/ePublicHealth/GeoPublicHealth/issues)
- **Discussions**: Use GitHub Issues for questions and discussions
- **Email**: manuel.vidaurre@gmail.com

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

Copyright (c) 2017-2026 The GeoPublicHealth Contributors and Original Authors.
