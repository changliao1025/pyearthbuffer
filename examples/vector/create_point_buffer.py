import os
from gcsbuffer import point
sFolder_data = os.path.join(os.path.dirname(__file__), '..','..','data')
#convert to absolute path
sFolder_data = os.path.abspath(sFolder_data)
print(sFolder_data)

sFolder_out = os.path.join(sFolder_data, 'point')
os.makedirs(sFolder_out, exist_ok=True)

point0= dict()


# Example point (latitude, longitude)

point_lon = -73.935242
point_lat = 40.730610
point_lon = -75.935242
point_lat = 44.730610

point_lon = -73.3722 #nyc earthquake
point_lat = 40.779

point0['dLongitude_degree'] = point_lon
point0['dLatitude_degree'] =  point_lat

pPoint_in = point(point0)
# Buffer radius in meters
buffer_radius = 10000  # 10 km
mile_2_meter = 1609.34
buffer_radius = 10 * mile_2_meter #mile to meter

# Number of points to calculate
num_points = 60
sFilename_out = os.path.join(sFolder_out, 'point_buffer.geojson')
aPoint_buffer = pPoint_in.calculate_buffer_zone_circle(buffer_radius, sFilename_out = sFilename_out )

