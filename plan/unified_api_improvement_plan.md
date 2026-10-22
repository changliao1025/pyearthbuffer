# pyearthbuffer Unified API Improvement Plan

## 1. Executive Summary & Context

`pyearthbuffer` is a Python library focused on Geographic Coordinate System (GCS) geodesic buffer operations on the WGS84 ellipsoid.

### Current Challenges
1. **Asymmetric Vector Operations**:
   - Point and Polyline buffering are exposed only as WKT string functions (`create_point_buffer_zone`, `create_polyline_buffer_zone`).
   - Polygon buffering is primarily implemented as a file-level processor (`create_buffer_zone_polygon_file`), while in-memory polygon buffering requires assembling complex internal `pyearth` primitives (`dLon_center`, `dLat_center`, `aLine`, `aPoint`).
   - File-based buffering is only available for polygons; point and polyline datasets cannot currently be buffered directly from files.
2. **Inconsistent API Signatures & Conventions**:
   - Parameter naming mixes Hungarian notation (`sWkt`, `dBuffer_distance_in`, `sFilename_polygon_in`) with Python snake_case (`buffer_radius`, `verbose`).
   - Function naming lacks uniformity: `create_point_buffer_zone` vs `create_buffer_zone_polygon_file`.
3. **Unclear Role of Raster**:
   - Raster buffering (`gcstiff`) currently relies on a vectorization -> per-polygon buffer -> rasterization -> merge pipeline, which has known limitations and bugs (e.g. incorrect `pypolygon` constructor calls).
   - As clarified by project scope, the primary focus is **vector buffering** (both object-based and file-based), while raster handling needs to be decoupled and treated as experimental or deferred until a robust algorithm is established.

---

## 2. Design Principles & Goals

1. **Clear Dual Modality**:
   - **Object-Based (In-Memory Geometries)**: Fast, flexible buffering for individual geometries, WKT strings, GeoJSON dicts/strings, Shapely/OGR geometries, or coordinate sequences.
   - **File-Based (Datasets on Disk)**: Robust, batch-capable processing of vector files (Shapefile, GeoJSON, GeoPackage, etc.), preserving attributes, coordinate systems, and offering dissolve/simplification options.
2. **Unified & Pythonic Interface**:
   - A single, intuitive top-level entry point (`buffer` for objects, `buffer_file` for files) with automatic geometry type detection.
   - Dedicated explicit functions (`buffer_point`, `buffer_line`, `buffer_polygon`) for users who want explicit typing and specialized parameters.
   - Standard keyword arguments: `distance` (in meters), `points` / `resolution`, `dissolve`, `preserve_attributes`.
3. **Three-Tier Architectural Layering**:
   - **Tier 1 (Foundations & Utilities)**: Coordinate validation, format conversion, OGR/WKT helpers, bounding box math.
   - **Tier 2 (Core Geodesic Engines)**: Geodesic buffer calculations on WGS84 for points, polylines, and polygons.
   - **Tier 3 (Public Interfaces & Pipelines)**: Unified `buffer` and `buffer_file` APIs, batch executors, export functions.
4. **Isolate & Decouple Raster Operations**:
   - Keep raster operations isolated in an optional/experimental namespace (`pyearthbuffer.raster` or `pyearthbuffer.experimental.raster`) without blocking or complicating vector core development.

---

## 3. Package Structure

```
pyearthbuffer/
├── __init__.py                  # Public exports: buffer, buffer_file, geometry primitives
├── vector/                      # Vector buffer domain (Core focus)
│   ├── __init__.py              # Exports: buffer, buffer_file, buffer_point, buffer_line, buffer_polygon
│   ├── geometry.py              # Object-based buffer operations & type auto-detection
│   ├── file.py                  # File-based buffer operations & batch file I/O
│   └── dissolve.py              # Dissolve, union, and polygon simplification helpers
├── raster/                      # Raster buffer operations (Experimental / Secondary)
│   ├── __init__.py              # Decoupled raster exports
│   └── binary_mask.py           # Raster mask buffer implementation
└── core/                        # Tier 1 primitives & foundations
    ├── __init__.py
    ├── validation.py            # Coordinate, distance, and geometry validators
    └── formats.py               # WKT, GeoJSON, OGR conversion utilities
```

