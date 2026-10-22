Raster Buffering (Experimental)
===============================

Raster buffering is secondary to the package's vector functionality and is
still experimental. The current implementation focuses on binary-mask
GeoTIFF input and uses an intermediate vectorization, geodesic buffer, and
rasterization workflow.

The raster interface is available from ``pyearthbuffer.raster``:

.. code-block:: python

    from pyearthbuffer.raster import RasterBuffer

    raster_buffer = RasterBuffer("binary_mask.tif")
    output_file = raster_buffer.calculate_binary_mask_buffer_zone(
        buffer_radius=1000,
        output_file="buffered_mask.tif",
    )

The input is expected to be a single-band binary mask with values 0 and 1.
Because the current workflow creates intermediate vector and raster files,
large datasets and edge cases should be validated carefully. Raster buffering
is not exposed through the top-level vector API and should not be treated as a
stable substitute for a purpose-built raster distance operation.
