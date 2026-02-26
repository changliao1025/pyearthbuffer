# gcsbuffer Package Design and Restructuring Plan

## Overview

Restructure gcsbuffer as a clean Python package that:
1. Reuses existing pyearth geometry classes (avoiding code duplication)
2. Provides simple, user-friendly imports: `from gcsbuffer import point, line, polygon, polyline`
3. Maintains gcsbuffer-specific functionality (buffer algorithms, raster processing)

## Current State Analysis

### Duplicate Classes (to be removed - already in pyearth)
- [`gcsbuffer/classes/vertex.py`](gcsbuffer/classes/vertex.py) → replace with [`pyearth.toolbox.mesh.point.pypoint`]
- [`gcsbuffer/classes/edge.py`](gcsbuffer/classes/edge.py) → replace with [`pyearth.toolbox.mesh.line.pyline`]
- [`gcsbuffer/classes/polygon.py`](gcsbuffer/classes/polygon.py) → replace with [`pyearth.toolbox.mesh.polygon.pypolygon`]
- [`gcsbuffer/classes/polyline.py`](gcsbuffer/classes/polyline.py) → replace with [`pyearth.toolbox.mesh.polyline.pypolyline`]

### gcsbuffer-Specific Classes (to keep)
- [`gcsbuffer/classes/gcstiff.py`](gcsbuffer/classes/gcstiff.py) - Raster/GeoTIFF buffer processing
- [`gcsbuffer/classes/pycase.py`](gcsbuffer/classes/pycase.py) - Case management (needs review for dependencies)

### Classes to Replace with pyearth
- [`gcsbuffer/classes/vertex.py`](gcsbuffer/classes/vertex.py) → replace with [`pyearth.toolbox.mesh.point.pypoint`]
- [`gcsbuffer/classes/edge.py`](gcsbuffer/classes/edge.py) → replace with [`pyearth.toolbox.mesh.line.pyline`]
- [`gcsbuffer/classes/polygon.py`](gcsbuffer/classes/polygon.py) → replace with [`pyearth.toolbox.mesh.polygon.pypolygon`]
- [`gcsbuffer/classes/polyline.py`](gcsbuffer/classes/polyline.py) → replace with [`pyearth.toolbox.mesh.polyline.pypolyline`]
- [`gcsbuffer/classes/circle.py`](gcsbuffer/classes/circle.py) → replace with [`pyearth.toolbox.mesh.circle.pycircle`]
- [`gcsbuffer/classes/timer.py`](gcsbuffer/classes/timer.py) → replace with [`pyearth.toolbox.date.timer.pytimer`]

### gcsbuffer-Specific Modules (to keep)
- [`gcsbuffer/algorithms/`](gcsbuffer/algorithms/) - Buffer-specific algorithms
  - [`find_minimal_enclosing_polygon.py`](gcsbuffer/algorithms/find_minimal_enclosing_polygon.py)
  - [`split_by_length.py`](gcsbuffer/algorithms/split_by_length.py)
- [`gcsbuffer/formats/`](gcsbuffer/formats/) - Custom format handlers
  - [`save_vertex_as_polygon.py`](gcsbuffer/formats/save_vertex_as_polygon.py)

## Proposed Package Structure

```
gcsbuffer/
├── __init__.py                    # Main package entry point
├── buffer/                        # Buffer-specific classes
│   ├── __init__.py
│   └── raster.py                 # Renamed from gcstiff.py for clarity
├── algorithms/                    # Keep existing
│   ├── __init__.py
│   ├── find_minimal_enclosing_polygon.py
│   └── split_by_length.py
├── formats/                       # Keep existing
│   ├── __init__.py
│   └── save_vertex_as_polygon.py
├── utils/                         # Utility classes (if needed)
│   ├── __init__.py
│   └── case.py                   # Renamed from pycase.py (review if needed)
└── classes/                       # DEPRECATED - to be removed
```

## Class Naming Convention

### File Names
- **Geometry files**: Re-exported from pyearth, no local files needed
  - Import `pypoint` as `point`
  - Import `pyline` as `line`
  - Import `pypolygon` as `polygon`
  - Import `pypolyline` as `polyline`
  - Import `pycircle` as `circle`

- **Buffer-specific files**: Use descriptive names
  - `buffer/raster.py` (renamed from `gcstiff.py` for clarity)

- **Utility files**: Use simple descriptive names (only if not in pyearth)
  - `utils/case.py` (renamed from `pycase.py` - review if actually needed)

### Class Names
- **Imported from pyearth**: Keep original names but provide aliases
  - `pypoint` → aliased as `point`
  - `pyline` → aliased as `line`
  - `pypolygon` → aliased as `polygon`
  - `pypolyline` → aliased as `polyline`
  - `pycircle` → aliased as `circle`
  - `pytimer` → aliased as `timer` (from pyearth.toolbox.date.timer)

