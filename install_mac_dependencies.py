"""
Installation script for GeoPublicHealth dependencies on macOS.

This script installs all required dependencies for the GeoPublicHealth QGIS plugin.

USAGE:

Method 1 - Run from QGIS Python Console (Recommended):
1. Open QGIS
2. Go to Plugins > Python Console
3. Click the "Show Editor" button (icon in console toolbar)
4. Open this file (install_mac_dependencies.py)
5. Click "Run Script" button
6. Restart QGIS when complete

Method 2 - Run from Terminal:
   /Applications/QGIS.app/Contents/MacOS/bin/python3 install_mac_dependencies.py

Method 3 - Paste into QGIS Python Console:
   Copy and paste the entire script into the console
"""

import subprocess
import sys


def install_dependencies():
    """Install all required dependencies for GeoPublicHealth on macOS."""

    print("=" * 70)
    print("GeoPublicHealth macOS Dependency Installer")
    print("=" * 70)

    # Get the current Python executable
    python_exe = sys.executable
    print(f"\nUsing Python: {python_exe}")
    print(f"Python version: {sys.version}")

    # Define dependencies to install
    # Order matters: install base packages first, then those that depend on them
    dependencies = [
        ("pip", ["pip", "--upgrade"], "Package installer"),
        ("numpy", ["numpy"], "Numerical computing"),
        ("scipy", ["scipy"], "Scientific computing"),
        ("pandas", ["pandas"], "Data analysis"),
        (
            "libpysal & esda",
            ["libpysal", "esda", "--no-build-isolation"],
            "Spatial analysis (Required)",
        ),
        ("numba", ["numba"], "Performance optimization (Required)"),
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

            print(f"Running: pip install {' '.join(packages)}")

            # Run pip install
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300  # 5 minute timeout
            )

            # Show output
            if result.stdout:
                # Only show last few lines to avoid clutter
                lines = result.stdout.strip().split("\n")
                for line in lines[-5:]:
                    if line.strip():
                        print(f"  {line}")

            if result.returncode == 0:
                print(f"✓ {name} installed successfully")
                installed.append(name)
            else:
                print(f"✗ {name} installation failed")
                if result.stderr:
                    print("Error details:")
                    for line in result.stderr.strip().split("\n")[-5:]:
                        if line.strip():
                            print(f"  {line}")
                failed.append(name)

        except subprocess.TimeoutExpired:
            print(f"✗ {name} installation timed out (took more than 5 minutes)")
            failed.append(name)
        except Exception as e:
            print(f"✗ Error installing {name}: {str(e)}")
            failed.append(name)

    # Summary
    print("\n" + "=" * 70)
    print("INSTALLATION SUMMARY")
    print("=" * 70)

    if installed:
        print(f"\n✓ Successfully installed ({len(installed)}):")
        for name in installed:
            print(f"  • {name}")

    if failed:
        print(f"\n✗ Failed to install ({len(failed)}):")
        for name in failed:
            print(f"  • {name}")

    # Verify critical dependencies
    print("\n" + "=" * 70)
    print("VERIFYING REQUIRED DEPENDENCIES")
    print("=" * 70)

    critical = {"libpysal": "Spatial analysis", "numba": "Performance optimization"}

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
    elif all_critical_ok:
        print("PARTIAL SUCCESS - Core dependencies are installed.")
        print(
            "\nSome optional packages failed, but the plugin should work for basic features."
        )
        print("\nNext steps:")
        print("1. Restart QGIS for changes to take effect")
        print("2. Install the GeoPublicHealth plugin from Plugins menu")
    else:
        print("INSTALLATION INCOMPLETE")
        print(
            "\nSome required dependencies failed to install. Please try manual installation:"
        )
        print("\nOption 1 - Terminal (recommended):")
        print(
            "  /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install libpysal esda numba --no-build-isolation"
        )
        print("\nOption 2 - QGIS Python Console (one command at a time):")
        print("  import pip")
        print("  pip.main(['install', 'libpysal', 'esda', '--no-build-isolation'])")
        print("  pip.main(['install', 'numba'])")

    print("=" * 70)

    return all_critical_ok


if __name__ == "__main__":
    # Run the installation
    install_dependencies()
