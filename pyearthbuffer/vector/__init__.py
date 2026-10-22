"""Vector domain geodesic buffer operations."""

from pyearthbuffer.vector.dissolve import (
    dissolve_geometries,
    extract_outer_ring_polygon,
    split_multipolygon_to_polygons,
)
from pyearthbuffer.vector.file import (
    gcsbuffer_file,
    gcsbuffer_line_file,
    gcsbuffer_point_file,
    gcsbuffer_polygon_file,
)
from pyearthbuffer.vector.geometry import (
    gcsbuffer,
    gcsbuffer_line,
    gcsbuffer_point,
    gcsbuffer_polygon,
)

__all__ = [
    "gcsbuffer",
    "gcsbuffer_point",
    "gcsbuffer_line",
    "gcsbuffer_polygon",
    "gcsbuffer_file",
    "gcsbuffer_point_file",
    "gcsbuffer_line_file",
    "gcsbuffer_polygon_file",
    "dissolve_geometries",
    "split_multipolygon_to_polygons",
    "extract_outer_ring_polygon",
]
