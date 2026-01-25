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
import importlib
import os
import subprocess
import sys
import tempfile
import time
import sysconfig
from collections import deque
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


def resolve_python_executable():
    python_exe = Path(sys.executable)
    candidates = []

    def add_versioned_candidates(base_dir):
        if not base_dir:
            return
        try:
            for candidate in base_dir.glob("python3*"):
                if candidate.is_file() and candidate.name.startswith("python3"):
                    candidates.append(candidate)
        except OSError:
            pass
        bin_dir = base_dir / "bin"
        try:
            for candidate in bin_dir.glob("python3*"):
                if candidate.is_file() and candidate.name.startswith("python3"):
                    candidates.append(candidate)
        except OSError:
            pass

    if python_exe.name.lower().startswith("python"):
        candidates.append(python_exe)

    try:
        qgis_core = importlib.import_module("qgis.core")
        qgis_prefix = Path(qgis_core.QgsApplication.prefixPath())
        candidates.append(qgis_prefix / "bin" / "python3")
        candidates.append(qgis_prefix / "bin" / "python")
        add_versioned_candidates(qgis_prefix)
        add_versioned_candidates(qgis_prefix / "Contents" / "MacOS")
    except Exception:
        pass

    for prefix in {
        sys.exec_prefix,
        sys.prefix,
        getattr(sys, "base_prefix", None),
    }:
        if prefix:
            candidates.append(Path(prefix) / "bin" / "python3")
            candidates.append(Path(prefix) / "bin" / "python")
            add_versioned_candidates(Path(prefix))
            add_versioned_candidates(Path(prefix) / "bin")

    candidates.append(python_exe.parent / "bin" / "python3")
    candidates.append(python_exe.parent / "bin" / "python")
    add_versioned_candidates(python_exe.parent)
    add_versioned_candidates(python_exe.parent / "bin")
    add_versioned_candidates(python_exe.parent.parent)

    for candidate in candidates:
        if candidate and candidate.exists() and candidate.name.startswith("python"):
            return candidate, candidates

    return python_exe, candidates


def resolve_python_home(python_version, qgis_root):
    version_str = f"{python_version.major}.{python_version.minor}"
    candidates = []

    if qgis_root:
        candidates.append(qgis_root / "Contents" / "Frameworks")
        candidates.append(qgis_root / "Contents" / "Resources")

    for prefix in {
        sys.exec_prefix,
        sys.prefix,
        getattr(sys, "base_prefix", None),
    }:
        if prefix:
            candidates.append(Path(prefix))

    candidates.append(python_executable.parent)
    candidates.append(python_executable.parent.parent)

    for base in candidates:
        if not base:
            continue
        lib_path = base / "lib" / f"python{version_str}" / "encodings" / "__init__.py"
        if lib_path.exists():
            return base, candidates
        direct_path = base / f"python{version_str}" / "encodings" / "__init__.py"
        if direct_path.exists():
            return base / f"python{version_str}", candidates

    return None, candidates


python_executable, python_candidates = resolve_python_executable()

# Check Python environment
print(f"Console Python: {sys.executable}")
print(f"Pip target Python: {python_executable}")

qgis_prefix = None
try:
    qgis_core = importlib.import_module("qgis.core")
    qgis_prefix = Path(qgis_core.QgsApplication.prefixPath())
except Exception:
    qgis_prefix = None


def resolve_qgis_app_root(prefix_path):
    if not prefix_path:
        return None
    current = Path(prefix_path)
    while current != current.parent:
        if current.name == "QGIS.app":
            return current
        current = current.parent
    return None


def resolve_qgis_profile_python_dir():
    for path_entry in sys.path:
        try:
            path = Path(path_entry)
        except TypeError:
            continue
        if not path.parts:
            continue
        if path.name == "python" and "profiles" in path.parts:
            return path
    return None


