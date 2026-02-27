import os
from gcsbuffer import point ,line
sFolder_data = os.path.join(os.path.dirname(__file__), '..','..','data')
#convert to absolute path
sFolder_data = os.path.abspath(sFolder_data)
print(sFolder_data)

sFolder_out = os.path.join(sFolder_data, 'line')
os.makedirs(sFolder_out, exist_ok=True)

point0= dict()
point_lon = -73.935242
point_lat = 40.730610
point0['dLongitude_degree'] = point_lon
point0['dLatitude_degree'] =  point_lat
pPoint0 = point(point0)


point_lon = -73.995242
point_lat = 40.790610
point1= dict()
point1['dLongitude_degree'] = point_lon
point1['dLatitude_degree'] =  point_lat
pPoint1 = point(point1)

pLine = line(pPoint0, pPoint1)

sFilename_out = os.path.join(sFolder_out, 'line_buffer.geojson')

aPoint_out, aPoint_center, aPoint_circle, aCircle = pLine.calculate_buffer_zone_polygon(1000, nPoint = 12,
                                               sFilename_out=sFilename_out,
                                              sFolder_out=sFolder_out)

