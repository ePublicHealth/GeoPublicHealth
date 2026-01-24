#!/bin/bash

# GeoPublicHealth macOS Dependency Installer
#
# This script installs all required dependencies for the GeoPublicHealth QGIS plugin on macOS.
#
# USAGE:
#   1. Open Terminal
#   2. Navigate to this directory: cd /path/to/GeoPublicHealth
#   3. Make script executable: chmod +x install_mac_dependencies.sh
#   4. Run: ./install_mac_dependencies.sh
#
# Or run directly:
#   bash install_mac_dependencies.sh

echo "======================================================================"
echo "GeoPublicHealth macOS Dependency Installer"
echo "======================================================================"
echo ""

# QGIS Python path
QGIS_PYTHON="/Applications/QGIS.app/Contents/MacOS/bin/python3"

# Check if QGIS is installed
if [ ! -f "$QGIS_PYTHON" ]; then
    echo "ERROR: QGIS Python not found at $QGIS_PYTHON"
    echo ""
    echo "Please install QGIS first:"
    echo "  https://download.qgis.org/downloads/macos/qgis-macos-pr.dmg"
    echo ""
    exit 1
fi

echo "Using QGIS Python: $QGIS_PYTHON"
echo ""
$QGIS_PYTHON --version
echo ""

echo "======================================================================"
echo "Installing dependencies..."
echo "======================================================================"
echo ""

# Function to install a package
install_package() {
    local package_name=$1
    shift
    local pip_args=("$@")

    echo "----------------------------------------------------------------------"
    echo "Installing $package_name..."
    echo "----------------------------------------------------------------------"

    if "$QGIS_PYTHON" -m pip install "${pip_args[@]}"; then
        echo "✓ $package_name installed successfully"
        return 0
    else
        echo "✗ $package_name installation failed"
        return 1
    fi
}

# Track installation status
FAILED=""

# Install pip upgrade
install_package "pip (upgrade)" pip --upgrade || FAILED="$FAILED pip"

# Install numpy
install_package "numpy" numpy || FAILED="$FAILED numpy"

# Install scipy
install_package "scipy" scipy || FAILED="$FAILED scipy"

# Install pandas
install_package "pandas" pandas || FAILED="$FAILED pandas"

# Install libpysal and esda (with special flag)
install_package "libpysal & esda" libpysal esda --no-build-isolation || FAILED="$FAILED libpysal/esda"

# Install numba
install_package "numba" numba || FAILED="$FAILED numba"

# Install matplotlib (optional)
install_package "matplotlib (optional)" matplotlib || echo "Note: matplotlib is optional, plugin will work without it"

echo ""
echo "======================================================================"
echo "INSTALLATION SUMMARY"
echo "======================================================================"
echo ""

# Check critical dependencies
echo "Verifying required dependencies..."
echo ""

CRITICAL_OK=true

# Check libpysal
if "$QGIS_PYTHON" -c "import libpysal" 2>/dev/null; then
    VERSION=$("$QGIS_PYTHON" -c "import libpysal; print(libpysal.__version__)")
    echo "✓ libpysal $VERSION is available"
else
    echo "✗ libpysal is NOT available (REQUIRED)"
    CRITICAL_OK=false
fi

# Check numba
if "$QGIS_PYTHON" -c "import numba" 2>/dev/null; then
    VERSION=$("$QGIS_PYTHON" -c "import numba; print(numba.__version__)")
    echo "✓ numba $VERSION is available"
else
    echo "✗ numba is NOT available (REQUIRED)"
    CRITICAL_OK=false
fi

# Check esda
if "$QGIS_PYTHON" -c "import esda" 2>/dev/null; then
    VERSION=$("$QGIS_PYTHON" -c "import esda; print(esda.__version__)")
    echo "✓ esda $VERSION is available"
else
    echo "✗ esda is NOT available (REQUIRED)"
    CRITICAL_OK=false
fi

echo ""
echo "Optional dependencies:"

# Check matplotlib
if "$QGIS_PYTHON" -c "import matplotlib" 2>/dev/null; then
    VERSION=$("$QGIS_PYTHON" -c "import matplotlib; print(matplotlib.__version__)")
    echo "✓ matplotlib $VERSION is available"
else
    echo "○ matplotlib is not available (plotting features will be disabled)"
fi

echo ""
echo "======================================================================"

if [ "$CRITICAL_OK" = true ]; then
    echo "SUCCESS! All required dependencies are installed."
    echo ""
    echo "Next steps:"
    echo "1. Open or restart QGIS"
    echo "2. Go to Plugins > Manage and Install Plugins"
    echo "3. Install the GeoPublicHealth plugin"
    echo "4. Start using GeoPublicHealth!"
else
    echo "INSTALLATION INCOMPLETE"
    echo ""
    echo "Some required dependencies failed to install."
    echo ""
    echo "Try manual installation:"
    echo "  $QGIS_PYTHON -m pip install libpysal esda numba --no-build-isolation"
    echo ""
    if [ -n "$FAILED" ]; then
        echo "Failed packages:$FAILED"
        echo ""
    fi
fi

echo "======================================================================"
