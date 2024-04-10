import os
import numpy as np
from osgeo import ogr, gdal, osr
from geographiclib.geodesic import Geodesic

from pyearth.gis.geometry.calculate_polygon_area  import calculate_polygon_area
from geobuf.classes.vertex import pyvertex
from geobuf.classes.edge import pyedge


point0= dict()
point_lon = -73.935242
point_lat = 40.730610
point0['dLongitude_degree'] = point_lon
point0['dLatitude_degree'] =  point_lat
pVertex1 = pyvertex(point0)  


point_lon = -73.995242
point_lat = 40.790610
point0['dLongitude_degree'] = point_lon
point0['dLatitude_degree'] =  point_lat
pVertex2 = pyvertex(point0) 

pEdge = pyedge(pVertex1, pVertex2)
sFolder_out = '/qfs/people/liao313/workspace/python/geobuf/data/edge'
sFilename_out = '/qfs/people/liao313/workspace/python/geobuf/data/edge/edge_buffer.geojson'
aVertex = pEdge.calculate_buffer_zone_polygon(1000, nPoint = 12, sFilename_out=sFilename_out, sFolder_out=sFolder_out)


