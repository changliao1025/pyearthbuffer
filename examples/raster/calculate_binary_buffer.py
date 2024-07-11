#provide a binary mask with 0 and 1, then a buffer distance, and calculate the buffer zone in binary mask as well
import os, sys
from shutil import copy2
from scipy.ndimage import binary_erosion, binary_dilation
import numpy as np
from osgeo import gdal

sPath_ncc = '/global/homes/l/liao313/workspace/python/gcsbuffer/'
sys.path.append(sPath_ncc)

from pyearth.gis.gdal.read.raster.gdal_read_geotiff_file import gdal_read_geotiff_file
from gcsbuffer.classes.gcstiff import gcstiff


# Buffer radius in meters
buffer_radius = 10000  # 10 km
mile_2_meter = 1609.34
buffer_radius = 10 * mile_2_meter #mile to meter



sFilename_binary_mask = '/global/cfs/projectdirs/m4611/data/output/waterbody/geotiff_merge/waterbody_merge_binary.tif'


#use erosion and dilation to adjust the mask


sWorkspace_out = '/global/homes/l/liao313/workspace/python/gcsbuffer/data/raster'
sFilename_out = os.path.join(sWorkspace_out, 'waterbody_merge_binary_adjust.tif')

#make a copy first


#Filename_binary_mask_copy = os.path.join(sWorkspace_out, 'waterbody_merge_binary.tif')
#
#opy2(sFilename_binary_mask, sFilename_binary_mask_copy)
#
#read the geotiff file
#ummy = gdal_read_geotiff_file (sFilename_binary_mask_copy)
#Data = dummy['dataOut']
#column = dummy['ncolumn']
#row = dummy['nrow']
#Resolution_x = dummy['pixelWidth']
#Resolution_y = dummy['pixelHeight']
#Projection = dummy['projection']
#Transform = dummy['geotransform']
#repeart 10 times to fix the mask
#or i in range(1):
#   aData = binary_erosion(aData, iterations=50).astype(aData.dtype)
#   aData = binary_dilation(aData, iterations=50).astype(aData.dtype)
#
#Driver_tif = gdal.GetDriverByName('GTiff')
#create a new geotiff file
#
#
#ptions = ['COMPRESS=DEFLATE', 'PREDICTOR=2']
#Dataset = pDriver_tif.Create(sFilename_out, ncolumn, nrow, 1, gdal.GDT_Byte, options)
#Dataset.SetGeoTransform(pTransform)
#Dataset.SetProjection(pProjection)
#Band = pDataset.GetRasterBand(1)
#Band.SetNoDataValue(0)
#Band.WriteArray(aData)
#Band.FlushCache()
#Dataset = None



print('The binary mask is adjusted!')

pBinary_mask = gcstiff(sFilename_out)
sFilename_out = os.path.join(sWorkspace_out, 'waterbody_merge_binary_buffer.tif')

pBinary_mask.calculate_binary_mash_buffer_zone(buffer_radius, sFilename_out)




