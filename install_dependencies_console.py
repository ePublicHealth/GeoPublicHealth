# -*- coding: utf-8 -*-
"""
/***************************************************************************

                                 GeoPublicHealth
                                 A QGIS plugin

                              -------------------
        begin                : 2026-01-24
        copyright            : (C) 2026 by Manuel Vidaurre
        email                : manuel.vidaurre@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

GeoPublicHealth Dependency Installer for QGIS Python Console

RECOMMENDED INSTALLATION METHOD - Run this from QGIS Python Console.

This script is designed to be run directly in the QGIS Python Console,
which automatically ensures dependencies are installed to the correct
Python environment.

USAGE:
1. Open QGIS
2. Go to Plugins → Python Console
3. Click "Show Editor" button (icon in toolbar)
4. Click "Open Script" and select this file
5. Click "Run Script" button
6. Wait for installation to complete
7. Restart QGIS

Or paste the code directly into the console (copy everything below the
instructions).

Why this method is best:
- Automatically uses QGIS's Python (no environment confusion)
- No need to find or type QGIS Python path
- Works regardless of other Python installations on your Mac
- No Terminal knowledge required
- Can't accidentally install to wrong Python
"""

import datetime
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Create log file in a writable location
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"geopublichealth_install_{timestamp}.log"
default_log_dir = Path.home() / "GeoPublicHealth"
try:
    default_log_dir.mkdir(parents=True, exist_ok=True)
    log_path = default_log_dir / log_filename
except OSError:
    log_path = Path(tempfile.gettempdir()) / log_filename

print("=" * 70)
print("GeoPublicHealth Dependency Installer")
print("=" * 70)
print()
print("Installing dependencies for QGIS Python environment...")
print(f"Log file: {log_path}")
print()

# Check Python environment
print(f"Python: {sys.executable}")
if "QGIS.app" in sys.executable or "qgis" in sys.executable.lower():
    print("✓ Running in QGIS Python environment (correct!)")
else:
    print("⚠️  Warning: This may not be QGIS Python")
    print("   Recommended: Run this from QGIS Python Console instead")
print()


def run_pip_install(packages, timeout=None):
    """
    Run pip install using subprocess for stability.

    Note: We use subprocess.run with sys.executable instead of pip.main()
    because pip.main() is not a stable public API and can break with pip
    upgrades.
    """
    cmd = [sys.executable, "-m", "pip", "install"] + packages

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n{'=' * 70}\n")
        log.write(f">>> {' '.join(cmd)}\n")
        log.write(f"{'=' * 70}\n")

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            # Write full output to log
            log.write(proc.stdout or "")
            log.write(proc.stderr or "")

            return proc.returncode, proc.stdout, proc.stderr

        except subprocess.TimeoutExpired as e:
            error_msg = f"Timeout after {timeout} seconds\n"
            log.write(error_msg)
            return 1, "", error_msg
        except Exception as e:
            error_msg = f"Error: {str(e)}\n"
            log.write(error_msg)
            return 1, "", error_msg


# Define packages to install
# Format: (name, pip_args, description, required)
# IMPORTANT: Order matters! numba must be installed before libpysal/esda
# because those packages may use numba during build/installation
packages = [
    ("pip", ["pip", "--upgrade"], "Package installer", True),
    ("numpy", ["numpy"], "Numerical computing", True),
    ("scipy", ["scipy"], "Scientific computing", True),
    ("pandas", ["pandas"], "Data analysis", True),
    ("numba", ["numba"], "Performance optimization", True),
    (
        "libpysal & esda",
        ["libpysal", "esda", "--no-build-isolation"],
        "Spatial analysis",
        True,
    ),
    ("matplotlib", ["matplotlib"], "Plotting and visualization", False),
]

print("The following packages will be installed:")
for name, _, desc, required in packages:
    status = "Required" if required else "Optional"
    print(f"  • {name}: {desc} ({status})")
print()

print("=" * 70)
print("Starting installation...")
print("=" * 70)
print()

installed = []
failed = []

for name, pip_args, desc, required in packages:
    print(f"Installing {name}...", end=" ", flush=True)

    rc, stdout, stderr = run_pip_install(pip_args, timeout=600)

    if rc == 0:
        print("✓")
        installed.append(name)
    else:
        print(f"✗")
        failed.append(name)
        if required:
            print(f"  Warning: {name} is required for the plugin to work")
        print(f"  See log for details: {log_path}")

print()
print("=" * 70)
print("Installation Summary")
print("=" * 70)
print()

if installed:
    print(f"✓ Successfully installed ({len(installed)}):")
    for name in installed:
        print(f"  • {name}")
    print()

if failed:
    print(f"✗ Failed to install ({len(failed)}):")
    for name in failed:
        print(f"  • {name}")
    print()
    print(f"Full installation log: {log_path}")
    print()

# Verify critical dependencies
print("=" * 70)
print("Verifying Required Dependencies")
print("=" * 70)
print()

critical_packages = {
    "libpysal": "Spatial analysis library",
    "esda": "Exploratory spatial data analysis",
    "numba": "Performance optimization",
}

all_critical_ok = True
for module, description in critical_packages.items():
    try:
        mod = __import__(module)
        version = getattr(mod, "__version__", "unknown")
        print(f"✓ {module} {version} - {description}")
    except ImportError:
        print(f"✗ {module} NOT FOUND - {description}")
        all_critical_ok = False

print()

# Check optional
try:
    import matplotlib

    print(f"✓ matplotlib {matplotlib.__version__} - Plotting (optional)")
except ImportError:
    print("matplotlib not installed - plotting disabled (optional)")

print()
print("=" * 70)

if all_critical_ok:
    print("SUCCESS!")
    print()
    print("All required dependencies are installed.")
    print()
    print("Next steps:")
    print("1. Restart QGIS completely (close and reopen)")
    print("2. Install the GeoPublicHealth plugin:")
    print("   - Go to Plugins → Manage and Install Plugins")
    print("   - Search for 'geopublichealth'")
    print("   - Click Install")
    print("3. Start using GeoPublicHealth!")
    print()
    print(f"Installation log saved to: {log_path}")
else:
    print("INSTALLATION INCOMPLETE")
    print()
    print("Some required dependencies failed to install.")
    print()
    print(f"Full installation log: {log_path}")
    print()
    print("Troubleshooting:")
    print("1. Try running this script again")
    print("2. Close and restart QGIS, then run the script again")
    print("3. See MAC_INSTALL_TECHNICAL.md for advanced troubleshooting")
    print("4. Report the issue with the log file:")
    print("   https://github.com/ePublicHealth/GeoPublicHealth/issues")
    print()
    print("NOTE: Installation incomplete. Please address the issues above.")
    # Note: We don't call sys.exit() here because when run in QGIS Python
    # Console it would raise SystemExit and show a stack trace that confuses
    # users.
    # The script simply finishes with the error message above.

print("=" * 70)
