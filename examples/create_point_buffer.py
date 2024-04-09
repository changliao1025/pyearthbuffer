import os
import numpy as np
from osgeo import ogr, gdal, osr
from geographiclib.geodesic import Geodesic

from pyearth.gis.geometry.calculate_polygon_area  import calculate_polygon_area
from geobuf.classes.vertex import pyvertex


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

pVertex_in = pyvertex(point0)  
# Buffer radius in meters
buffer_radius = 10000  # 10 km
mile_2_meter = 1609.34
buffer_radius = 10 * mile_2_meter #mile to meter

# Number of points to calculate
num_points = 60

# Calculate the buffer points
buffer_points = []

for bearing in range(0, 360, 360//num_points):
    pVertex_buffer = pVertex_in.calculate_buffer_zone_vertex(buffer_radius, bearing)
    print(f"Point {bearing+1}:")
    
    print("Longitude:", pVertex_buffer.dLongitude_degree)
    print("Latitude:", pVertex_buffer.dLatitude_degree)
    buffer_points.append((pVertex_buffer.dLongitude_degree, pVertex_buffer.dLatitude_degree ))

# Print the buffer points

aLon =list()
aLat = list()
ring = ogr.Geometry(ogr.wkbLinearRing)
for i, (lon, lat) in enumerate(buffer_points):
    print(f"Point {i+1}:")
    print("Longitude:", lon)
    print("Latitude:", lat)    
    ring.AddPoint(lon, lat)
    aLon.append(lon)
    aLat.append(lat)

x1 = buffer_points[0][0]
y1 = buffer_points[0][1]
ring.AddPoint( x1, y1) #double check 
print(ring.ExportToWkt())
 

#save it as parquet file using gdal 

pDriver = ogr.GetDriverByName('GEOJSON')

sFilename_out = 'point_buffer_nyc.geojson'
if os.path.exists(sFilename_out):
    os.remove(sFilename_out)

#create the output file with the polygon feature
pDS = pDriver.CreateDataSource(sFilename_out)
pLayer = pDS.CreateLayer('buffer_circle', geom_type=ogr.wkbPolygon)

pLayer.CreateField(ogr.FieldDefn('longitude', ogr.OFTReal)) #long type for high resolution
pLayer.CreateField(ogr.FieldDefn('latitude', ogr.OFTReal)) #long type for high resolution
pArea_field = ogr.FieldDefn('area', ogr.OFTReal)
pArea_field.SetWidth(20)
pArea_field.SetPrecision(2)
pLayer.CreateField(pArea_field)

pLayerDefn = pLayer.GetLayerDefn()
pFeature = ogr.Feature(pLayerDefn) 

#add the first point to close the ring

dArea = calculate_polygon_area(aLon, aLat)

           
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

