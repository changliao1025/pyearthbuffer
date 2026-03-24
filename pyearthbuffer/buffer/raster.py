import os
import numpy as np
from osgeo import ogr, gdal, osr
from scipy.ndimage import label, generate_binary_structure

from pyearth.gis.gdal.read.raster.gdal_read_geotiff_file import gdal_read_geotiff_file
from pyearth.toolbox.conversion.vectorize_raster import vectorize_raster
from pyearth.toolbox.conversion.rasterize_vector import rasterize_vector
from pyearth.toolbox.management.raster.merge_raster_files import merge_raster_files

# Import from pyearth instead of local classes
from pyearth.toolbox.mesh.point import pypoint
from pyearth.toolbox.mesh.line import pyline
from pyearth.toolbox.mesh.polygon import pypolygon



class gcstiff(object):

    sFilename_raster = None
    def __init__(self, sFilename_geotiff):

        #a geotiff file is required to initialize the object
        #other format will be supported in the future

        self.sFilename_raster = sFilename_geotiff

        #check if the file exists
        if not os.path.exists(sFilename_geotiff):
            print('The file does not exist!')
            return


    def calculate_binary_mash_buffer_zone( self, buffer_radius, sFilename_out):
        #read the geotiff file

        #get the folder that contain the output file
        sFolder_out = os.path.dirname(sFilename_out)

        pDriver_memory = ogr.GetDriverByName('Memory')
        sFilename_raster = self.sFilename_raster
        dummy = gdal_read_geotiff_file(sFilename_raster)
        aData = dummy['dataOut']

        ncolumn = dummy['ncolumn']
        nrow = dummy['nrow']
        dResolution_x = dummy['pixelWidth']
        dResolution_y = -dummy['pixelHeight']
        pProjection = dummy['projection']
        pTransform = dummy['geotransform']

        iMin = np.min(aData)
        iMax = np.max(aData)

        if iMin !=0 :
            print('The binary mask is not binary!')
            return

        if iMax !=1 :
            print('The binary mask is not binary!')
            return

        #get pixel of interest

        #ideally, we want to treat the cluster of pixel as a single ojbect
        #then we need to convert a raster a vector
        sFilename_shapefile = sFilename_raster.replace('.tif', '.shp')
        sFilename_geojson = sFilename_raster.replace('.tif', '.geojson')

        s = generate_binary_structure(2,2)
        labeled_array, num_features = label(aData, structure=s)
        sFilename_raster_label = sFilename_raster.replace('.tif', '_label.tif')
        pDriver_tif = gdal.GetDriverByName('GTiff')
        options = ['COMPRESS=DEFLATE', 'PREDICTOR=2']
        pDataset = pDriver_tif.Create(sFilename_raster_label, ncolumn, nrow, 1, gdal.GDT_Int16, options)
        pDataset.SetGeoTransform(pTransform)
        pDataset.SetProjection(pProjection)
        pBand = pDataset.GetRasterBand(1)
        pBand.WriteArray(labeled_array)
        pBand.SetNoDataValue(0)
        pBand.FlushCache()
        pDataset = None

        vectorize_raster(sFilename_raster_label , sFilename_shapefile)


        #open and read the vector file
        pDriver_vector = ogr.GetDriverByName('ESRI Shapefile')
        pDriver_geojson = ogr.GetDriverByName('GeoJSON')
        #covnert shapefile to geojson
        convert_shapefile_to_geojson( sFilename_shapefile, sFilename_geojson )
        pDataSource_vector = pDriver_geojson.Open(sFilename_geojson, 0)
        if pDataSource_vector is None:
            print('The file does not exist!')
            return

        pLayer_vector = pDataSource_vector.GetLayer()
        nFeature = pLayer_vector.GetFeatureCount()
        aFilename_raster_out = list()
        for i in np.arange(nFeature):
            sPart = "{:08d}".format( i + 1 )
            pFeature = pLayer_vector.GetFeature(i)
            pGeometry = pFeature.GetGeometryRef()
            #check if it is a polygon
            if pGeometry.GetGeometryName() == 'POLYGON':
                #get all the vertices
                pRing = pGeometry.GetGeometryRef(0)
                nVertex = pRing.GetPointCount()
                if nVertex < 3:
                    print('The polygon is not valid!', i)
                    continue
                aVertex = list()
                for j in range(nVertex):
                    pPoint = pRing.GetPoint(j)
                    point0= dict()
                    point0['dLongitude_degree'] = pPoint[0]
                    point0['dLatitude_degree'] =  pPoint[1]
                    pVertex0 = pypoint(point0)  # Changed from pyvertex to pypoint
                    aVertex.append(pVertex0)

                aEdge = list()
                for k in range(0, nVertex-1):
                    pEdge = pyline(aVertex[k], aVertex[k+1])  # Changed from pyedge to pyline
                    aEdge.append(pEdge)

                pPolygon = pypolygon(aEdge)
                #create a temporary polygon file in the memory
                sFilename_out_dummy = os.path.join(sFolder_out,  'temp' + sPart  + '.geojson')
                pPolygon.calculate_buffer_zone_polygon(buffer_radius, sFilename_out = sFilename_out_dummy)
                #convert the polygon to raster
                sFilename_raster_out = sFilename_out_dummy.replace('.geojson', '.tif')
                rasterize_vector(sFilename_out_dummy, sFilename_raster_out,
                     dResolution_x, dResolution_y,
                     iFlag_boundary_only_in = None,
                     iFlag_use_field_value_in=None,
                     sAttribute_name_in=None,
                     dMissing_value_in=None,
                     dField_value_in=None,
                     dFill_value_in=None,
                     iDataType_out=None,
                     dMin_x_in =None, dMax_x_in=None, dMin_y_in=None, dMax_y_in=None,
                     nRow_in=None, nColumn_in=None,
                     pProjection_target_in = None )

                aFilename_raster_out.append(sFilename_raster_out)
                print(sPart)
            else:
                print('The geometry type is not supported!')
                continue





        #merge all the raster files
        sFilename_merge_out = sFilename_out

        sFilename_mask = sFilename_raster
        merge_raster_files(aFilename_raster_out, sFilename_merge_out, dResolution_x, dResolution_y,
                           sFilename_mask)


        return