def resolve_scripts_dir():
    candidates = []

    try:
        scripts_path = sysconfig.get_path("scripts")
        if scripts_path:
            candidates.append(Path(scripts_path))
    except Exception:
        pass

    cmd = [
        str(python_executable),
        "-c",
        "import sysconfig; print(sysconfig.get_path('scripts'))",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, env=python_env)
    if result.returncode == 0:
        scripts_path = result.stdout.strip()
        if scripts_path:
            candidates.append(Path(scripts_path))

    if qgis_root:
        candidates.append(qgis_root / "Contents" / "Frameworks" / "bin")
        candidates.append(qgis_root / "Contents" / "MacOS" / "bin")

    for candidate in candidates:
        if candidate:
            return candidate

    return None


python_ok = python_executable.exists() and python_executable.name.startswith("python")
qgis_root = resolve_qgis_app_root(qgis_prefix)
if not qgis_root and "QGIS.app" in str(sys.executable):
    qgis_root = resolve_qgis_app_root(Path(sys.executable))

python_home, python_home_candidates = resolve_python_home(sys.version_info, qgis_root)
python_env = os.environ.copy()
if python_home:
    python_env["PYTHONHOME"] = str(python_home)
qgis_profile_python_dir = resolve_qgis_profile_python_dir()
if qgis_profile_python_dir:
    python_env["PYTHONPATH"] = os.pathsep.join(
        [str(qgis_profile_python_dir)] + [p for p in sys.path if p]
    )
else:
    python_env["PYTHONPATH"] = os.pathsep.join(sys.path)
if python_ok and qgis_root:
    try:
        python_executable.relative_to(qgis_root)
    except ValueError:
        python_ok = False
if python_ok and not python_home:
    python_ok = False

if python_ok:
    print("✓ Running in QGIS Python environment (correct!)")
    if qgis_profile_python_dir:
        print(f"Profile Python path: {qgis_profile_python_dir}")
    scripts_dir = resolve_scripts_dir()
    if scripts_dir:
        try:
            scripts_dir.mkdir(parents=True, exist_ok=True)
            print(f"Scripts directory: {scripts_dir}")
        except OSError:
            print("⚠️  Warning: Could not create scripts directory")
    if qgis_root:
        bin_dirs = [
            qgis_root / "Contents" / "bin",
            qgis_root / "Contents" / "Frameworks" / "bin",
            qgis_root / "Contents" / "MacOS" / "bin",
        ]
        for bin_dir in bin_dirs:
            try:
                bin_dir.mkdir(parents=True, exist_ok=True)
            except OSError:
                print(f"⚠️  Warning: Could not create {bin_dir}")
else:
    print("⚠️  Warning: Could not locate QGIS Python interpreter")
    print("   The script will not run pip to avoid QGIS errors.")
    if python_candidates:
        print("   Candidates checked:")
        for candidate in python_candidates:
            print(f"     - {candidate}")
    if python_home_candidates:
        print("   Python home candidates checked:")
        for candidate in python_home_candidates:
            print(f"     - {candidate}")
    print("   Recommended: Run this from QGIS Python Console instead")
print()


def run_pip_install(packages, timeout=None):
    """
    Run pip install using subprocess for stability.

    Note: We use subprocess with a resolved QGIS Python instead of pip.main()
    because pip.main() is not a stable public API and can break with pip
    upgrades.
    """
    cmd = [
        str(python_executable),
        "-m",
        "pip",
        "install",
        "--no-input",
        "--disable-pip-version-check",
    ] + packages
    last_lines = deque(maxlen=6)

    def should_print_line(line):
        prefixes = (
            "Collecting ",
            "Using cached",
            "Downloading",
            "Building wheel for",
            "Created wheel for",
            "Installing collected packages",
            "Requirement already satisfied",
            "Successfully installed",
            "ERROR:",
            "WARNING:",
        )
        return line.startswith(prefixes)

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n{'=' * 70}\n")
        log.write(f">>> {' '.join(cmd)}\n")
        log.write(f"{'=' * 70}\n")

        try:
            start_time = time.monotonic()
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=python_env,
            )

            if proc.stdout is None:
                error_msg = "Error: failed to capture pip output\n"
                log.write(error_msg)
                return 1, "", error_msg

            while True:
                if timeout and (time.monotonic() - start_time) > timeout:
                    proc.terminate()
                    error_msg = f"Timeout after {timeout} seconds\n"
                    log.write(error_msg)
                    return 1, "", error_msg

                line = proc.stdout.readline()
                if not line:
                    if proc.poll() is not None:
                        break
                    time.sleep(0.1)
                    continue

                log.write(line)
                last_lines.append(line)
                if should_print_line(line.lstrip()):
                    print(f"  {line.rstrip()}")

            return proc.returncode, "".join(last_lines), ""

        except Exception as e:
            error_msg = f"Error: {str(e)}\n"
            log.write(error_msg)
            return 1, "", error_msg


