"""
GeoPublicHealth Dependency Installer for QGIS Python Console

RECOMMENDED INSTALLATION METHOD - Run this from QGIS Python Console.

This script is designed to be run directly in the QGIS Python Console, which
automatically ensures dependencies are installed to the correct Python environment.

USAGE:
1. Open QGIS
2. Go to Plugins → Python Console
3. Click "Show Editor" button (icon in toolbar)
4. Click "Open Script" and select this file
5. Click "Run Script" button
6. Wait for installation to complete
7. Restart QGIS

Or paste the code directly into the console (copy everything below the instructions).

Why this method is best:
- Automatically uses QGIS's Python (no environment confusion)
- No need to find or type QGIS Python path
- Works regardless of other Python installations on your Mac
- No Terminal knowledge required
- Can't accidentally install to wrong Python
"""

print("=" * 70)
print("GeoPublicHealth Dependency Installer")
print("=" * 70)
print()
print("Installing dependencies for QGIS Python environment...")
print()

# Import pip
try:
    import pip
except ImportError:
    print("ERROR: pip not found. This should not happen in QGIS.")
    print("Please report this issue.")
    raise

# Check Python environment
import sys
print(f"Python: {sys.executable}")
if "QGIS.app" in sys.executable or "qgis" in sys.executable.lower():
    print("✓ Running in QGIS Python environment (correct!)")
else:
    print("⚠️  Warning: This may not be QGIS Python")
    print("   Recommended: Run this from QGIS Python Console instead")
print()

# Define packages to install
# Format: (name, pip_args, description, required)
packages = [
    ("pip", ["pip", "--upgrade"], "Package installer", True),
    ("numpy", ["numpy"], "Numerical computing", True),
    ("scipy", ["scipy"], "Scientific computing", True),
    ("pandas", ["pandas"], "Data analysis", True),
    (
        "libpysal & esda",
        ["libpysal", "esda", "--no-build-isolation"],
        "Spatial analysis",
        True,
    ),
    ("numba", ["numba"], "Performance optimization", True),
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
skipped = []

for name, pip_args, desc, required in packages:
    print(f"Installing {name}...", end=" ")

    try:
        # Use pip.main() to install - this is the most reliable method
        # when running inside QGIS Python Console
        result = pip.main(["install"] + pip_args)

        if result == 0:
            print("✓")
            installed.append(name)
        else:
            print("✗")
            failed.append(name)
            if required:
                print(f"  Warning: {name} is required for the plugin to work")

    except Exception as e:
        print(f"✗ Error: {e}")
        failed.append(name)
        if required:
            print(f"  Warning: {name} is required for the plugin to work")

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
    print("○ matplotlib not installed - Plotting features will be disabled (optional)")

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
else:
    print("INSTALLATION INCOMPLETE")
    print()
    print("Some required dependencies failed to install.")
    print()
    print("Troubleshooting:")
    print("1. Try running this script again")
    print("2. Close and restart QGIS, then run the script again")
    print("3. See MAC_INSTALL_TECHNICAL.md for advanced troubleshooting")
    print("4. Report the issue: https://github.com/ePublicHealth/GeoPublicHealth/issues")

print("=" * 70)
