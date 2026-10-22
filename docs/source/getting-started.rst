Getting Started
===============

PyEarthBuffer creates geodesic buffer zones for vector data using distances in
meters on the WGS84 ellipsoid. Its main interfaces are ``buffer`` for
in-memory geometries and ``buffer_file`` for file-to-file processing.

Installation
============

PyEarthBuffer uses GDAL/OGR and scientific Python dependencies. Conda is
recommended for resolving geospatial packages.

Using Conda (Recommended)
-------------------------

.. code-block:: bash

    conda create -n earthbuffer python=3.12 -c conda-forge
    conda activate earthbuffer
    conda install -c conda-forge gdal numpy scipy geographiclib
    pip install pyearth pyearthbuffer

Using pip
---------

If GDAL and its Python bindings are already installed and available in your
environment:

.. code-block:: bash

    python -m pip install pyearthbuffer

Building from Source
--------------------

.. code-block:: bash

    git clone https://github.com/changliao1025/pyearthbuffer.git
    cd pyearthbuffer
    python -m pip install -e .

Quickstart: Object-Based Buffering
==================================

Pass a WKT geometry, GeoJSON geometry mapping, OGR geometry, or a point
coordinate pair ``(longitude, latitude)`` to ``buffer``. The result defaults
to WKT; request GeoJSON or an OGR geometry with ``output_format``.

.. code-block:: python

    import pyearthbuffer as peb

    # Point coordinates are longitude, latitude; distance is in meters.
    point_buffer = peb.buffer((-74.006, 40.7128), distance=1000)

    line = "LINESTRING (-74.006 40.7128, -73.990 40.7200)"
    corridor = peb.buffer(line, distance=100, output_format="geojson")

    polygon = (
        "POLYGON ((-74.0 40.7, -74.0 40.8, -73.9 40.8, "
        "-73.9 40.7, -74.0 40.7))"
    )
    buffered_polygon = peb.buffer(polygon, distance=500)

Quickstart: File-Based Buffering
================================

.. code-block:: python

    import pyearthbuffer as peb

    written = peb.buffer_file(
        "input_roads.geojson",
        "output_corridors.gpkg",
        distance=100,
        dissolve=False,
        preserve_attributes=True,
    )
    print(f"Wrote {written} buffered features")

File operations use OGR-supported vector formats and currently assume input
coordinates are longitude/latitude in WGS84. The output layer is written in
WGS84. See :doc:`file-api` for options and limitations.

Next Steps
==========

* See :doc:`geometry-api` for supported geometry inputs and output formats.
* See :doc:`file-api` for batch processing, attributes, dissolve, and filtering.
* See :doc:`raster` for the status and limitations of raster buffering.