# Define packages to install
# Format: (name, pip_args, description, required, min_version, check_modules)
# IMPORTANT: Order matters!
# - fiona must be installed before geopandas (dependency)
# - geopandas should be installed before libpysal (used by plugin for GeoPackage support)
# - numba must be installed before libpysal/esda (may use during build)
packages = [
    ("pip", ["pip", "--upgrade"], "Package installer", True, None, None),
    ("numpy", ["numpy"], "Numerical computing", True, None, None),
    ("scipy", ["scipy"], "Scientific computing", True, None, None),
    ("pandas", ["pandas"], "Data analysis", True, None, None),
    (
        "shapely",
        ["shapely==2.1.2", "--upgrade", "--force-reinstall", "--no-deps"],
        "Geometry engine",
        True,
        "2.1.2",
        ["shapely"],
    ),
    (
        "fiona",
        ["fiona"],
        "Geospatial file I/O",
        True,
        None,
        ["fiona"],
    ),
    (
        "geopandas",
        ["geopandas"],
        "Geospatial data handling (GeoPackage support)",
        True,
        None,
        ["geopandas"],
    ),
    (
        "numba",
        ["numba", "--no-warn-script-location"],
        "Performance optimization",
        True,
        None,
        ["numba"],
    ),
    (
        "libpysal & esda",
        ["libpysal", "esda", "--no-build-isolation"],
        "Spatial analysis",
        True,
        None,
        ["libpysal", "esda"],
    ),
    (
        "matplotlib",
        ["matplotlib"],
        "Plotting and visualization",
        False,
        None,
        ["matplotlib"],
    ),
]

print("The following packages will be checked/installed:")
for name, _, desc, required, _, _ in packages:
    status = "Required" if required else "Optional"
    print(f"  • {name}: {desc} ({status})")
print()

if not python_ok:
    print("=" * 70)
    print("Installation Aborted")
    print("=" * 70)
    print()
    print("Could not locate the QGIS Python interpreter.")
    print("No packages were installed to avoid QGIS errors.")
    print()
    print("Troubleshooting:")
    print("1. Run this script from the QGIS Python Console")
    print("2. Ensure QGIS is fully installed")
    print("3. See MAC_INSTALL_TECHNICAL.md for advanced troubleshooting")
    print()
    print(f"Log file: {log_path}")
    print("=" * 70)
