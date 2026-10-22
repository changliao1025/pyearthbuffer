Object-Based Geometry API
=========================

The object API is centered on ``pyearthbuffer.buffer``. It detects the OGR
geometry type and returns a polygonal buffer as WKT by default.

.. function:: buffer(geometry, distance, *, num_points=60, output_format="wkt")

   Calculate a geodesic buffer on WGS84.

   :param geometry: WKT string, GeoJSON mapping or string, OGR geometry, or a
                    two-element point coordinate pair ``(longitude, latitude)``.
   :param distance: Positive buffer distance in meters.
   :param num_points: Number of points used to approximate circular arcs.
                      Applies to point buffers; must be at least 3.
   :param output_format: One of ``"wkt"``, ``"geojson"``, or ``"ogr"``.
   :returns: A WKT string, GeoJSON geometry mapping, or cloned OGR geometry.
   :raises TypeError: If the geometry or distance has an unsupported type.
   :raises ValueError: If distance is not positive, input geometry is invalid,
                       or the output format is unsupported.

Supported OGR geometry types are ``POINT``, ``MULTIPOINT``, ``LINESTRING``,
``MULTILINESTRING``, ``POLYGON``, ``MULTIPOLYGON``, and
``GEOMETRYCOLLECTION``. The dispatcher buffers components and unions the
resulting areas for multi-geometries and collections.

Examples
--------

.. code-block:: python

    from pyearthbuffer import buffer

    # Returns WKT by default.
    result_wkt = buffer("POINT (-74.006 40.7128)", distance=1000)

    # Return GeoJSON geometry, not a Feature or FeatureCollection.
    result_geojson = buffer(
        "LINESTRING (-74.006 40.7128, -73.990 40.7200)",
        distance=50,
        output_format="geojson",
    )

Convenience Functions
---------------------

The package also exports geometry-specific helpers:

* ``buffer_point(point, distance, *, num_points=60, output_format="wkt")``
* ``buffer_line(line, distance, *, output_format="wkt")``
* ``buffer_polygon(polygon, distance, *, output_format="wkt")``

Each helper checks that the input is of the expected OGR geometry family, then
uses the same geodesic buffering implementation as ``buffer``.

Input and Coordinate Notes
--------------------------

* Coordinates are interpreted as WGS84 longitude and latitude in degrees and
  should be supplied in that order.
* A raw coordinate pair is interpreted as one point. To represent lines or
  polygons, use WKT, GeoJSON, or an OGR geometry.
* Geometry inputs with a source CRS other than WGS84 are not reprojected.
* Polygon buffering currently uses the exterior ring; polygon holes are not
  retained as interior rings in the output.
