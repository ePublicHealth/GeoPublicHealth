# GeoPublicHealth

[![Version](https://img.shields.io/badge/version-0.2.22-blue.svg)](https://github.com/ePublicHealth/GeoPublicHealth/releases/tag/v0.2.22)
[![QGIS](https://img.shields.io/badge/QGIS-3.42%2B-green.svg)](https://qgis.org)
[![License](https://img.shields.io/badge/license-GPL--2.0-orange.svg)](LICENSE)
[![Test Status](https://github.com/ePublicHealth/GeoPublicHealth/actions/workflows/test.yml/badge.svg)](https://github.com/ePublicHealth/GeoPublicHealth/actions)

**A QGIS Plugin for Epidemiology and Public Health GIS Analysis**

## Overview

GeoPublicHealth provides a simplified interface within QGIS, tailored for users in epidemiology and public health. It builds upon the foundation laid by the [GeoHealth Plugin](https://github.com/Gustry/GeoHealth) (developed by Etienne Trimaille) and incorporates additional methods highly relevant for applying GIS in public health research and practice.

This plugin aims to integrate and enhance methods similar to those found in the pioneering SIGEpi software, leveraging the power and flexibility of the modern QGIS platform.

Key analysis tools include:
- Spatial autocorrelation: Moran (local/global), Moran rate, bivariate Moran, Join Counts, Local Geary, Getis-Ord G
- Incidence and density mapping workflows
- Composite index building and data blurring utilities
- Autocorrelation UI with dynamic help text and summary output panel

## Prerequisites

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

## Quick Start

### Latest Release

Download the latest version from [GitHub Releases](https://github.com/ePublicHealth/GeoPublicHealth/releases/latest) or install directly from QGIS.

**Latest Version:** v0.2.22 (2026-01-23) - Autocorrelation UI improvements

## Installation

Installation involves two main steps: installing the correct QGIS version with dependencies, and then installing the GeoPublicHealth plugin itself.

### QGIS Download Links by Version

Choose the QGIS version that best fits your needs:

| Version | Release Type | Windows | macOS | Linux |
|---------|--------------|---------|-------|-------|
| **3.44.6 'Solothurn'** | Latest Release (Recommended) | [Download](https://download.qgis.org/downloads/QGIS-OSGeo4W-3.44.6-1.msi) | [Download](https://download.qgis.org/downloads/macos/qgis-macos-pr.dmg) | [See distro links](#linux) |
| **3.40.14 'Bratislava'** | Long Term Release (LTR) | [Download](https://download.qgis.org/downloads/QGIS-OSGeo4W-3.40.14-1.msi) | Not Available* | [See distro links](#linux) |
| **OSGeo4W Installer** | Network Installer (All versions) | [Download](https://download.osgeo.org/osgeo4w/v2/osgeo4w-setup.exe) | - | - |

\* *macOS users should use QGIS 3.44, which is stable and recommended for macOS.*

### Step 1: Install QGIS and Dependencies

#### Windows

Using the OSGeo4W Network Installer is **highly recommended** on Windows to ensure all necessary dependencies (like specific versions of GDAL and PySAL) are installed correctly.

##### Option A: OSGeo4W Network Installer (Recommended)

1.  Download the **[OSGeo4W Network Installer](https://download.osgeo.org/osgeo4w/v2/osgeo4w-setup.exe)** from the [QGIS Download Page](https://qgis.org/download/)
2.  Run the downloaded `osgeo4w-setup.exe`
3.  Choose **Advanced Install** and click **Next >**
4.  Select **Install from Internet** and click **Next >**
5.  Select the Root Install Directory (default recommended) and click **Next >**
6.  Select Local Package Directory (default recommended) and click **Next >**
7.  Select your Internet Connection (default recommended) and click **Next >**
8.  Choose a Download Site (default `https://download.osgeo.org` recommended) and click **Next >**
9.  In the "Select Packages" screen, search for and select the following packages:
    * Search for `qgis`. Expand `Desktop`. Select `qgis: QGIS Desktop` (latest version or LTR). Change "Skip" to the version number to mark it for installation.
    * Search for `gdal`. Expand `Libs`. Select `gdal: The GDAL/OGR library and command line tools`. Mark it for installation.
    * Search for `pysal`. Expand `Libs`. Select `python3-libpysal: Core components of PySAL...` (version 4.3.0 or newer). Mark it for installation.
10. Click **Next >**
11. Review the dependencies that will be installed. Keep "Install these packages to meet dependencies" checked. Click **Next >**
12. Accept the License Agreements if prompted and click **Next >** to begin the download and installation
13. Once finished, launch QGIS Desktop to ensure it starts correctly

##### Option B: Standalone Installers

For offline installation or sharing on USB/network:

- **Latest Release (3.44):** [Download QGIS 3.44.6](https://download.qgis.org/downloads/QGIS-OSGeo4W-3.44.6-1.msi)
- **Long Term Release (3.40 LTR):** [Download QGIS 3.40.14](https://download.qgis.org/downloads/QGIS-OSGeo4W-3.40.14-1.msi)

After installation, install Python dependencies via Python Console (see macOS instructions below).

*You can see a [video of the OSGeo4W process here](videos/install.qgis.gdal.pysal.win.2022.06.mp4) (Note: Video from 2022, interface might differ slightly).*

#### macOS

> **Quick Start:** For a simplified guide, see [INSTALL_MAC.md](INSTALL_MAC.md)

1.  Download the **[QGIS macOS Installer](https://download.qgis.org/downloads/macos/qgis-macos-pr.dmg)** from the [QGIS Download Page](https://qgis.org/download/)
2.  Run the installer (`.dmg` file) and drag the QGIS icon to your Applications folder
3.  **Important Security Note:** macOS may prevent QGIS from opening initially because it's from an unidentified developer. On first launch, **right-click (or Control-click)** the QGIS icon in Applications, choose **Open** from the menu, and then click the **Open** button in the confirmation dialog. You should only need to do this once.
4.  **Install Dependencies:** Choose one of the following methods (Option A is simplest):

##### Option A: Automated Script (Recommended - Easiest)

Run the automated installer script from QGIS:

1.  Start QGIS
2.  Go to **Plugins → Python Console**
3.  Click the **"Show Editor"** button (icon in console toolbar)
4.  Click **"Open Script"** and select `install_mac_dependencies.py` from where you downloaded/cloned GeoPublicHealth
5.  Click **"Run Script"** button
6.  Wait for installation to complete
7.  Restart QGIS

##### Option B: Terminal One-Liner (Fast)

For users comfortable with Terminal:

```bash
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install numpy scipy pandas libpysal esda numba matplotlib --no-build-isolation
```

Then restart QGIS.

##### Option C: Shell Script

1.  Download or clone this repository
2.  Open Terminal
3.  Navigate to the GeoPublicHealth folder
4.  Run:
    ```bash
    bash install_mac_dependencies.sh
    ```
5.  Restart QGIS

##### Option D: Manual Installation (Most Control)

If you prefer to install packages manually one-by-one:

1.  Start QGIS
2.  Open **Python Console** (Plugins Menu → Python Console)
3.  Run these commands **one at a time** (press Enter after each):
    ```python
    import pip
    pip.main(['install', 'pip', '--upgrade'])
    pip.main(['install', 'numpy'])
    pip.main(['install', 'scipy'])
    pip.main(['install', 'pandas'])
    pip.main(['install', 'libpysal', 'esda', '--no-build-isolation'])
    pip.main(['install', 'numba'])
    pip.main(['install', 'matplotlib'])  # Optional
    ```
4.  Restart QGIS

**Verify Installation:**

After restarting QGIS, open Python Console and run:
```python
import libpysal, esda, numba
print(f"✓ libpysal {libpysal.__version__}, esda {esda.__version__}, numba {numba.__version__}")
```

**Note:** There are no QGIS 3.40 LTR builds available on macOS. QGIS 3.44 is recommended for macOS users.

*(Tip: If you encounter library loading errors, installing [XQuartz](https://www.xquartz.org/) may help, though this is less common with recent QGIS versions.)*

*You can see a [video of the QGIS and plugin installation process for Mac here](videos/install.qgis.and.geopublichealth.mac.2022.09.mp4) (Note: Video from 2022, interface/versions might differ).*

#### Linux

Install QGIS using your distribution's package manager or follow the instructions for various Linux distributions on the [QGIS Download Page](https://qgis.org/download/). 

Common distributions:
- **Debian/Ubuntu**: [Installation Instructions](https://qgis.org/resources/installation-guide/#debian--ubuntu)
- **Fedora**: [Installation Instructions](https://qgis.org/resources/installation-guide/#fedora)
- **Arch Linux**: [Installation Instructions](https://qgis.org/resources/installation-guide/#arch-linux)
- **Flatpak** (universal): [Installation Instructions](https://qgis.org/resources/installation-guide/#flatpak)

Ensure that `python3-gdal`, `python3-pysal` (or `python3-libpysal`), and `python3-numba` are installed and accessible within the QGIS Python environment. Package names may vary slightly between distributions.

### Step 2: Install the GeoPublicHealth Plugin

You have three options to install the plugin:

#### Option A: From QGIS Plugin Repository (Recommended)

1.  Start QGIS (ensure dependencies from Step 1 are installed, especially on macOS).
2.  Go to the **Plugins** menu and select **Manage and Install Plugins…**.
3.  Go to the **Settings** tab.
4.  Ensure the **[x] Show also experimental plugins** checkbox is checked.
5.  Click the **Add…** button to add a new repository.
6.  Set the **Name** to `epipublichealth` (or similar).
7.  Set the **URL** to `https://raw.githubusercontent.com/ePublicHealth/GeoPublicHealth/main/docs/plugins.xml`.
8.  Click **OK**.
9.  Go to the **All** tab.
10. In the **Search** field, type `geopublichealth`.
11. Select the **GeoPublicHealth** plugin from the list.
12. Click the **Install Plugin** button.
13. Once installation is complete, click **Close**.
14. Check that the **GeoPublicHealth** entry now appears in the **Plugins** menu in QGIS.

#### Option B: Install from ZIP (Direct Download)

1.  Download the latest release from [GitHub Releases](https://github.com/ePublicHealth/GeoPublicHealth/releases/latest)
2.  In QGIS, go to **Plugins → Manage and Install Plugins...**
3.  Click on **Install from ZIP**
4.  Select the downloaded `geopublichealth.zip` file
5.  Click **Install Plugin**

#### Option C: Install from GitHub (Development Version)

For the latest development version:

```bash
cd ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
# Or on Windows: %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\
git clone https://github.com/ePublicHealth/GeoPublicHealth.git
```

Then restart QGIS and enable the plugin in the Plugin Manager.

### Optional: Install matplotlib for Plotting Features

matplotlib is optional but enables graphing and plotting features in analysis dialogs. To install:

**Using QGIS Python Console:**

1. Open QGIS
2. Go to **Plugins** → **Python Console**
3. Run these commands **one at a time** (press Enter after each):
   ```python
   import pip
   ```
   ```python
   pip.main(['install', 'matplotlib'])
   ```
4. Restart QGIS
5. **Verify installation:**
   ```python
   import matplotlib
   print(f"matplotlib {matplotlib.__version__} installed!")
   ```

**Note:** Do not paste multiple lines at once in the Python Console. Run each command separately.

See [UNINSTALL_INSTRUCTIONS.md](UNINSTALL_INSTRUCTIONS.md) for more installation options and troubleshooting.

## Troubleshooting

### Plugin Not Appearing After Installation

If the plugin doesn't appear after installation:

1. **Check experimental plugins are enabled:**
   - Go to **Plugins** → **Manage and Install Plugins** → **Settings**
   - Ensure **[x] Show also experimental plugins** is checked

2. **Clear cache and reinstall:**
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

3. **Restart QGIS** and reinstall the plugin

### ModuleNotFoundError

If you see errors about missing modules:

- **matplotlib**: Optional - see [installation instructions above](#optional-install-matplotlib-for-plotting-features)
- **libpysal, esda, numba**: Required - see [Step 1: Install QGIS and Dependencies](#step-1-install-qgis-and-dependencies)

### Python Console Installation Issues

**Important:** When using the QGIS Python Console:
- Run commands **one line at a time** (press Enter after each line)
- Do NOT paste multiple lines at once - this will cause `SyntaxError: multiple statements found`
- Wait for each command to complete before running the next one
- If installation fails with build errors, use the `--no-build-isolation` flag:
  ```python
  pip.main(['install', 'libpysal', 'esda', '--no-build-isolation'])
  ```

### Other Issues

- Check the [QGIS Python Console](https://docs.qgis.org/latest/en/docs/user_manual/plugins/python_console.html) for detailed error messages
- See [UNINSTALL_INSTRUCTIONS.md](UNINSTALL_INSTRUCTIONS.md) for complete reinstallation guide
- See [DEPENDENCIES.md](DEPENDENCIES.md) for dependency troubleshooting
- Report issues on [GitHub Issues](https://github.com/ePublicHealth/GeoPublicHealth/issues)

## Usage

Once installed, the GeoPublicHealth plugin tools and algorithms can typically be accessed via:

* The **Plugins Menu -> GeoPublicHealth**.
* A dedicated **GeoPublicHealth Toolbar** (check View Menu -> Toolbars).
* The **QGIS Processing Toolbox** (under Plugins or GeoPublicHealth).

Refer to specific documentation or tutorials for detailed workflows using the plugin's features.

## Development

### For Developers

See [AGENTS.md](AGENTS.md) for development guidelines and coding standards.

See [RELEASE.md](RELEASE.md) for information on the release process.

### Running Tests

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

## Contributing

Contributions are welcome! Please review the [Contribution Guidelines](CONTRIBUTING.md) before starting.

1.  **Fork** the repository on GitHub.
2.  Create your feature branch: `git checkout -b my-new-feature`
3.  Make your changes following the [code style guidelines](AGENTS.md)
4.  Run tests: `python test_suite.py` and `make pep8`
5.  Commit your changes: `git commit -am 'Add some feature'`
6.  Push to the branch: `git push origin my-new-feature`
7.  Open a **Pull Request**

## Reporting Issues

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

## Credits and Authorship

**GeoPublicHealth Plugin:**

* Conceptual Design and Extension: Dr. Carlos Castillo-Salgado, Johns Hopkins Bloomberg School of Public Health [Global Public Health Observatory](http://gpho.info/)
* Development Lead: [Manuel Vidaurre](https://github.com/mvidaurre), ePublicHealth
* QGIS 3 Migration: [Pai (Supharerk Thawillarp)](https://github.com/raynus)
* Project Support: ePublicHealth

**Based on the original GeoHealth Plugin:**

* Original Author: Etienne Trimaille
* Original Design: UMR Espace-DEV (IRD, UAG, UM2, UR)

## Changelog

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

## Documentation

### Installation
- [INSTALL_MAC.md](INSTALL_MAC.md) - Quick Mac installation guide
- [DEPENDENCIES.md](DEPENDENCIES.md) - Detailed dependency information and troubleshooting
- [UNINSTALL_INSTRUCTIONS.md](UNINSTALL_INSTRUCTIONS.md) - Complete plugin reinstallation guide
- [install_mac_dependencies.py](install_mac_dependencies.py) - Automated Mac dependency installer
- [install_mac_dependencies.sh](install_mac_dependencies.sh) - Shell script for Mac dependencies
- [install_matplotlib_in_qgis.py](install_matplotlib_in_qgis.py) - Script to install matplotlib in QGIS

### Development
- [AGENTS.md](AGENTS.md) - Development guide for AI coding agents
- [RELEASE.md](RELEASE.md) - Release process and versioning
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

## Support

- **Issues**: [GitHub Issues](https://github.com/ePublicHealth/GeoPublicHealth/issues)
- **Discussions**: Use GitHub Issues for questions and discussions
- **Email**: manuel.vidaurre@gmail.com

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

Copyright (c) 2017-2026 The GeoPublicHealth Contributors and Original Authors.
