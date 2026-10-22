import os

from pyearthbuffer import pyline, pypoint, pypolyline

sFolder_data = os.path.join(os.path.dirname(__file__), "..", "..", "data")
# convert to absolute path
sFolder_data = os.path.abspath(sFolder_data)
print(sFolder_data)

sFolder_out = os.path.join(sFolder_data, "pypoint")
os.makedirs(sFolder_out, exist_ok=True)


point0 = dict()
point_lon = -73
point_lat = 40.0
point0["dLongitude_degree"] = point_lon
point0["dLatitude_degree"] = point_lat
pPoint0 = pypoint(point0)


point_lon = -73
point_lat = 41
point1 = dict()
point1["dLongitude_degree"] = point_lon
point1["dLatitude_degree"] = point_lat
pPoint1 = pypoint(point1)

point_lon = -72
point_lat = 41
point2 = dict()
point2["dLongitude_degree"] = point_lon
point2["dLatitude_degree"] = point_lat
pPoint2 = pypoint(point2)

pLine0 = pyline(pPoint0, pPoint1)
pLine1 = pyline(pPoint1, pPoint2)

aEdge = list()
aEdge.append(pLine0)
aEdge.append(pLine1)
pPolyline = pypolyline(aEdge)


sFilename_out = os.path.join(sFolder_out, "polyline_buffer.geojson")

sWkt_buffer_polygon, aPoint_out, aCircle_out = pPolyline.calculate_buffer_zone_polygon(
    1000, sFilename_out=sFilename_out, sFolder_out=sFolder_out
)
