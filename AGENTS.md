# GeoPublicHealth Agent Development Guide

This document provides essential information for AI coding agents working on the GeoPublicHealth QGIS plugin.

## Project Overview

GeoPublicHealth is a QGIS 3.x plugin for epidemiology and public health GIS analysis. It's written in Python and uses PyQGIS, PyQt5, and spatial analysis libraries.

**Key Technologies:**
- Python 3.x (QGIS 3.42.x compatible)
- PyQGIS API for QGIS integration
- PyQt5 for UI components
- libpysal 4.3.0 for spatial analysis
- GDAL ~3.10.2 for geospatial operations
- NumPy, Numba for numerical operations

**Autocorrelation Coverage:**
- Moran (local/global), Moran Rate, bivariate Moran (global/local), Join Counts (global/local), Local Geary, Getis-Ord G

**Autocorrelation UI Notes:**
- Statistic selector drives contextual help content and summary output panel

## Build, Lint, and Test Commands

### Running Tests

**Run all tests:**
```bash
python test_suite.py
```

**Run a single test:**
```bash
python -m unittest src.test.test_pep8.TestPep8.test_pep8
```

**Run specific test module:**
```bash
python -m unittest discover -s src/test -p "test_*.py"
```

### Test Harness

**Run unit tests (script):**
```bash
./scripts/run_tests.sh
```

**Run unit tests (make):**
```bash
make test
```

### Testing Standards

- Use lightweight mocks instead of full QGIS layers when possible.
- Division by zero in rates returns `None` (not 0).
- Null/invalid inputs in rates return `None` per feature.
- Inequality metrics reject negative values (raise error).
- Variance defaults to population (sample variance only when explicitly requested).

### QGIS Testing Practices (Reference)

- Add unit tests for new functionality and regression tests for bug fixes.
- Keep test data small, reusable, and never modify it in place.
- Prefer deterministic tests and isolate QGIS UI dependencies.
- For Processing algorithms, use the YAML-based algorithm tests and expected outputs with tolerances when needed.

References:
- https://docs.qgis.org/3.40/en/docs/developers_guide/unittesting.html
- https://docs.qgis.org/3.40/en/docs/developers_guide/processingtesting.html

## Architecture & Services

- New analysis logic should live in `src/core/services/`.
- GUI dialogs should call services and avoid heavy computation.
- Processing algorithms should wrap the same service functions for parity.

### Code Style Checking

**Run PEP8 style check:**
```bash
make pep8
```

**PEP8 configuration:**
- Ignores: E203, E121, E122, E123, E124, E125, E126, E127, E128, E402
- Excludes: resources_rc.py, geopublichealth/ui/

### Translation Commands

**Update translation strings:**
```bash
make update-translation-strings
```

**Compile translation strings:**
```bash
make compile-translation-strings
```

**Test translations:**
```bash
make test-translations
```

**Translation stats:**
```bash
make translation-stats
```

## Code Style Guidelines

### File Headers

All Python files must start with UTF-8 encoding declaration and GPL license header:

```python
# -*- coding: utf-8 -*-
"""
/***************************************************************************

                                 GeoPublicHealth
                                 A QGIS plugin

                              -------------------
        begin                : YYYY-MM-DD
        copyright            : (C) YYYY by Author Name
        email                : email@example.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
```

### Import Organization

Imports should be organized in this order:
1. Future imports (from `__future__` or `builtins`)
2. Standard library imports
3. Third-party imports (numpy, libpysal, etc.)
4. PyQt/QGIS imports (group together)
5. Local/plugin imports (GeoPublicHealth.*)

**Example:**
```python
from builtins import str
from uuid import uuid4
from tempfile import NamedTemporaryFile

import numpy as np
import libpysal

from qgis.PyQt.QtCore import QSettings, QVariant
from qgis.PyQt.QtWidgets import QApplication, QDialog
from qgis.core import QgsVectorLayer, Qgis
from qgis.gui import QgsMessageBar

from GeoPublicHealth.src.core.tools import tr
from GeoPublicHealth.src.core.exceptions import GeoPublicHealthException
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `GeoPublicHealthPlugin`, `AutocorrelationDialog`)
- **Functions/Methods**: snake_case (e.g., `create_memory_layer`, `open_main_window`)
- **Variables**: snake_case (e.g., `layer_name`, `coordinate_reference_system`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `PYSAL_AVAILABLE`, `DEFAULT_NUMBER_LINES`)
- **Private methods**: prefix with underscore (e.g., `_run_tests`, `_validate_input`)

### Type Hints

Use type hints for function parameters and return types, especially in newer code:

```python
from typing import Dict, List, Optional, Union, Any, Tuple

def create_memory_layer(
        layer_name: str, 
        geometry: QgsWkbTypes, 
        coordinate_reference_system: Optional[QgsCoordinateReferenceSystem] = None, 
        fields: Optional[QgsFields] = None) -> QgsVectorLayer:
    """Create a vector memory layer."""
    pass
