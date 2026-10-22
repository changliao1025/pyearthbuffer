Frequently Asked Questions
==========================

What units does ``distance`` use?
---------------------------------

Buffer distances are in meters. Coordinates are expected in WGS84 longitude
and latitude degrees.

Does the package reproject input geometries?
--------------------------------------------

No. Inputs must already be expressed as WGS84 longitude/latitude. File output
is labeled EPSG:4326, so using projected or other geographic coordinates
without transforming them first can produce incorrect results.

How do I choose between ``buffer`` and ``buffer_file``?
-------------------------------------------------------

Use ``buffer`` for an in-memory geometry and ``buffer_file`` to process all
features in an OGR-supported vector dataset.

What can I use as an in-memory geometry?
----------------------------------------

Use WKT, a GeoJSON geometry mapping or string, an OGR geometry, or a two-number
``(longitude, latitude)`` pair for a point. Complex coordinate sequences
should be converted to WKT, GeoJSON, or OGR geometry first.

Are raster buffers production-ready?
------------------------------------

No. Raster mask buffering is experimental. See :doc:`raster` for its input
expectations and current workflow.
