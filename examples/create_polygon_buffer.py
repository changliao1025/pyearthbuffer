import os
import numpy as np
from osgeo import ogr, gdal, osr
from geographiclib.geodesic import Geodesic

from pyearth.gis.geometry.calculate_polygon_area  import calculate_polygon_area
from geobuf.classes.vertex import pyvertex
from geobuf.classes.edge import pyedge
from geobuf.classes.flowline import pyflowline
from geobuf.algorithms.find_minimal_enclosing_polygon import find_minimal_enclosing_polygon

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


point_lon = -71.934242
point_lat = 47.730610
point2= dict()
point2['dLongitude_degree'] = point_lon
point2['dLatitude_degree'] =  point_lat
pVertex3 = pyvertex(point2) 


point_lon = -72.934242
point_lat = 47.830610
point2= dict()
point2['dLongitude_degree'] = point_lon
point2['dLatitude_degree'] =  point_lat
pVertex4 = pyvertex(point2) 


#using 4 point as an example
#a sinlge polygon can be separated into multiple line

aVertex = list()
aVertex.append(pVertex0)
aVertex.append(pVertex1)
aVertex.append(pVertex2)
aVertex.append(pVertex3)
aVertex.append(pVertex4)
nPoint = len(aVertex)


sFolder_out = '/qfs/people/liao313/workspace/python/geobuf/data/flowline'


if nPoint == 3:
    pass
else:
    nPart = nPoint // 2 
    #the first part is a flowline
    aEdge = list()
    for i in range(0, nPart+1):
        pEdge = pyedge(aVertex[i], aVertex[i+1])
        aEdge.append(pEdge)
    pFlowline = pyflowline(aEdge)
    aVertex0 = pFlowline.calculate_buffer_zone_polygon(5000, sFolder_out=sFolder_out)

    #the second part
    aEdge = list()
    for i in range(nPart, nPoint-1):
        pEdge = pyedge(aVertex[i], aVertex[i+1])
        aEdge.append(pEdge)    
    #add the return edge
    pEdge = pyedge(aVertex[nPoint-1], aVertex[0])
    aEdge.append(pEdge)
    pFlowline = pyflowline(aEdge)
    aVertex1 = pFlowline.calculate_buffer_zone_polygon(5000, sFolder_out=sFolder_out)

    #now merge using the first and last point
    aLongitude_degree = list()
    aLatitude_degree = list()
    for pVertex in aVertex0:
        aLongitude_degree.append(pVertex.dLongitude_degree)
        aLatitude_degree.append(pVertex.dLatitude_degree)
    for pVertex in aVertex1:
        aLongitude_degree.append(pVertex.dLongitude_degree)
        aLatitude_degree.append(pVertex.dLatitude_degree)

    pPolygon_out = find_minimal_enclosing_polygon(aLongitude_degree, aLatitude_degree)
    aVertex_out = list()
    for p in pPolygon_out:
        point0= dict()
        point0['dLongitude_degree'] = p[0]
        point0['dLatitude_degree'] = p[1]
        pVertex_out = pyvertex(point0)  
        aVertex_out.append(pVertex_out)

    
    aLon =list()
    aLat = list()
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for pVertex in aVertex_out:
        lon = pVertex.dLongitude_degree
        lat = pVertex.dLatitude_degree
        ring.AddPoint(lon, lat)
        aLon.append(lon)
        aLat.append(lat)


    ring.AddPoint( aVertex_out[0].dLongitude_degree, aVertex_out[0].dLatitude_degree) #double check 
    print(ring.ExportToWkt())
    

    #save it as parquet file using gdal 

    pDriver = ogr.GetDriverByName('GEOJSON')

    sFoler  = '/qfs/people/liao313/workspace/python/geobuf/data/polygon'
    sFilename_out = os.path.join(sFoler,  'polygon_buffer.geojson')
    if os.path.exists(sFilename_out):
        os.remove(sFilename_out)

    #create the output file with the polygon feature
    pDS = pDriver.CreateDataSource(sFilename_out)
    pLayer = pDS.CreateLayer('buffer_edge', geom_type=ogr.wkbPolygon)

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
    




