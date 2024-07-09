import os
import numpy as np
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file

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
        dummy = gdal_read_geotiff_file(self.sFilename_raster)
        aData = dummy['dataOut']

        ncolumn = dummy['ncolumn']
        nrow = dummy['nrow']
        dResolution_x = dummy['dResolution_x']
        dResolution_y = dummy['dResolution_y']

        iMin = np.min(aData)
        iMax = np.max(aData)

        if iMin !=0 :
            print('The binary mask is not binary!')
            return

        if iMax !=1 :
            print('The binary mask is not binary!')
            return

        #get pixel of interest


        return