- **gcsbuffer-specific**: Use descriptive names
  - `gcstiff` → aliased as `RasterBuffer` for clarity
  - `pycase` → keep as `BufferCase` (review if this is gcsbuffer-specific or should be in pyearth)

## Implementation Plan: Main __init__.py

```python
# gcsbuffer/__init__.py
"""
gcsbuffer: Geographic Coordinate System Buffer Operations

A Python package for creating buffer zones in Geographic Coordinate System (GCS).
Provides buffer operations for:
- Vector data (point, line, polygon, polyline)
- Raster data (binary masks)
"""

__version__ = '0.1.0'
__author__ = 'Chang Liao'

# Import geometry classes from pyearth with simple names
from pyearth.toolbox.mesh.point import pypoint as point
from pyearth.toolbox.mesh.line import pyline as line
from pyearth.toolbox.mesh.polygon import pypolygon as polygon
from pyearth.toolbox.mesh.polyline import pypolyline as polyline
from pyearth.toolbox.mesh.circle import pycircle as circle

# Import timer utility from pyearth
from pyearth.toolbox.date.timer import pytimer as timer

# Import buffer-specific classes
from gcsbuffer.buffer.raster import gcstiff as RasterBuffer

# Import gcsbuffer utilities (if needed)
from gcsbuffer.utils.case import pycase as BufferCase

# Import key algorithms
from gcsbuffer.algorithms.find_minimal_enclosing_polygon import find_minimal_enclosing_polygon
from gcsbuffer.algorithms.split_by_length import split_edge_by_length

# Import format handlers
from gcsbuffer.formats.save_vertex_as_polygon import save_vertex_as_polygon

# Define public API
__all__ = [
    # Core geometry (from pyearth)
    'point',
    'line',
    'polygon',
    'polyline',
    'circle',
    # Utilities (from pyearth)
    'timer',
    # Buffer classes (gcsbuffer-specific)
    'RasterBuffer',
    'BufferCase',
    # Algorithms
    'find_minimal_enclosing_polygon',
    'split_edge_by_length',
    # Formats
    'save_vertex_as_polygon',
]
```


## Implementation Plan: buffer/__init__.py

```python
# gcsbuffer/buffer/__init__.py
"""
Buffer-specific classes for raster operations.
"""

from gcsbuffer.buffer.raster import gcstiff as RasterBuffer

__all__ = ['RasterBuffer']
```

## Implementation Plan: utils/__init__.py

```python
# gcsbuffer/utils/__init__.py
"""
Utility classes specific to gcsbuffer operations.
"""

from gcsbuffer.utils.case import pycase as BufferCase

__all__ = ['BufferCase']
```

## Migration Steps

### Step 1: Create new directory structure
- Create `gcsbuffer/buffer/` directory
- Create `gcsbuffer/utils/` directory (only if keeping pycase)

### Step 2: Move and rename files
- Move `gcstiff.py` → `buffer/raster.py`
- Move `pycase.py` → `utils/case.py` (only if needed)

### Step 3: Update imports in moved files
- Update `buffer/raster.py`: Change vertex/edge/polygon imports to use pyearth classes
- Update `utils/case.py`: Change vertex/edge/polyline/timer imports to use pyearth classes

### Step 4: Create __init__.py files
- Create `gcsbuffer/__init__.py` (main entry point)
- Create `gcsbuffer/buffer/__init__.py`
- Create `gcsbuffer/utils/__init__.py`
- Update `gcsbuffer/algorithms/__init__.py`
- Update `gcsbuffer/formats/__init__.py`

### Step 5: Delete duplicate/redundant files
- Delete `gcsbuffer/classes/vertex.py` (use pyearth.point)
- Delete `gcsbuffer/classes/edge.py` (use pyearth.line)
- Delete `gcsbuffer/classes/polygon.py` (use pyearth.polygon)
- Delete `gcsbuffer/classes/polyline.py` (use pyearth.polyline)
- Delete `gcsbuffer/classes/circle.py` (use pyearth.circle)
- Delete `gcsbuffer/classes/timer.py` (use pyearth.timer)
- Delete `gcsbuffer/classes/__init__.py`
- Remove `gcsbuffer/classes/` directory (after moving remaining files)

### Step 6: Create package configuration
- Create `setup.py` or `pyproject.toml`
- Specify `pyearth` as a required dependency
- Define package metadata

### Step 7: Update examples
- Update `examples/vector/create_point_buffer.py`
- Update `examples/vector/create_edge_buffer.py`
- Update `examples/vector/create_polyline_buffer.py`
- Update `examples/vector/create_polygon_buffer.py`

### Step 8: Update documentation
- Update README.md with new import examples
- Create migration guide for existing users

## Example Usage: Before vs After

