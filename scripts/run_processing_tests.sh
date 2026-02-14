#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# If qgis is already available in the active Python env, use it directly.
if python3 -c "import qgis" >/dev/null 2>&1; then
    exec python3 scripts/run_processing_tests.py
fi

# macOS fallback: run tests using the QGIS bundled Python.
if [[ "$(uname -s)" == "Darwin" ]]; then
    QGIS_APP="${QGIS_APP:-/Applications/QGIS.app}"
    QGIS_PYTHON="${QGIS_PYTHON:-$QGIS_APP/Contents/MacOS/python3.12}"

    if [[ ! -x "$QGIS_PYTHON" ]]; then
        echo "QGIS Python not found: $QGIS_PYTHON" >&2
        echo "Set QGIS_PYTHON or QGIS_APP and try again." >&2
        exit 1
    fi

    export PYTHONHOME="${PYTHONHOME:-$QGIS_APP/Contents/Frameworks}"
    export GPH_PLUGIN_PATH="${GPH_PLUGIN_PATH:-$ROOT_DIR}"
    export PYTHONPATH="$GPH_PLUGIN_PATH:$QGIS_APP/Contents/Resources/python:$QGIS_APP/Contents/Resources/python/plugins:$QGIS_APP/Contents/Resources/qgis/python:$QGIS_APP/Contents/Resources/qgis/python/plugins${PYTHONPATH:+:$PYTHONPATH}"

    exec "$QGIS_PYTHON" scripts/run_processing_tests.py
fi

echo "QGIS Python environment not available." >&2
echo "Install/configure QGIS Python or run inside a QGIS-enabled environment." >&2
exit 1
