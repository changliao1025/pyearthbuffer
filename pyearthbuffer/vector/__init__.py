"""Vector domain geodesic buffer operations."""

from pyearthbuffer.vector.dissolve import (
    dissolve_geometries,
    extract_outer_ring_polygon,
    split_multipolygon_to_polygons,
)
from pyearthbuffer.vector.file import (
    buffer_file,
    buffer_line_file,
    buffer_point_file,
    buffer_polygon_file,
)
from pyearthbuffer.vector.geometry import (
    buffer,
    buffer_line,
    buffer_point,
    buffer_polygon,
)

__all__ = [
    "buffer",
    "buffer_point",
    "buffer_line",
    "buffer_polygon",
    "buffer_file",
    "buffer_point_file",
    "buffer_line_file",
    "buffer_polygon_file",
    "dissolve_geometries",
    "split_multipolygon_to_polygons",
    "extract_outer_ring_polygon",
]
