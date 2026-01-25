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

Method A - Using GUI (Recommended):
1. Open QGIS
2. Go to Plugins → Python Console
3. Click "Show Editor" button (📝 icon in toolbar)
4. Click "Open Script" (📂 folder icon) and select this file
5. Click "Run Script" (▶️ play button)
6. Wait for installation to complete
7. Restart QGIS

Method B - If you have the file path, run in QGIS Python Console:
exec(open('/path/to/install_dependencies_console.py').read())

Method C - Paste entire script:
Copy everything from line 50 onwards and paste into the console.

IMPORTANT: Do NOT just type the filename in the console - Python will
interpret it as a variable name, not execute the script.

Why this method is best:
- Automatically uses QGIS's Python (no environment confusion)
- No need to find or type QGIS Python path
- Works regardless of other Python installations on your Mac
- No Terminal knowledge required
- Can't accidentally install to wrong Python
"""

import subprocess
import sys
import os
import datetime
from pathlib import Path

# Create log file
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_path = Path(f"./geopublichealth_install_{timestamp}.log").absolute()

print("=" * 70)
print("GeoPublicHealth Dependency Installer")
print("=" * 70)
print()
print("Installing dependencies for QGIS Python environment...")
print(f"Log file: {log_path}")
print()

def resolve_python_executable():
    """
    Find the actual Python executable to use with subprocess.

    When running from QGIS Python Console on macOS, sys.executable points to
    the QGIS application bundle (/Applications/QGIS.app/Contents/MacOS/QGIS),
    not the Python interpreter. This function finds the actual python3 binary.
    """
    python_exe = Path(sys.executable)

    # If sys.executable already looks like Python, use it
    if python_exe.name.lower().startswith("python"):
        return python_exe

    # Check if we're in a macOS QGIS.app bundle
    if "QGIS.app" in str(python_exe):
        # Try common locations for Python in QGIS.app bundle
        qgis_app = str(python_exe)

        # Extract path to QGIS.app
        if "/Contents/MacOS" in qgis_app:
            app_path = qgis_app.split("/Contents/MacOS")[0]
        else:
            app_path = qgis_app

        # Try common Python locations in QGIS.app
        candidates = [
            Path(app_path) / "Contents" / "MacOS" / "bin" / "python3",
            Path(app_path) / "Contents" / "Frameworks" / "Python.framework" / "Versions" / "Current" / "bin" / "python3",
            Path(app_path) / "Contents" / "Resources" / "python" / "bin" / "python3",
        ]

        for candidate in candidates:
            if candidate.exists():
                return candidate

    # Try using sys.exec_prefix
    exec_prefix = Path(sys.exec_prefix)
    candidate = exec_prefix / "bin" / "python3"
    if candidate.exists():
        return candidate

    # Try looking relative to sys.executable
    candidate = python_exe.parent / "bin" / "python3"
    if candidate.exists():
        return candidate

    # Last resort: return sys.executable and hope for the best
    return python_exe


python_executable = resolve_python_executable()

# Check Python environment
print(f"Console Python: {sys.executable}")
print(f"Pip target Python: {python_executable}")
if "QGIS.app" in str(python_executable) and python_executable.name.startswith("python"):
    print("✓ Running in QGIS Python environment (correct!)")
else:
    print("⚠️  Warning: This may not be QGIS Python")
    print("   Recommended: Run this from QGIS Python Console instead")
print()


def run_pip_install(packages, timeout=None):
    """
    Run pip install using subprocess for stability.

    Note: We use subprocess.run with python_executable instead of pip.main()
    because pip.main() is not a stable public API and can break with pip
    upgrades.
    """
    cmd = [str(python_executable), "-m", "pip", "install"] + packages

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


def check_module(module_name):
    """Check if a module is available in the target Python environment."""
    cmd = [
        str(python_executable),
        "-c",
        f"import importlib; module = importlib.import_module('{module_name}'); print(getattr(module, '__version__', 'unknown'))",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return True, result.stdout.strip()
    return False, result.stderr.strip()


all_critical_ok = True
for module, description in critical_packages.items():
    ok, version = check_module(module)
    if ok:
        print(f"✓ {module} {version} - {description}")
    else:
        print(f"✗ {module} NOT FOUND - {description}")
        all_critical_ok = False

print()

# Check optional
ok, version = check_module("matplotlib")
if ok:
    print(f"✓ matplotlib {version} - Plotting (optional)")
else:
    print("matplotlib not installed - plotting disabled (optional)")

print()
print("=" * 70)

if all_critical_ok:
    print("SUCCESS!")
    print()
    print("All required dependencies are installed.")
    print()
    print("Next steps:")
    print("1. ⚠️  CRITICAL: Restart QGIS completely (close and reopen)")
    print("   Dependencies won't be available until you restart!")
    print()
    print("2. Install the GeoPublicHealth plugin:")
    print("   - Go to Plugins → Manage and Install Plugins")
    print("   - Go to Settings tab")
    print("   - ⚠️  CRITICAL: Check 'Show also experimental plugins'")
    print("   - Go to All tab and search for 'geopublichealth'")
    print("   - Click Install")
    print()
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
