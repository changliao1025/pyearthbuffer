# pyearthbuffer

Geographic Coordinate System (GCS) Buffer Operations in Python.

If you find this package useful, please cite it in your work.
You can also support it by [buying me a coffee](https://www.buymeacoffee.com/changliao) or sponsoring it on [GitHub](https://github.com/sponsors/changliao1025).

## Dependencies

`pyearthbuffer` depends on the following packages:

1. `numpy`
2. `gdal`
3. `scipy`
4. `geographiclib`
5. `matplotlib`
6. `cartopy`
7. `pyearth`

## Documentation

Please refer to the [documentation](https://pyearthbuffer.readthedocs.io) for details on how to get started using the `pyearthbuffer` package.

## Installation

`pyearthbuffer` depends on several geospatial packages including `gdal`, which are most reliably installed through `conda`:

```bash
conda install -c conda-forge pyearthbuffer
```

Or install from source in editable mode:

```bash
pip install -e .
```

## Features

`pyearthbuffer` provides geodesic buffer operations on the WGS84 ellipsoid:

1. **Object-based vector buffer (`buffer`)**:
   - Geodesic buffers for Points, LineStrings, Polygons, and Multi-geometries.
   - Accepts WKT strings, GeoJSON mappings, OGR geometries, or coordinate sequences.
   - Formats output as WKT, GeoJSON, or OGR geometry objects.
   - Explicit helpers: `buffer_point`, `buffer_line`, `buffer_polygon`.

2. **File-based vector batch buffer (`buffer_file`)**:
   - Batch-processes GIS vector files (Shapefile, GeoJSON, GeoPackage, etc.).
   - Preserves feature attribute tables and schema.
   - Supports dissolve/union (`dissolve=True`) and polygon area filtering (`min_area`).
   - Explicit helpers: `buffer_point_file`, `buffer_line_file`, `buffer_polygon_file`.

## Quick Start

### 1. In-Memory Geometry Buffering

```python
import pyearthbuffer as peb

# Buffer a point (lon, lat) by 1,000 meters
point_wkt = peb.buffer((-74.006, 40.7128), distance=1000.0)

# Buffer a line corridor to GeoJSON
line_wkt = "LINESTRING (-74.006 40.7128, -73.990 40.7200)"
corridor = peb.buffer(line_wkt, distance=50.0, output_format="geojson")

# Buffer a polygon
poly_wkt = "POLYGON ((-74.0 40.7, -74.0 40.8, -73.9 40.8, -73.9 40.7, -74.0 40.7))"
poly_buffered = peb.buffer(poly_wkt, distance=500.0)
```

### 2. Batch File Buffering

```python
import pyearthbuffer as peb

# Buffer an entire vector dataset file
peb.buffer_file(
    input_file="input_roads.geojson",
    output_file="output_corridors.shp",
    distance=100.0,
    dissolve=True,  # Merge overlapping buffer zones
    preserve_attributes=True,
)
```

## Acknowledgment

This research was supported as part of the Next Generation Ecosystem Experiments-Tropics, funded by the U.S. Department of Energy, Office of Science, Office of Biological and Environmental Research at Pacific Northwest National Laboratory. The study was also partly supported by U.S. Department of Energy Office of Science Biological and Environmental Research through the Earth and Environmental System Modeling program as part of the Energy Exascale Earth System Model (E3SM) project.

## License

BSD 3-Clause License. See [LICENSE.md](LICENSE.md) for details.
