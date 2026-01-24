#!/usr/bin/env bash

# GeoPublicHealth macOS Dependency Installer
#
# This script installs all required dependencies for the GeoPublicHealth QGIS plugin on macOS.
#
# IMPORTANT: This script installs to QGIS's Python, NOT your system Python.
#            QGIS has its own isolated Python separate from Homebrew/Anaconda/system Python.
#            This is correct - dependencies must be installed to QGIS's Python to work.
#
# USAGE:
#   1. Open Terminal
#   2. Navigate to this directory: cd /path/to/GeoPublicHealth
#   3. Run: bash install_mac_dependencies.sh
#
# Override QGIS Python path:
#   QGIS_PYTHON="/Applications/QGIS-LTR.app/Contents/MacOS/bin/python3" bash install_mac_dependencies.sh
#
# Specify log directory:
#   LOG_DIR=/tmp bash install_mac_dependencies.sh

# Strict error handling
set -euo pipefail
IFS=$'\n\t'

# Configuration
LOG_DIR="${LOG_DIR:-.}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/geopublichealth_install_${TIMESTAMP}.log"

# QGIS Python path - can be overridden via environment variable
QGIS_PYTHON="${QGIS_PYTHON:-/Applications/QGIS.app/Contents/MacOS/bin/python3}"

echo "======================================================================"
echo "GeoPublicHealth macOS Dependency Installer"
echo "======================================================================"
echo ""
echo "This script will install dependencies to QGIS's Python environment."
echo "This is separate from your system/Homebrew/Anaconda Python."
echo ""
echo "Log file: $LOG_FILE"
echo ""

# Check if QGIS is installed at specified path
if [ ! -x "$QGIS_PYTHON" ]; then
    echo "QGIS Python not found at: $QGIS_PYTHON" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "Attempting to discover QGIS installation..." | tee -a "$LOG_FILE"

    # Try to find QGIS installation automatically
    candidate=""
    for app in /Applications/QGIS*.app; do
        if [ -d "$app" ]; then
            python_path="$app/Contents/MacOS/bin/python3"
            if [ -x "$python_path" ]; then
                candidate="$python_path"
                break
            fi
        fi
    done

    if [ -n "$candidate" ]; then
        QGIS_PYTHON="$candidate"
        echo "✓ Found QGIS Python at: $QGIS_PYTHON" | tee -a "$LOG_FILE"
    else
        echo "ERROR: Could not find QGIS Python." | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        echo "Please install QGIS first:" | tee -a "$LOG_FILE"
        echo "  https://download.qgis.org/downloads/macos/qgis-macos-pr.dmg" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        echo "Or set QGIS_PYTHON environment variable to the correct path:" | tee -a "$LOG_FILE"
        echo "  QGIS_PYTHON=\"/path/to/QGIS.app/Contents/MacOS/bin/python3\" bash install_mac_dependencies.sh" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        exit 1
    fi
fi

echo "Using QGIS Python: $QGIS_PYTHON" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
"$QGIS_PYTHON" --version 2>&1 | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "======================================================================"
echo "Installing dependencies..."
echo "======================================================================"
echo ""

# Function to install a package with logging
install_package() {
    local package_name=$1
    shift
    local pip_args=("$@")

    echo "----------------------------------------------------------------------" | tee -a "$LOG_FILE"
    echo "Installing $package_name..." | tee -a "$LOG_FILE"
    echo "Running: $QGIS_PYTHON -m pip install ${pip_args[*]}" | tee -a "$LOG_FILE"
    echo "----------------------------------------------------------------------" | tee -a "$LOG_FILE"

    if "$QGIS_PYTHON" -m pip install "${pip_args[@]}" >>"$LOG_FILE" 2>&1; then
        echo "✓ $package_name installed successfully" | tee -a "$LOG_FILE"
        return 0
    else
        echo "✗ $package_name installation failed" | tee -a "$LOG_FILE"
        echo "  See log for details: $LOG_FILE" | tee -a "$LOG_FILE"
        return 1
    fi
}

# Track installation status
FAILED_PACKAGES=""
CRITICAL_FAILED=false

# Install packages (continue even if one fails to see all results)
set +e  # Don't exit on error for package installations

install_package "pip (upgrade)" pip --upgrade || FAILED_PACKAGES="$FAILED_PACKAGES pip"

install_package "numpy" numpy || FAILED_PACKAGES="$FAILED_PACKAGES numpy"

