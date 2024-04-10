
import os
from osgeo import ogr

from pyearth.gis.geometry.calculate_polygon_area  import calculate_polygon_area
def save_vertex_as_polygon(aVertex_in, sFilename_out):
    pDriver = ogr.GetDriverByName('GEOJSON')
    if os.path.exists(sFilename_out):
        os.remove(sFilename_out)

    pDataset = pDriver.CreateDataSource(sFilename_out)
    pLayer = pDataset.CreateLayer('buffer_ploygon', geom_type=ogr.wkbPolygon)
    aLon = list()
    aLat = list()
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for pVertex in aVertex_in:
        ring.AddPoint(pVertex.dLongitude_degree, pVertex.dLatitude_degree)
        aLon.append(pVertex.dLongitude_degree)
        aLat.append(pVertex.dLatitude_degree)
    
    ring.AddPoint(aVertex_in[0].dLongitude_degree, aVertex_in[0].dLatitude_degree)
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
    pFeature.SetField("area", dArea )
    pLayer.CreateFeature(pFeature)
    #flush the cache and close the file
    pDataset.FlushCache()
    pDataset.Destroy()
    return