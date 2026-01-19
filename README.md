# GeoPublicHealth

[![Version](https://img.shields.io/badge/version-0.2.1-blue.svg)](https://github.com/ePublicHealth/GeoPublicHealth/releases/tag/v0.2.1)
[![QGIS](https://img.shields.io/badge/QGIS-3.42.x-green.svg)](https://qgis.org)
[![License](https://img.shields.io/badge/license-GPL--2.0-orange.svg)](LICENSE)
[![Test Status](https://github.com/ePublicHealth/GeoPublicHealth/actions/workflows/test.yml/badge.svg)](https://github.com/ePublicHealth/GeoPublicHealth/actions)

**A QGIS Plugin for Epidemiology and Public Health GIS Analysis**

## Overview

GeoPublicHealth provides a simplified interface within QGIS, tailored for users in epidemiology and public health. It builds upon the foundation laid by the [GeoHealth Plugin](https://github.com/Gustry/GeoHealth) (developed by Etienne Trimaille) and incorporates additional methods highly relevant for applying GIS in public health research and practice.

This plugin aims to integrate and enhance methods similar to those found in the pioneering SIGEpi software, leveraging the power and flexibility of the modern QGIS platform.

## Prerequisites

Before installing the GeoPublicHealth plugin, you need:

1.  **QGIS:** Version **3.42.x Münster** is required.
2.  **Python Dependencies:** The plugin relies on specific Python libraries that must be correctly installed within your QGIS environment:
    * `gdal` (usually included with QGIS/OSGeo4W, target version ~3.10.2)
    * `libpysal` (target version ~4.3.0)
    * `numba` (latest compatible version)

**Note:** The installation methods below are designed to help ensure these dependencies are met.

## Quick Start

### Latest Release

Download the latest version from [GitHub Releases](https://github.com/ePublicHealth/GeoPublicHealth/releases/latest) or install directly from QGIS.

**Latest Version:** [v0.2.1](https://github.com/ePublicHealth/GeoPublicHealth/releases/tag/v0.2.1) - Bug fix release for macOS compatibility

## Installation

Installation involves two main steps: installing the correct QGIS version with dependencies, and then installing the GeoPublicHealth plugin itself.

### Step 1: Install QGIS 3.42.x and Dependencies

#### Windows

Using the OSGeo4W Network Installer is **highly recommended** on Windows to ensure all necessary dependencies (like specific versions of GDAL and PySAL) are installed correctly.

1.  Download the **OSGeo4W Network Installer (64 bit)** from the [QGIS Download Page](https://qgis.org/en/site/forusers/download-windows.html). Find the installer matching QGIS version **3.42.2**. *Direct link provided in original README (check if still valid): `https://download.qgis.org/downloads/QGISQT6-OSGeo4W-3.42.2-2.msi`*
2.  Run the downloaded installer (`.msi` or `.exe`).
3.  Choose **Advanced Install** and click **Next >**.
4.  Select **Install from Internet** and click **Next >**.
5.  Select the Root Install Directory (default recommended) and click **Next >**.
6.  Select Local Package Directory (default recommended) and click **Next >**.
7.  Select your Internet Connection (default recommended) and click **Next >**.
8.  Choose a Download Site (default `https://download.osgeo.org` recommended) and click **Next >**.
9.  In the "Select Packages" screen, search for and select the following packages (ensure the versions match):
    * Search for `qgis`. Expand `Desktop`. Select `qgis: QGIS Desktop`. Ensure the version is `3.42.2-x`. Change "Skip" to the version number to mark it for installation.
    * Search for `gdal`. Expand `Libs`. Select `gdal: The GDAL/OGR library and command line tools`. Ensure the version is `3.10.2-x`. Mark it for installation.
    * Search for `pysal`. Expand `Libs`. Select `python3-libpysal: Core components of PySAL...`. Ensure the version is `4.3.0-x`. Mark it for installation.
10. Click **Next >**.
11. Review the dependencies that will be installed. Keep "Install these packages to meet dependencies" checked. Click **Next >**.
12. Accept the License Agreements if prompted and click **Next >** to begin the download and installation.
13. Once finished, launch QGIS Desktop to ensure it starts correctly.

*You can see a [video of this process here](videos/install.qgis.gdal.pysal.win.2022.06.mp4) (Note: Video from 2022, interface might differ slightly).*

#### macOS

1.  Download the **QGIS macOS Installer** for version **3.42.x** from the [QGIS Download Page](https://qgis.org/en/site/forusers/download-macos.html).
2.  Run the installer (`.dmg` file) and drag the QGIS icon to your Applications folder.
3.  **Important Security Note:** macOS may prevent QGIS from opening initially because it's from an unidentified developer or not notarized. On first launch, **right-click (or Control-click)** the QGIS icon in Applications, choose **Open** from the menu, and then click the **Open** button in the confirmation dialog. You should only need to do this once.
4.  **Install Dependencies (PySAL, Numba):** QGIS on macOS often requires manual installation of some Python packages within its own environment.
    * Start QGIS.
    * Open the **Python Console** (Plugins Menu -> Python Console).
    * Execute the following commands one by one in the console prompt (`>>>`):
        ```python
        import pip
        pip.main(['install', 'pip', '--upgrade'])
        pip.main(['install', 'libpysal==4.3.0']) # Install specific required version
        pip.main(['install', 'numba', '--upgrade'])
        ```
    * Close and restart QGIS after installing these packages.

*(Note: The original README mentioned potential issues requiring XQuartz (`Library not loaded: /opt/X11/lib/libxcb.1.dylib`). This is less common with recent QGIS versions but if you encounter such errors, installing [XQuartz](https://www.xquartz.org/) might help.)*

*You can see a [video of the QGIS and plugin installation process for Mac here](videos/install.qgis.and.geopublichealth.mac.2022.09.mp4) (Note: Video from 2022, interface/versions might differ).*

#### Linux

Install QGIS 3.42.x using your distribution's package manager or follow the instructions for various Linux distributions on the [QGIS Download Page](https://qgis.org/en/site/forusers/alldownloads.html#linux). Ensure that `python3-gdal`, `python3-pysal` (or `python3-libpysal`), and `python3-numba` are installed and accessible within the QGIS Python environment. Package names may vary slightly between distributions.

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
4.  Select the downloaded `geopublichealth*.zip` file
5.  Click **Install Plugin**

#### Option C: Install from GitHub (Development Version)

For the latest development version:

```bash
cd ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
# Or on Windows: %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\
git clone https://github.com/ePublicHealth/GeoPublicHealth.git
```

Then restart QGIS and enable the plugin in the Plugin Manager.

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

### v0.2.1 (2026-01-19)
- **Bug Fix**: Fixed f-string syntax error in autocorrelation dialog that prevented plugin loading on macOS
- Added AGENTS.md for AI coding agent guidance
- Added RELEASE.md for release process documentation
- Set up GitHub Actions for automated testing and releases
- Fixed indentation errors in test files

### v0.2.0 (2025-05-01)
- QGIS 3.42 support and autocorrelation improvements
- Updated dependencies and compatibility

See [all releases](https://github.com/ePublicHealth/GeoPublicHealth/releases) for complete version history.

## Documentation

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