install_package "scipy" scipy || FAILED_PACKAGES="$FAILED_PACKAGES scipy"

install_package "pandas" pandas || FAILED_PACKAGES="$FAILED_PACKAGES pandas"

install_package "libpysal & esda" libpysal esda --no-build-isolation || {
    FAILED_PACKAGES="$FAILED_PACKAGES libpysal/esda"
    CRITICAL_FAILED=true
}

install_package "numba" numba || {
    FAILED_PACKAGES="$FAILED_PACKAGES numba"
    CRITICAL_FAILED=true
}

install_package "matplotlib (optional)" matplotlib || echo "Note: matplotlib is optional, plugin will work without it" | tee -a "$LOG_FILE"

set -e  # Re-enable exit on error

echo ""
echo "======================================================================"
echo "INSTALLATION SUMMARY"
echo "======================================================================"
echo ""
echo "Log file: $LOG_FILE"
echo ""

# Check critical dependencies
echo "Verifying required dependencies..." | tee -a "$LOG_FILE"
echo ""

VERIFY_FAILED=false

# Check libpysal
if "$QGIS_PYTHON" -c "import libpysal" 2>/dev/null; then
    VERSION=$("$QGIS_PYTHON" -c "import libpysal; print(libpysal.__version__)")
    echo "✓ libpysal $VERSION is available" | tee -a "$LOG_FILE"
else
    echo "✗ libpysal is NOT available (REQUIRED)" | tee -a "$LOG_FILE"
    VERIFY_FAILED=true
fi

# Check numba
if "$QGIS_PYTHON" -c "import numba" 2>/dev/null; then
    VERSION=$("$QGIS_PYTHON" -c "import numba; print(numba.__version__)")
    echo "✓ numba $VERSION is available" | tee -a "$LOG_FILE"
else
    echo "✗ numba is NOT available (REQUIRED)" | tee -a "$LOG_FILE"
    VERIFY_FAILED=true
fi

# Check esda
if "$QGIS_PYTHON" -c "import esda" 2>/dev/null; then
    VERSION=$("$QGIS_PYTHON" -c "import esda; print(esda.__version__)")
    echo "✓ esda $VERSION is available" | tee -a "$LOG_FILE"
else
    echo "✗ esda is NOT available (REQUIRED)" | tee -a "$LOG_FILE"
    VERIFY_FAILED=true
fi

echo ""
echo "Optional dependencies:"

# Check matplotlib
if "$QGIS_PYTHON" -c "import matplotlib" 2>/dev/null; then
    VERSION=$("$QGIS_PYTHON" -c "import matplotlib; print(matplotlib.__version__)")
    echo "✓ matplotlib $VERSION is available" | tee -a "$LOG_FILE"
else
    echo "○ matplotlib is not available (plotting features will be disabled)" | tee -a "$LOG_FILE"
fi

echo ""
echo "======================================================================"

if [ "$VERIFY_FAILED" = false ]; then
    echo "SUCCESS! All required dependencies are installed." | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "Next steps:" | tee -a "$LOG_FILE"
    echo "1. Open or restart QGIS" | tee -a "$LOG_FILE"
    echo "2. Go to Plugins > Manage and Install Plugins" | tee -a "$LOG_FILE"
    echo "3. Install the GeoPublicHealth plugin" | tee -a "$LOG_FILE"
    echo "4. Start using GeoPublicHealth!" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "Installation log: $LOG_FILE" | tee -a "$LOG_FILE"
    echo "======================================================================"
    exit 0
else
    echo "INSTALLATION INCOMPLETE" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "Some required dependencies failed to install." | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "Full installation log: $LOG_FILE" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    if [ -n "$FAILED_PACKAGES" ]; then
        echo "Failed packages:$FAILED_PACKAGES" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
    fi
    echo "Try running install_dependencies_console.py from QGIS Python Console" | tee -a "$LOG_FILE"
    echo "Or see INSTALL_MAC.md and MAC_INSTALL_TECHNICAL.md for troubleshooting." | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "If reporting an issue, please attach:" | tee -a "$LOG_FILE"
    echo "  - Log file: $LOG_FILE" | tee -a "$LOG_FILE"
    echo "  - QGIS version: (run: $QGIS_PYTHON -c \"from qgis.core import QgsApplication; print(QgsApplication.version())\")" | tee -a "$LOG_FILE"
    echo "  - macOS version: (run: sw_vers)" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "======================================================================"
    exit 1
fi
