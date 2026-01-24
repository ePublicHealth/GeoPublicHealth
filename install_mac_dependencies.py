"""
Installation script for GeoPublicHealth dependencies on macOS.

This script installs all required dependencies for the GeoPublicHealth QGIS plugin.

IMPORTANT: This script MUST be run using QGIS's Python, not your system Python.
           QGIS has its own isolated Python environment separate from:
           - macOS system Python (/usr/bin/python3)
           - Homebrew Python (/opt/homebrew/bin/python3 or /usr/local/bin/python3)
           - Anaconda/Miniconda Python
           - Any other Python installation

USAGE:

Method 1 - Run from QGIS Python Console (RECOMMENDED - Always uses correct Python):
1. Open QGIS
2. Go to Plugins > Python Console
3. Click the "Show Editor" button (icon in console toolbar)
4. Open this file (install_mac_dependencies.py)
5. Click "Run Script" button
6. Restart QGIS when complete

Method 2 - Run from Terminal (ONLY if you use the full QGIS Python path):
   /Applications/QGIS.app/Contents/MacOS/bin/python3 install_mac_dependencies.py

   Optional arguments:
   --python-path PATH    Override Python executable path
   --yes, -y             Skip interactive prompts (for automation)
   --timeout SECONDS     Timeout for each package install (default: none)
   --log PATH            Log file path (default: auto-generated)

   Example for automation:
   /Applications/QGIS.app/Contents/MacOS/bin/python3 install_mac_dependencies.py --yes --log /tmp/install.log

   WARNING: Do NOT run with just "python3" or "python" - this will use the wrong Python!

Method 3 - Paste into QGIS Python Console:
   Copy and paste the entire script into the console
"""

import subprocess
import sys
import os
import argparse
import datetime
from pathlib import Path