### Before (Current)
```python
from pyearth.toolbox.mesh.point import pypoint
from gcsbuffer.classes.vertex import pyvertex
from gcsbuffer.classes.edge import pyedge

# Mixed imports, confusing naming
point0 = {'dLongitude_degree': -73.935242, 'dLatitude_degree': 40.730610}
pVertex_in = pypoint(point0)
pVertex_buffer = pVertex_in.calculate_buffer_zone_circle(10000, sFilename_out='output.geojson')
```

### After (Proposed)
```python
from gcsbuffer import point, circle

# Clean, simple imports
point_data = {'dLongitude_degree': -73.935242, 'dLatitude_degree': 40.730610}
my_point = point(point_data)
buffer_result = my_point.calculate_buffer_zone_circle(10000, sFilename_out='output.geojson')
```

## Class/File Name Mapping Reference

| Current File | Current Class | New Location | New Import |
|-------------|---------------|--------------|------------|
| `classes/vertex.py` | `pyvertex` | ❌ DELETE (use pyearth.point) | `from gcsbuffer import point` |
| `classes/edge.py` | `pyedge` | ❌ DELETE (use pyearth.line) | `from gcsbuffer import line` |
| `classes/polygon.py` | `pypolygon` | ❌ DELETE (use pyearth.polygon) | `from gcsbuffer import polygon` |
| `classes/polyline.py` | `pyflowline` | ❌ DELETE (use pyearth.polyline) | `from gcsbuffer import polyline` |
| `classes/circle.py` | `pycircle` | ❌ DELETE (use pyearth.circle) | `from gcsbuffer import circle` |
| `classes/timer.py` | `pytimer` | ❌ DELETE (use pyearth.timer) | `from gcsbuffer import timer` |
| `classes/gcstiff.py` | `gcstiff` | `buffer/raster.py` | `from gcsbuffer import RasterBuffer` |
| `classes/pycase.py` | `pycase` | `utils/case.py` | `from gcsbuffer import BufferCase` |

## Package Configuration: pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "gcsbuffer"
version = "0.1.0"
description = "Geographic Coordinate System Buffer Operations in Python"
readme = "README.md"
authors = [
    {name = "Chang Liao", email = "your.email@example.com"}
]
license = {text = "BSD-3-Clause"}
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Scientific/Engineering :: GIS",
]
requires-python = ">=3.8"
dependencies = [
    "numpy",
    "gdal",
    "matplotlib",
    "cartopy",
    "pyearth",
    "geographiclib",
    "scipy",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "black",
    "flake8",
]

[project.urls]
Homepage = "https://github.com/changliao/gcsbuffer"
Documentation = "https://gcsbuffer.readthedocs.io"
Repository = "https://github.com/changliao/gcsbuffer"
```

## Benefits of This Design

1. **Maximum Code Reuse**: All geometry classes and timer from pyearth
   - Geometry: point, line, polygon, polyline, circle
   - Utility: timer
2. **Minimal Duplication**: Only maintain gcsbuffer-specific functionality
   - Raster buffer operations (gcstiff → RasterBuffer)
   - Buffer algorithms
   - Format handlers
   - Case management (if truly gcsbuffer-specific)
3. **Clean API**: Simple imports like `from gcsbuffer import point, line, circle, timer`
4. **Clear Separation**: pyearth classes vs gcsbuffer-specific functionality
5. **Backwards Compatible Path**: Can provide deprecated imports during transition
6. **Maintainability**: Minimal code to maintain, rely on well-tested pyearth
7. **Consistent Naming**: Follows Python package conventions

## Next Steps

1. Review and approve this design
2. Switch to Code mode to implement the restructuring
3. Test all examples with new structure
4. Update documentation
5. Create migration guide for existing users

## Summary: What to Keep vs Delete

### ✅ DELETE (all available in pyearth):
- `vertex.py` → use `pyearth.toolbox.mesh.point.pypoint`
- `edge.py` → use `pyearth.toolbox.mesh.line.pyline`
- `polygon.py` → use `pyearth.toolbox.mesh.polygon.pypolygon`
- `polyline.py` → use `pyearth.toolbox.mesh.polyline.pypolyline`
- `circle.py` → use `pyearth.toolbox.mesh.circle.pycircle`
- `timer.py` → use `pyearth.toolbox.date.timer.pytimer`

### ✅ KEEP (gcsbuffer-specific):
- `gcstiff.py` → raster buffer operations (move to `buffer/raster.py`)
- `algorithms/` → buffer-specific algorithms
- `formats/` → format handlers
- `pycase.py` → case management (move to `utils/case.py`, review if needed)

## Questions for Clarification

1. ✅ **RESOLVED**: circle.py can be deleted - pyearth already has pycircle
2. ✅ **RESOLVED**: timer.py can be deleted - pyearth already has pytimer
3. Should we keep `gcstiff` class name or rename to `RasterBuffer` for clarity?
4. Is `pycase` truly gcsbuffer-specific, or should it be moved to pyearth?
5. Should we provide a deprecation period with warnings for old import paths?
6. Should examples be updated to use the new import structure immediately?
