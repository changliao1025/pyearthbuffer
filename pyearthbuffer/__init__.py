"""
pyearthbuffer: Geographic Coordinate System Buffer Operations

A Python package for creating buffer zones in Geographic Coordinate System (GCS).
Provides buffer operations for:
- Vector data (point, line, polygon, polyline)
- Raster data (binary masks)

Example:
    >>> from pyearthbuffer import point, line, polygon, circle
    >>> point_data = {'dLongitude_degree': -73.935242, 'dLatitude_degree': 40.730610}
    >>> my_point = point(point_data)
    >>> buffer_result = my_point.calculate_buffer_zone_circle(10000, sFilename_out='output.geojson')
"""

__version__ = '0.1.0'
__author__ = 'Chang Liao'

# Import geometry classes from pyearth with simple names
from pyearth.toolbox.mesh.point import pypoint
from pyearth.toolbox.mesh.line import pyline
from pyearth.toolbox.mesh.polygon import pypolygon
from pyearth.toolbox.mesh.polyline import pypolyline
from pyearth.toolbox.mesh.circle import pycircle

# Import timer utility from pyearth
from pyearth.toolbox.date.timer import pytimer as timer

# Import buffer-specific classes
from pyearthbuffer.buffer.raster import gcstiff as RasterBuffer

# Import pyearthbuffer utilities
from pyearthbuffer.utility.case import pycase as BufferCase


# Define public API
__all__ = [
    # Core geometry (from pyearth)
    'pypoint',
    'pyline',
    'pypolygon',
    'pypolyline',
    'pycircle',
    # Utilities (from pyearth)
    'timer',
    # Buffer classes (pyearthbuffer-specific)
    'RasterBuffer',
    'BufferCase',
]
