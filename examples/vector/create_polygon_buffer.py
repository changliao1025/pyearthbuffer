import os
import numpy as np
from osgeo import ogr, gdal, osr
from geographiclib.geodesic import Geodesic

from pyearth.gis.geometry.calculate_polygon_area  import calculate_polygon_area
from gcsbuffer.classes.vertex import pyvertex
from gcsbuffer.classes.edge import pyedge
from gcsbuffer.classes.polygon import pypolygon
from gcsbuffer.algorithms.find_minimal_enclosing_polygon import find_minimal_enclosing_polygon

point0= dict()
# Example point (latitude, longitude)

point_lon = -73.
point_lat = 40.
point0['dLongitude_degree'] = point_lon
point0['dLatitude_degree'] =  point_lat
pVertex0 = pyvertex(point0)


point_lon = -73
point_lat = 42
point1= dict()
point1['dLongitude_degree'] = point_lon
point1['dLatitude_degree'] =  point_lat
pVertex1 = pyvertex(point1)

point_lon = -71
point_lat = 42
point2= dict()
point2['dLongitude_degree'] = point_lon
point2['dLatitude_degree'] =  point_lat
pVertex2 = pyvertex(point2)


point_lon = -72
point_lat = 41
point2= dict()
point2['dLongitude_degree'] = point_lon
point2['dLatitude_degree'] =  point_lat
pVertex3 = pyvertex(point2)


point_lon = -72.5
point_lat = 40
point2= dict()
point2['dLongitude_degree'] = point_lon
point2['dLatitude_degree'] =  point_lat
pVertex4 = pyvertex(point2)



aVertex = list()
aVertex.append(pVertex0)
aVertex.append(pVertex1)
aVertex.append(pVertex2)
aVertex.append(pVertex3)
aVertex.append(pVertex4)
nPoint = len(aVertex)

nVertex = len(aVertex)

aEdge = list()
for i in range(0, nVertex-1):
    pEdge = pyedge(aVertex[i], aVertex[i+1])
    aEdge.append(pEdge)

pEdge = pyedge(aVertex[nVertex-1], aVertex[0])
aEdge.append(pEdge)

pPolygon = pypolygon(aEdge)

sFolder_out  = '/qfs/people/liao313/workspace/python/geobuf/data/polygon'
sFilename_out = os.path.join(sFolder_out,  'polygon_buffer.geojson')

pPolygon.calculate_buffer_zone_polygon(50000, sFilename_out = sFilename_out, sFolder_out=sFolder_out)