```

### Docstrings

Use Google-style docstrings with type information:

```python
def copy_layer(source, target):
    """Copy a vector layer to another one.

    :param source: The vector layer to copy.
    :type source: QgsVectorLayer

    :param target: The destination.
    :type target: QgsVectorLayer
    """
    pass
```

### Exception Handling

- Custom exceptions inherit from `GeoPublicHealthException`
- Use descriptive exception messages
- All exceptions should be defined in `src/core/exceptions.py`

**Example:**
```python
from GeoPublicHealth.src.core.exceptions import (
    GeoPublicHealthException,
    NoLayerProvidedException,
    DifferentCrsException
)

if not layer:
    raise NoLayerProvidedException()
```

### Translation Support

Always wrap user-facing strings with `tr()` function:

```python
from GeoPublicHealth.src.core.tools import tr

message = tr(u'No layer was provided.')
display_message_bar(tr(u'Error while processing'), Qgis.Critical)
```

### UI Components

- UI files (.ui) are created with Qt Designer
- Generate Python UI files with: `pyuic5 -o output_ui.py input.ui`
- Keep UI logic separate from business logic
- UI classes typically end with `Dialog` (e.g., `AutocorrelationDialog`)

## Project Structure

```
GeoPublicHealth/
├── src/
│   ├── core/            # Core functionality and utilities
│   │   ├── blurring/    # Blurring algorithms
│   │   ├── gis/         # GIS utilities
│   │   └── accessibility/
│   ├── gui/             # GUI dialogs and windows
│   │   ├── analysis/    # Analysis dialogs
│   │   ├── import_gui/  # Import dialogs
│   │   └── export/      # Export dialogs
│   ├── processing_geopublichealth/  # QGIS Processing algorithms
│   ├── datastore/       # Data storage implementations
│   ├── ui/              # Qt Designer .ui files
│   ├── test/            # Unit tests
│   ├── doc/             # Documentation
│   └── utilities/       # Utility functions
├── sample_data/         # Sample data for testing
├── scripts/             # Build and helper scripts
└── docs/                # Documentation files
```

## Common Patterns

### Memory Layer Creation

```python
from GeoPublicHealth.src.core.tools import create_memory_layer
from qgis.core import QgsWkbTypes

layer = create_memory_layer(
    layer_name='my_layer',
    geometry=QgsWkbTypes.Point,
    coordinate_reference_system=source_crs,
    fields=source_fields
)
```

### Warning Suppression for PySAL

```python
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, 
                       message="Objects based on the `Geometry` class will deprecated")
warnings.filterwarnings("ignore", category=ResourceWarning, 
                       message="unclosed file")
```

### Fallback Imports

Always check for optional dependencies:

```python
try:
    import libpysal
    PYSAL_AVAILABLE = True
except ImportError:
    PYSAL_AVAILABLE = False
```

## Important Notes

1. **QGIS Compatibility**: Target QGIS 3.42.x Münster
2. **Python Version**: Python 3.x (bundled with QGIS)
3. **DRY Principle**: Don't Repeat Yourself - reuse existing functions
4. **Testing**: All code changes should include or update tests
5. **PEP8 Compliance**: Code must pass `make pep8` with the project's ignore rules
6. **Localization**: All user-facing strings must be translatable (wrapped in `tr()`)
7. **Qt Compatibility**: Use PyQt5 (or PyQt6 if migrating, but currently PyQt5)
8. **macOS dialogs**: File dialogs fall back to manual path prompts for stability

## Contributing Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b my-new-feature`
3. Make changes following style guidelines
4. Run tests: `python test_suite.py`
5. Run PEP8 check: `make pep8`
6. Commit with descriptive message: `git commit -am 'Add some feature'`
7. Push to branch: `git push origin my-new-feature`
8. Open a Pull Request

## Commit Messages

- Use Conventional Commits (https://www.conventionalcommits.org/).
- Format: `type(scope): short summary`
- Examples: `feat(analysis): add inequality metrics`, `fix(core): handle null rates`, `refactor(gui): extract services`

## Release Packaging Notes

- The plugin zip must contain a top-level folder named `geopublichealth` to match the plugin id.
- Keep the published filename as `geopublichealth.zip` (no version suffix) because QGIS infers the folder name from the zip.
- When building manually, sync files into `build/geopublichealth/`, zip from `build/`, then copy the zip to `installation/geopublichealth.zip`.
- Update `docs/plugins.xml` to point at `installation/geopublichealth.zip` and refresh the `<update_date>`.

## References

- [CONTRIBUTING.md](CONTRIBUTING.md) - Full contribution guidelines
- [PyQGIS Developer Cookbook](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/)
- [QGIS Plugin Structure](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/plugins/plugin_structure.html)
- [PyQt5 Documentation](https://riverbankcomputing.com/software/pyqt/intro)
- [PySAL Documentation](https://pysal.org/)
