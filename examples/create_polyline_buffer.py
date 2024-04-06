import os
import numpy as np
from osgeo import ogr, gdal, osr
from geographiclib.geodesic import Geodesic
from scipy.spatial import ConvexHull

from pyearth.gis.geometry.calculate_polygon_area  import calculate_polygon_area

def find_minimal_enclosing_polygon(lat_lon_points):
    # Convert lat/lon points to Cartesian coordinates
    # Assuming lat_lon_points is a list of tuples (latitude, longitude)
    points_cartesian = [(np.cos(np.deg2rad(lat)) * np.cos(np.deg2rad(lon)),
                         np.cos(np.deg2rad(lat)) * np.sin(np.deg2rad(lon)),
                         np.sin(np.deg2rad(lat)))
                        for lat, lon in lat_lon_points]

    # Create a ConvexHull object from the Cartesian coordinates
    hull = ConvexHull(points_cartesian)

    # Get the indices of the points on the convex hull
    indices = hull.vertices

    # Get the points on the convex hull in Cartesian coordinates
    points_on_hull_cartesian = [points_cartesian[i] for i in indices]

    # Convert the points on the convex hull back to lat/lon coordinates
    points_on_hull_latlon = [(np.rad2deg(np.arcsin(p[2])),
                              np.rad2deg(np.arctan2(p[1], p[0])))
                             for p in points_on_hull_cartesian]

    return points_on_hull_latlon

def calculate_buffer_zone(lat, lon, bearing, radius):
    # Create a geodesic object
    geod = Geodesic.WGS84

    # Calculate the geodesic buffer
    buffer = geod.Direct(lat, lon, bearing, radius)

    # Extract the latitude and longitude of the buffer point
    buffer_lat = buffer['lat2']
    buffer_lon = buffer['lon2']

    return buffer_lat, buffer_lon

# Example point (latitude, longitude)
point_lat = 40.730610
point_lon = -73.935242

# Buffer radius in meters
buffer_radius = 10000  # 10 km

# Number of points to calculate
num_points = 360

# Calculate the buffer points
buffer_points = [calculate_buffer_zone(point_lat, point_lon, bearing, buffer_radius) for bearing in range(0, 360, 360//num_points)]

# Print the buffer points

ring = ogr.Geometry(ogr.wkbLinearRing)
aCoords = np.full((num_points,2), -9999.0, dtype=float)
aLon =list()
aLat = list()

for i, (lat, lon) in enumerate(buffer_points):
    print(f"Point {i+1}:")
    print("Latitude:", lat)
    print("Longitude:", lon)
    ring.AddPoint(lon, lat)
    aLon.append(lon)
    aLat.append(lat)
 

#save it as parquet file using gdal 

pDriver = ogr.GetDriverByName('Parquet')

sFilename_parquet = 'buffer_points.parquet'
if os.path.exists(sFilename_parquet):
    os.remove(sFilename_parquet)

#create the output file with the polygon feature
pDS = pDriver.CreateDataSource(sFilename_parquet)
pLayer = pDS.CreateLayer('buffer_points', geom_type=ogr.wkbPoint)

pLayer.CreateField(ogr.FieldDefn('longitude', ogr.OFTReal)) #long type for high resolution
pLayer.CreateField(ogr.FieldDefn('latitude', ogr.OFTReal)) #long type for high resolution
pArea_field = ogr.FieldDefn('area', ogr.OFTReal)
pArea_field.SetWidth(20)
pArea_field.SetPrecision(2)
pLayer.CreateField(pArea_field)

pLayerDefn = pLayer.GetLayerDefn()
pFeature = ogr.Feature(pLayerDefn) 

#add the first point to close the ring
x1 = buffer_points[0][0]
y1 = buffer_points[0][1]

dArea = calculate_polygon_area(aLon, aLat)

ring.AddPoint(x1, y1) #double check            
pPolygon = ogr.Geometry(ogr.wkbPolygon)
pPolygon.AddGeometry(ring)
pFeature.SetGeometry(pPolygon)
pFeature.SetField("longitude", point_lon )
pFeature.SetField("latitude", point_lat )
pFeature.SetField("area", dArea )
pLayer.CreateFeature(pFeature)


#flush the cache and close the file
pDS.FlushCache()
pDS.Destroy()

