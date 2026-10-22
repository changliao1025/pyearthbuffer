"""pyearthbuffer: Geographic Coordinate System Buffer Operations.

A Python package for creating buffer zones in Geographic Coordinate System (GCS)
using geodesic calculations on the WGS84 ellipsoid.

Example:
    >>> import pyearthbuffer as peb
    >>> # Buffer an in-memory point
    >>> wkt_buf = peb.gcsbuffer("POINT (-74.006 40.7128)", distance=1000.0)
    >>> # Buffer a vector dataset file
    >>> peb.gcsbuffer_file("points.geojson", "points_buffered.geojson", distance=500.0)
"""

__version__ = "0.2.0"
__author__ = "Chang Liao"

# Core geometry classes from pyearth
from pyearth.toolbox.date.timer import pytimer
from pyearth.toolbox.mesh.circle import pycircle
from pyearth.toolbox.mesh.line import pyline
from pyearth.toolbox.mesh.point import pypoint
from pyearth.toolbox.mesh.polygon import pypolygon
from pyearth.toolbox.mesh.polyline import pypolyline

# Vector buffer operations
from pyearthbuffer.vector import (
    gcsbuffer,
    gcsbuffer_file,
    gcsbuffer_line,
    gcsbuffer_line_file,
    gcsbuffer_point,
    gcsbuffer_point_file,
    gcsbuffer_polygon,
    gcsbuffer_polygon_file,
)

__all__ = [
    # Unified buffer operations
    "gcsbuffer",
    "gcsbuffer_file",
    "gcsbuffer_point",
    "gcsbuffer_line",
    "gcsbuffer_polygon",
    "gcsbuffer_point_file",
    "gcsbuffer_line_file",
    "gcsbuffer_polygon_file",
    # Geometry primitives
    "pypoint",
    "pyline",
    "pypolygon",
    "pypolyline",
    "pycircle",
    # Utilities
    "pytimer",
]
