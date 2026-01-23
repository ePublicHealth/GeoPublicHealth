"""
Installation script for matplotlib in QGIS Python environment.

Run this script from within QGIS Python Console:
1. Open QGIS
2. Go to Plugins > Python Console
3. Click the "Show Editor" button
4. Open this file
5. Click "Run Script" button

Or paste the code below directly into the QGIS Python Console.
"""

import subprocess
import sys
import os


def install_matplotlib():
    """Install matplotlib using pip in the current Python environment."""

    print("=" * 60)
    print("Installing matplotlib for QGIS...")
    print("=" * 60)

    # Get the current Python executable
    python_exe = sys.executable
    print(f"\nUsing Python: {python_exe}")
    print(f"Python version: {sys.version}")

    # Check if matplotlib is already installed
    try:
        import matplotlib

        print(f"\n✓ matplotlib is already installed (version {matplotlib.__version__})")
        print("  No installation needed!")
        return True
    except ImportError:
        print("\n○ matplotlib is not installed. Installing now...")

    # Try to install matplotlib
    try:
        # Use subprocess to run pip
        print("\nRunning: pip install matplotlib")
        print("-" * 60)

        result = subprocess.run(
            [python_exe, "-m", "pip", "install", "matplotlib"],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        print(result.stdout)
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)

        if result.returncode == 0:
            print("-" * 60)
            print("\n✓ matplotlib installed successfully!")

            # Verify installation
            try:
                import matplotlib

                print(f"✓ Verified: matplotlib version {matplotlib.__version__}")
                print("\nPlease restart QGIS for the changes to take effect.")
                return True
            except ImportError:
                print(
                    "✗ Installation appeared successful but matplotlib cannot be imported."
                )
                print("  Please restart QGIS and try again.")
                return False
        else:
            print("-" * 60)
            print(f"\n✗ Installation failed with return code {result.returncode}")
            print("\nTry installing manually:")
            print(f"  {python_exe} -m pip install --user matplotlib")
            return False

    except subprocess.TimeoutExpired:
        print("\n✗ Installation timed out (took more than 5 minutes)")
        return False
    except Exception as e:
        print(f"\n✗ Error during installation: {str(e)}")
        print(f"\nError type: {type(e).__name__}")
        print("\nYou may need to install matplotlib manually outside of QGIS.")
        return False


if __name__ == "__main__":
    # Run the installation
    success = install_matplotlib()

    if not success:
        print("\n" + "=" * 60)
        print("ALTERNATIVE INSTALLATION METHODS")
        print("=" * 60)
        print("\n1. Using Terminal (recommended):")
        print(f"   {sys.executable} -m pip install --user matplotlib")
        print("\n2. Using conda (if available):")
        print("   conda install -c conda-forge matplotlib")
        print("\n3. Check QGIS documentation for your OS:")
        print("   https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/")
