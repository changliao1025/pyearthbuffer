import os
from pyearthbuffer import pypoint, pyline, pypolygon

sFolder_data = os.path.join(os.path.dirname(__file__), '..','..','data')
#convert to absolute path
sFolder_data = os.path.abspath(sFolder_data)
print(sFolder_data)

sFolder_out = os.path.join(sFolder_data, 'pypolygon')
os.makedirs(sFolder_out, exist_ok=True)

point0= dict()
# Example pypoint (latitude, longitude)

point_lon = -73.
point_lat = 40.
point0['dLongitude_degree'] = point_lon
point0['dLatitude_degree'] =  point_lat
pPoint0 = pypoint(point0)

point_lon = -73
point_lat = 42
point1= dict()
point1['dLongitude_degree'] = point_lon
point1['dLatitude_degree'] =  point_lat
pPoint1 = pypoint(point1)

point_lon = -71
point_lat = 42
point2= dict()
point2['dLongitude_degree'] = point_lon
point2['dLatitude_degree'] =  point_lat
pPoint2 = pypoint(point2)


point_lon = -72
point_lat = 41
point2= dict()
point2['dLongitude_degree'] = point_lon
point2['dLatitude_degree'] =  point_lat
pPoint3 = pypoint(point2)

point_lon = -72.5
point_lat = 40
point2= dict()
point2['dLongitude_degree'] = point_lon
point2['dLatitude_degree'] =  point_lat
pPoint4 = pypoint(point2)

aPoint = list()
aPoint.append(pPoint0)
aPoint.append(pPoint1)
aPoint.append(pPoint2)
aPoint.append(pPoint3)
aPoint.append(pPoint4)
nPoint = len(aPoint)

nPoint = len(aPoint)

aLine = list()
for i in range(0, nPoint-1):
    pLine = pyline(aPoint[i], aPoint[i+1])
    aLine.append(pLine)

pLine = pyline(aPoint[nPoint-1], aPoint[0])
aLine.append(pLine)

dLon_center = sum([p.dLongitude_degree for p in aPoint]) / nPoint
dLat_center = sum([p.dLatitude_degree for p in aPoint]) / nPoint

aPoint.append(aPoint[0])

pPolygon = pypolygon(dLon_center, dLat_center, aLine, aPoint)

sFilename_out = os.path.join(sFolder_out,  'polygon_buffer.geojson')

pPolygon.calculate_buffer_zone_polygon(50000, sFilename_out = sFilename_out, sFolder_out=sFolder_out)
