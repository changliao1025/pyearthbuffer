import os
import numpy as np
from osgeo import ogr, gdal, osr
from geographiclib.geodesic import Geodesic

from pyearth.gis.geometry.calculate_polygon_area  import calculate_polygon_area
from geobuf.classes.vertex import pyvertex
from geobuf.classes.edge import pyedge
from geobuf.classes.flowline import pyflowline


point0= dict()
# Example point (latitude, longitude)

point_lon = -73.935242
point_lat = 40.730610
point0['dLongitude_degree'] = point_lon
point0['dLatitude_degree'] =  point_lat
pVertex0 = pyvertex(point0)  


point_lon = -75.935242
point_lat = 44.730610
point1= dict()
point1['dLongitude_degree'] = point_lon
point1['dLatitude_degree'] =  point_lat
pVertex1 = pyvertex(point1) 

point_lon = -71.935242
point_lat = 47.730610
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

sFolder_out = '/qfs/people/liao313/workspace/python/geobuf/data/flowline'

aVertex = pFlowline.calculate_buffer_zone_polygon(1000, sFolder_out=sFolder_out)

#save as a polygon

aLon =list()
aLat = list()
ring = ogr.Geometry(ogr.wkbLinearRing)
for pVertex in aVertex:
    lon = pVertex.dLongitude_degree
    lat = pVertex.dLatitude_degree
    ring.AddPoint(lon, lat)
    aLon.append(lon)
    aLat.append(lat)

ring.AddPoint( aVertex[0].dLongitude_degree, aVertex[0].dLatitude_degree) #double check 
print(ring.ExportToWkt())
 
 

#save it as parquet file using gdal 

pDriver = ogr.GetDriverByName('GEOJSON')

sFoler  = '/qfs/people/liao313/workspace/python/geobuf/data/flowline'
sFilename_out = os.path.join(sFoler,  'flowline_buffer.geojson')
if os.path.exists(sFilename_out):
    os.remove(sFilename_out)

#create the output file with the polygon feature
pDS = pDriver.CreateDataSource(sFilename_out)
pLayer = pDS.CreateLayer('flowline_buffer', geom_type=ogr.wkbPolygon)

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