def verify_qgis_python(python_exe):
    """Verify we're running with QGIS Python, not system Python."""
    # Check if this looks like QGIS Python
    is_qgis_python = "QGIS.app" in python_exe or "qgis" in python_exe.lower()
    return is_qgis_python


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Install GeoPublicHealth dependencies for macOS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with QGIS Python (recommended):
  /Applications/QGIS.app/Contents/MacOS/bin/python3 install_mac_dependencies.py

  # Non-interactive mode for automation:
  /Applications/QGIS.app/Contents/MacOS/bin/python3 install_mac_dependencies.py --yes --log /tmp/install.log

  # Override QGIS Python path:
  python3 install_mac_dependencies.py --python-path /Applications/QGIS-LTR.app/Contents/MacOS/bin/python3
        """
    )

    parser.add_argument(
        "--python-path",
        help="Path to Python executable to use (default: current Python)",
        default=sys.executable
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip interactive prompts (assume yes)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help="Timeout in seconds for each pip install (default: none)"
    )
    parser.add_argument(
        "--log",
        help="Path to log file (default: ./geopublichealth_install_TIMESTAMP.log)"
    )

    return parser.parse_args()


def install_dependencies():
    """Install all required dependencies for GeoPublicHealth on macOS."""

    # Parse arguments (only when run from command line, not when pasted in console)
    try:
        args = parse_args()
        python_exe = args.python_path
        non_interactive = args.yes
        timeout = args.timeout
        log_file = args.log
    except SystemExit:
        # When pasted into QGIS console, argparse may fail - use defaults
        python_exe = sys.executable
        non_interactive = False
        timeout = None
        log_file = None

    # Determine log file path
    if not log_file:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path(f"./geopublichealth_install_{timestamp}.log").absolute()
    else:
        log_path = Path(log_file).absolute()

    print("=" * 70)
    print("GeoPublicHealth macOS Dependency Installer")
    print("=" * 70)

    # Verify we're using QGIS Python
    is_qgis_python = verify_qgis_python(python_exe)

    print(f"\nPython executable: {python_exe}")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Log file: {log_path}")

    if is_qgis_python:
        print("✓ Running with QGIS Python (correct!)")
    else:
        print("\n" + "!" * 70)
        print("⚠️  WARNING: This may NOT be QGIS's Python!")
        print("!" * 70)
        print("\nYou appear to be running with system/Homebrew/Anaconda Python.")
        print("Dependencies installed here will NOT be available in QGIS.")
        print("\nQGIS Python is usually located at:")
        print("  /Applications/QGIS.app/Contents/MacOS/bin/python3")
        print("\nRECOMMENDED: Run this script from QGIS Python Console instead.")
        print("See installation instructions in README.md or INSTALL_MAC.md")
        print("\n" + "!" * 70)

        if not non_interactive:
            response = input("\nContinue anyway? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("\nInstallation cancelled. Please run from QGIS Python Console.")
                return False
        print("\nProceeding with current Python (you have been warned)...")

    print("\n" + "=" * 70)

    # Define dependencies to install
    # IMPORTANT: Order matters! numba must be installed before libpysal/esda
    # because those packages may use numba during build/installation
    dependencies = [
        ("pip", ["pip", "--upgrade"], "Package installer"),
        ("numpy", ["numpy"], "Numerical computing"),
        ("scipy", ["scipy"], "Scientific computing"),
        ("pandas", ["pandas"], "Data analysis"),
        ("numba", ["numba"], "Performance optimization (Required)"),
        (
            "libpysal & esda",
            ["libpysal", "esda", "--no-build-isolation"],
            "Spatial analysis (Required)",
        ),
        ("matplotlib", ["matplotlib"], "Plotting (Optional)"),
    ]

    print("\nThe following packages will be installed:")
    for name, _, description in dependencies:
        print(f"  • {name}: {description}")

    print("\n" + "=" * 70)
    print("Starting installation...")
    print("=" * 70)

    installed = []
    failed = []

    for name, packages, description in dependencies:
        print(f"\n[{len(installed) + len(failed) + 1}/{len(dependencies)}] Installing {name}...")
        print("-" * 70)

        try:
            # Build the pip install command
            cmd = [python_exe, "-m", "pip", "install"] + packages

            print(f"Running: {' '.join(cmd)}")

            # Write to log
            with open(log_path, "a", encoding="utf-8") as log:
                log.write(f"\n{'='*70}\n")
                log.write(f">>> {' '.join(cmd)}\n")
                log.write(f"{'='*70}\n")

            # Run pip install
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            # Write full output to log
            with open(log_path, "a", encoding="utf-8") as log:
                log.write(result.stdout or "")
                log.write(result.stderr or "")

            # Show abbreviated output to console
            if result.stdout:
                # Only show last few lines to avoid clutter
                lines = result.stdout.strip().split("\n")
                for line in lines[-3:]:
                    if line.strip():
                        print(f"  {line}")

            if result.returncode == 0:
                print(f"✓ {name} installed successfully")
                installed.append(name)
            else:
                print(f"✗ {name} installation failed")
                print(f"  See full log: {log_path}")
                if result.stderr:
                    print("  Error snippet:")
                    for line in result.stderr.strip().split("\n")[-3:]:
                        if line.strip():
                            print(f"    {line}")
                failed.append(name)

        except subprocess.TimeoutExpired:
            error_msg = f"✗ {name} installation timed out (exceeded {timeout} seconds)"
            print(error_msg)
            with open(log_path, "a", encoding="utf-8") as log:
                log.write(f"\n{error_msg}\n")
            failed.append(name)
        except Exception as e:
            error_msg = f"✗ Error installing {name}: {str(e)}"
            print(error_msg)
            with open(log_path, "a", encoding="utf-8") as log:
                log.write(f"\n{error_msg}\n")
            failed.append(name)

    # Summary
    print("\n" + "=" * 70)
    print("INSTALLATION SUMMARY")
    print("=" * 70)
    print(f"\nLog file: {log_path}")

    if installed:
        print(f"\n✓ Successfully installed ({len(installed)}):")
        for name in installed:
            print(f"  • {name}")

    if failed:
        print(f"\n✗ Failed to install ({len(failed)}):")
        for name in failed:
            print(f"  • {name}")
        print(f"\nFull installation log: {log_path}")

    # Verify critical dependencies
    print("\n" + "=" * 70)
    print("VERIFYING REQUIRED DEPENDENCIES")
    print("=" * 70)

    critical = {
        "libpysal": "Spatial analysis",
        "esda": "Exploratory spatial data analysis",
        "numba": "Performance optimization"
    }

    all_critical_ok = True
    for module, description in critical.items():
        try:
            __import__(module)
            print(f"✓ {module} is available - {description}")
        except ImportError:
            print(f"✗ {module} is NOT available - {description}")
            all_critical_ok = False

    # Check optional dependencies
    print("\nOptional dependencies:")
    try:
        import matplotlib

        print(f"✓ matplotlib is available (version {matplotlib.__version__})")
    except ImportError:
        print("○ matplotlib is not available (plotting features will be disabled)")

    # Final message
    print("\n" + "=" * 70)
    if all_critical_ok and not failed:
        print("SUCCESS! All dependencies installed successfully.")
        print("\nNext steps:")
        print("1. Restart QGIS for changes to take effect")
        print("2. Install the GeoPublicHealth plugin from Plugins menu")
        print("3. Start using GeoPublicHealth!")
        print(f"\nInstallation log: {log_path}")
        exit_code = 0
    elif all_critical_ok:
        print("PARTIAL SUCCESS - Core dependencies are installed.")
        print(
            "\nSome optional packages failed, but the plugin should work for basic features."
        )
        print("\nNext steps:")
        print("1. Restart QGIS for changes to take effect")
        print("2. Install the GeoPublicHealth plugin from Plugins menu")
        print(f"\nInstallation log: {log_path}")
        exit_code = 0
    else:
        print("INSTALLATION INCOMPLETE")
        print(
            "\nSome required dependencies failed to install."
        )
        print(f"\nFull installation log: {log_path}")
        print("\nPlease try running install_dependencies_console.py from QGIS Python Console")
        print("Or see INSTALL_MAC.md and MAC_INSTALL_TECHNICAL.md for troubleshooting.")
        print("\nIf reporting an issue, please attach:")
        print(f"  - Log file: {log_path}")
        print(f"  - QGIS version: (run in QGIS console: from qgis.core import QgsApplication; print(QgsApplication.version()))")
        print(f"  - macOS version: (run in terminal: sw_vers)")
        exit_code = 1

    print("=" * 70)

    return exit_code


if __name__ == "__main__":
    # Run the installation
    exit_code = install_dependencies()
    sys.exit(exit_code)