else:
    print("=" * 70)
    print("Starting installation...")
    print("=" * 70)
    print()

    def check_package_version(module_name, min_version=None):
        """Check if a package is already installed with the required version."""
        cmd = [
            str(python_executable),
            "-c",
            (
                "import importlib; "
                f"module = importlib.import_module('{module_name}'); "
                "print(getattr(module, '__version__', 'unknown'))"
            ),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, env=python_env)
        if result.returncode != 0:
            return False, None

        version = result.stdout.strip()
        if min_version and version != "unknown":
            # Simple string comparison for exact version match
            return version == min_version, version
        return True, version
        return True, version

    installed = []
    failed = []
    skipped = []

    for name, pip_args, desc, required, min_version, check_modules in packages:
        # Check if already installed with correct version
        skip_install = False
        if check_modules:
            all_present = True
            versions = []
            for module in check_modules:
                present, version = check_package_version(
                    module, min_version if module == check_modules[0] else None
                )
                if not present:
                    all_present = False
                    break
                versions.append(f"{module} {version}")

            if all_present:
                skip_install = True
                print(
                    f"Checking {name}... ✓ (already installed: {', '.join(versions)})"
                )
                skipped.append(name)

        if skip_install:
            continue

        print(f"Installing {name}...", end=" ", flush=True)

        if name in ("shapely", "numba") and qgis_profile_python_dir:
            target_dir = str(qgis_profile_python_dir)
            try:
                qgis_profile_python_dir.mkdir(parents=True, exist_ok=True)
            except OSError:
                print()
                print("⚠️  Warning: Could not create profile Python directory")
            pip_args = pip_args + ["--target", target_dir, "--upgrade", "--no-deps"]

        rc, stdout, stderr = run_pip_install(pip_args, timeout=600)

        if rc == 0:
            print("✓")
            installed.append(name)
        else:
            print("✗")
            failed.append(name)
            if required:
                print(f"  Warning: {name} is required for the plugin to work")
            if stdout:
                print("  Output snippet:")
                for line in stdout.splitlines():
                    if line.strip():
                        print(f"    {line}")
            print(f"  See log for details: {log_path}")

    print()
    print("=" * 70)
    print("Installation Summary")
    print("=" * 70)
    print()

    if skipped:
        print(f"○ Already installed ({len(skipped)}):")
        for name in skipped:
            print(f"  • {name}")
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
        if not python_ok:
            return False, ""
        cmd = [
            str(python_executable),
            "-c",
            (
                "import importlib; "
                f"module = importlib.import_module('{module_name}'); "
                "print(getattr(module, '__version__', 'unknown'))"
            ),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, env=python_env)
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
        print("1. Restart QGIS completely (close and reopen)")
        print("2. Install the GeoPublicHealth plugin:")
        print("   - Go to Plugins → Manage and Install Plugins")
        print("   - Search for 'geopublichealth'")
        print("   - Click Install")
        print("3. Start using GeoPublicHealth!")
        print()
        print(f"Installation log saved to: {log_path}")
        print()
        try:
            response = (
                input("Restart QGIS now to reload updated libraries? [Y/n]: ")
                .strip()
                .lower()
            )
        except EOFError:
            response = ""
        if response in {"", "y", "yes"}:
            try:
                qgis_core = importlib.import_module("qgis.core")
                project = qgis_core.QgsProject.instance()
                if project and project.isDirty():
                    try:
                        confirm = (
                            input("Unsaved changes detected. Quit anyway? [y/N]: ")
                            .strip()
                            .lower()
                        )
                    except EOFError:
                        confirm = ""
                    if confirm not in {"y", "yes"}:
                        print("Restart cancelled. Please save your project.")
                    else:
                        qgis_core.QgsApplication.exitQgis()
                else:
                    qgis_core.QgsApplication.exitQgis()
            except Exception:
                print("Unable to restart QGIS automatically.")
    else:
        print("INSTALLATION INCOMPLETE")
        print()
        print("Some required dependencies could not be verified.")
        print()
        print("NOTE: If packages were installed successfully above, the")
        print("verification may fail because QGIS needs to be restarted")
        print("to reload the updated libraries.")
        print()
        print(f"Full installation log: {log_path}")
        print()
        print("Troubleshooting:")
        print("1. Close and restart QGIS, then test imports manually.")
        print("   To test after restart, open QGIS Python Console:")
        print("   - Click 'Show Editor' button")
        print("   - Copy and paste these lines into the editor:")
        print()
        print("import libpysal")
        print("import esda")
        print("import numba")
        print("print('All imports successful!')")
        print()
        print("   - Click 'Run Script' button")
        print("2. If imports still fail, run this script again")
        print("3. See MAC_INSTALL_TECHNICAL.md for advanced troubleshooting")
        print("4. Report the issue with the log file:")
        print("   https://github.com/ePublicHealth/GeoPublicHealth/issues")
        # Note: We don't call sys.exit() here because when run in QGIS Python
        # Console it would raise SystemExit and show a stack trace that confuses
        # users.
        # The script simply finishes with the error message above.

    print("=" * 70)