---

## 4. API Specification

### Part A: Object-Based (Geometry) API (`pyearthbuffer.vector.geometry`)

Provides geodesic buffer operations on in-memory geometric representations.

#### 1. Unified Dispatcher: `buffer(geometry, distance, ...)`
Automatically detects the geometry type and input format (WKT string, GeoJSON mapping, OGR geometry, or coordinate list).

```python
from pyearthbuffer import buffer

# 1. From WKT string
buffer_wkt = buffer("POINT (-74.006 40.7128)", distance=1000.0)

# 2. From coordinate tuple / list (auto-detected as Point)
buffer_geom = buffer((-74.006, 40.7128), distance=1000.0, output_format="geojson")

# 3. LineString buffering
line_wkt = "LINESTRING (-74.006 40.7128, -73.990 40.7200)"
corridor_wkt = buffer(line_wkt, distance=50.0)

# 4. Polygon buffering
poly_wkt = "POLYGON ((-74.0 40.7, -74.0 40.8, -73.9 40.8, -73.9 40.7, -74.0 40.7))"
outer_buffer = buffer(poly_wkt, distance=500.0)
```

**Function Signature:**
```python
def buffer(
    geometry: Union[str, dict, ogr.Geometry, tuple, list],
    distance: float,
    *,
    num_points: int = 60,
    output_format: str = "wkt",  # "wkt", "geojson", "ogr"
) -> Union[str, dict, ogr.Geometry]:
    """Calculate a geodesic buffer zone around a geometric feature.

    Parameters
    ----------
    geometry : str, dict, ogr.Geometry, tuple, list
        Input geometry representation:
        - WKT string (e.g. 'POINT (...)', 'LINESTRING (...)', 'POLYGON (...)')
        - GeoJSON geometry dictionary
        - OGR Geometry instance
        - Coordinate tuple (lon, lat) for point or list of tuples for line/polygon
    distance : float
        Buffer distance in meters on the WGS84 ellipsoid.
    num_points : int, optional
        Number of points approximating circular arcs (default: 60).
    output_format : {"wkt", "geojson", "ogr"}, optional
        Format of the returned buffer geometry (default: "wkt").

    Returns
    -------
    str, dict, or ogr.Geometry
        Buffered geometry in the requested format.
    """
```

#### 2. Specialized Geometry Functions:
- `buffer_point(point, distance, num_points=60, output_format="wkt")`
- `buffer_line(line, distance, num_points=60, output_format="wkt")`
- `buffer_polygon(polygon, distance, output_format="wkt")`

---

### Part B: File-Based API (`pyearthbuffer.vector.file`)

Provides file-to-file batch buffer processing with vector format detection, attribute preservation, and optional dissolve/simplification.

#### 1. Unified Dispatcher: `buffer_file(input_file, output_file, distance, ...)`
Buffers all features in a vector file regardless of geometry type (Points, Lines, Polygons, or Multi-geometries).

```python
from pyearthbuffer import buffer_file

# Buffer points file (e.g. earthquake epicenters)
buffer_file(
    input_file="epicenters.geojson",
    output_file="hazard_zones.geojson",
    distance=10000.0,  # 10 km
    preserve_attributes=True,
)

# Buffer roads file with corridor dissolve
buffer_file(
    input_file="highways.shp",
    output_file="highway_noise_zones.gpkg",
    distance=150.0,
    dissolve=True,
)

# Buffer polygon boundaries with area filter
buffer_file(
    input_file="watersheds.shp",
    output_file="riparian_buffers.shp",
    distance=500.0,
    min_area=1.0e6,  # Skip polygons smaller than 1 km²
    dissolve=False,
    verbose=True,
)
```

