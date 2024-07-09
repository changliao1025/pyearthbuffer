import os
import numpy as np
from osgeo import ogr, gdal, osr
from geographiclib.geodesic import Geodesic

from pyearth.gis.geometry.calculate_polygon_area  import calculate_polygon_area
from gcsbuffer.classes.vertex import pyvertex
from gcsbuffer.classes.edge import pyedge
from gcsbuffer.classes.flowline import pyflowline


point0= dict()
point_lon = -73
point_lat = 40.
point0['dLongitude_degree'] = point_lon
point0['dLatitude_degree'] =  point_lat
pVertex0 = pyvertex(point0)


point_lon = -73
point_lat = 41
point1= dict()
point1['dLongitude_degree'] = point_lon
point1['dLatitude_degree'] =  point_lat
pVertex1 = pyvertex(point1)

point_lon = -72
point_lat = 41
point2= dict()
point2['dLongitude_degree'] = point_lon
point2['dLatitude_degree'] =  point_lat
pVertex2 = pyvertex(point2)

pEdge0 = pyedge(pVertex0, pVertex1)
pEdge1 = pyedge(pVertex1, pVertex2)

aEdge = list()
aEdge.append(pEdge0)
aEdge.append(pEdge1)
pFlowline = pyflowline(aEdge)

sFolder_out = '/qfs/people/liao313/workspace/python/gcsbuffer/data/flowline'
sFilename_out = '/qfs/people/liao313/workspace/python/gcsbuffer/data/flowline/flowline_buffer.geojson'

aVertex = pFlowline.calculate_buffer_zone_polygon(1000, sFilename_out=sFilename_out , sFolder_out=sFolder_out)


