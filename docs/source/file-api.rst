File-Based Vector API
=====================

Use ``pyearthbuffer.gcsbuffer_file`` to buffer every supported feature in an OGR
vector dataset and write the resulting polygons to another vector dataset.
The function returns the number of output features written.

.. function:: gcsbuffer_file(input_file, output_file, distance, *, dissolve=False, min_area=None, preserve_attributes=True, output_driver=None, overwrite=True, verbose=False)

   Batch-buffer an OGR-supported vector dataset with geodesic distances on WGS84.

   :param input_file: Input vector file path.
   :param output_file: Output vector file path.
   :param distance: Positive buffer distance in meters.
   :param dissolve: Union buffer geometries and write polygon components. In
                    this mode source attributes are not carried through.
   :param min_area: Optional minimum polygon area in square meters. Polygon
                    features below this threshold are skipped.
   :param preserve_attributes: Copy input fields when ``dissolve=False``.
   :param output_driver: OGR output driver name. If omitted, inferred from the
                         output filename; unsupported extensions fall back to GeoJSON.
   :param overwrite: Remove an existing output file before writing.
   :param verbose: Enable progress messages through Python logging.
   :returns: Number of buffered output features.

Example
-------

.. code-block:: python

    from pyearthbuffer import gcsbuffer_file

    count = gcsbuffer_file(
        input_file="roads.geojson",
        output_file="road_buffers.gpkg",
        distance=100,
        dissolve=True,
        verbose=True,
    )
    print(f"Created {count} buffer components")

Convenience Functions
---------------------

The public API also includes ``gcsbuffer_point_file``, ``gcsbuffer_line_file``, and
``gcsbuffer_polygon_file``. These delegate to ``gcsbuffer_file`` with the same
options; they do not currently validate that every feature matches the helper
name. Use ``gcsbuffer_file`` for mixed-geometry datasets.

Important Limitations
---------------------

* Input coordinates are expected to be WGS84 longitude/latitude. The code does
  not reproject source coordinates before calculating buffers.
* Output layers are written with an EPSG:4326 spatial reference.
* If ``dissolve=True``, output features have generated ``id`` and
  ``buffer_dist`` fields rather than original feature attributes.
* Per-feature buffer failures are logged and skipped; check logs and output
  counts when processing important data.
* Polygon area filtering is meaningful for polygon features; non-polygon
  features are not filtered by ``min_area``.