**Function Signature:**
```python
def buffer_file(
    input_file: Union[str, Path],
    output_file: Union[str, Path],
    distance: float,
    *,
    dissolve: bool = False,
    min_area: Optional[float] = None,
    preserve_attributes: bool = True,
    output_driver: Optional[str] = None,
    overwrite: bool = True,
    verbose: bool = False,
) -> int:
    """Buffer all features in a vector dataset using geodesic distances on WGS84.

    Parameters
    ----------
    input_file : str or Path
        Source vector file (.shp, .geojson, .gpkg, .kml, etc.).
    output_file : str or Path
        Target vector file (.shp, .geojson, .gpkg, etc.).
    distance : float
        Buffer distance in meters.
    dissolve : bool, default False
        Whether to dissolve/union overlapping buffer polygons into a merged layer.
    min_area : float, optional
        Minimum area threshold in square meters (for polygon inputs). Polygons
        with area smaller than this threshold are skipped.
    preserve_attributes : bool, default True
        If True, copies feature attributes to the output layer (when not dissolved).
    output_driver : str, optional
        GDAL/OGR driver name (auto-detected from file extension if None).
    overwrite : bool, default True
        Whether to overwrite existing output files.
    verbose : bool, default False
        Whether to print progress updates.

    Returns
    -------
    int
        Count of buffered features successfully written.
    """
```

#### 2. Specialized File Functions:
- `buffer_point_file(input_file, output_file, distance, ...)`
- `buffer_line_file(input_file, output_file, distance, ...)`
- `buffer_polygon_file(input_file, output_file, distance, min_area=..., ...)`

---

### Part C: Raster Strategy

Given that the package's primary identity and maturity reside in vector operations:
1. **Decouple from Vector Core**:
   - Move raster logic strictly into `pyearthbuffer.raster` (or `pyearthbuffer.experimental.raster`).
   - Do not require raster dependencies or import raster modules at top-level `__init__.py`.
2. **Document Status**:
   - Explicitly note in `README.md` and module docstrings that raster GCS buffering is under experimental development.
   - Retain `RasterBuffer` / `gcstiff` for existing workflows without advertising it as the core feature until a robust geodesic raster buffering algorithm is finalized.

---

## 5. Clean Modern API (No Legacy Compatibility Burden)

Per architecture rules and design direction, legacy shims, alias assignments, and redundant wrappers are completely removed:
- Old functions (`create_point_buffer_zone`, `create_polyline_buffer_zone`, `create_buffer_zone_polygon_file`) are eliminated in favor of canonical `buffer` and `buffer_file`.
- Raster operations are decoupled from root exports into `pyearthbuffer.raster`.
- Top-level `pyearthbuffer` exposes only clean, modern interfaces: `buffer`, `buffer_file`, `buffer_point`, `buffer_line`, `buffer_polygon`.

---

## 6. Implementation Roadmap

### Phase 1: Tier 1 Core Primitives & Format Helpers (`pyearthbuffer/core/`)
- Extract format parsers (`wkt_to_ogr`, `ogr_to_wkt`, `geojson_to_ogr`, `coords_to_point`).
- Centralize input validation for coordinates, bounding boxes, and positive buffer distances.

### Phase 2: Object-Based Vector Engine (`pyearthbuffer/vector/geometry.py`)
- Implement `buffer_point`, `buffer_line`, and `buffer_polygon` for in-memory geometries.
- Implement top-level dispatcher `buffer(geometry, distance, ...)`.
- Support multiple output formats (`wkt`, `geojson`, `ogr`).

### Phase 3: File-Based Vector Pipeline (`pyearthbuffer/vector/file.py`)
- Generalize vector file reading and writing across all vector geometry types (Points, Lines, Polygons).
- Implement feature attribute preservation and schema copying.
- Implement dissolve/union handling via `_dissolve_buffer_geometries`.
- Implement `buffer_file` with progress reporting.

### Phase 4: Integration, Tests & Documentation
- Expose modern functions in `pyearthbuffer/__init__.py`.
- Author targeted pytest unit tests in `tests/test_vector_geometry.py` and `tests/test_vector_file.py`.
- Update `README.md` with the new unified API examples.
