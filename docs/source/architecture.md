# Architecture

PyEarthBuffer is organized around two vector workflows: buffering one
in-memory geometry and processing a vector dataset file. Both workflows use
the same geometry dispatcher.

## Public workflow

```text
gcsbuffer(geometry, distance)
    -> normalize geometry input
    -> dispatch on OGR geometry type
    -> calculate geodesic buffer using pyearth
    -> format as WKT, GeoJSON, or OGR geometry

gcsbuffer_file(input_file, output_file, distance)
    -> read features with OGR
    -> call gcsbuffer(geometry, distance) for each feature
    -> optionally dissolve results
    -> write output geometry and attributes with OGR
```

## Package layers

* `pyearthbuffer.core` provides input validation and geometry format conversion.
* `pyearthbuffer.vector.geometry` provides in-memory `gcsbuffer` dispatch.
* `pyearthbuffer.vector.file` provides batch file reading, buffering, and output.
* `pyearthbuffer.vector.dissolve` provides union and polygon decomposition
  helpers.
* `pyearthbuffer.raster` contains separate experimental binary-mask operations.

The vector API relies on `pyearth` geometry classes and GDAL/OGR for geometry
and file handling. Buffer distances are geodesic meters; geometry coordinates
must be WGS84 longitude/latitude.

## Scope

Vector buffering is the primary supported workflow. Raster buffering is not
part of the vector API and remains experimental while its raster alignment,
nodata, performance, and edge-case semantics are refined.
