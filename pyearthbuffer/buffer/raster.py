"""Raster buffer operations for Geographic Coordinate Systems."""

import os
from typing import Optional

import numpy as np
from osgeo import gdal, ogr
from pyearth.gis.gdal.read.raster.gdal_read_geotiff_file import gdal_read_geotiff_file
from pyearth.toolbox.conversion.convert_vector_format import convert_vector_format
from pyearth.toolbox.conversion.rasterize_vector import rasterize_vector
from pyearth.toolbox.conversion.vectorize_raster import vectorize_raster
from pyearth.toolbox.management.raster.merge_raster_files import merge_raster_files
from pyearth.toolbox.mesh.line import pyline
from pyearth.toolbox.mesh.point import pypoint
from pyearth.toolbox.mesh.polygon import pypolygon
from scipy.ndimage import generate_binary_structure, label


class gcstiff:
    """Geographic Coordinate System GeoTIFF buffer handler.

    Args:
        sFilename_geotiff (str): Path to input GeoTIFF file.
    """

    sFilename_raster: str

    def __init__(self, sFilename_geotiff: str):
        if not os.path.exists(sFilename_geotiff):
            raise FileNotFoundError(f"The file does not exist: {sFilename_geotiff}")
        self.sFilename_raster = os.path.abspath(sFilename_geotiff)

    def calculate_binary_mask_buffer_zone(
        self,
        buffer_radius: float,
        sFilename_out: str,
    ) -> Optional[str]:
        """Calculate buffer zone for binary mask raster.

        Args:
            buffer_radius (float): Buffer radius in meters.
            sFilename_out (str): Path to output raster file.

        Returns:
            Optional[str]: Path to output raster file, or None on failure.
        """
        sFolder_out = os.path.dirname(sFilename_out)
        if sFolder_out:
            os.makedirs(sFolder_out, exist_ok=True)

        sFilename_raster = self.sFilename_raster
        dummy = gdal_read_geotiff_file(sFilename_raster)
        aData = dummy["dataOut"]

        ncolumn = dummy["ncolumn"]
        nrow = dummy["nrow"]
        dResolution_x = dummy["pixelWidth"]
        dResolution_y = -dummy["pixelHeight"]
        pProjection = dummy["projection"]
        pTransform = dummy["geotransform"]

        iMin = np.min(aData)
        iMax = np.max(aData)

        if iMin != 0 or iMax != 1:
            raise ValueError(
                f"The raster data is not a binary mask (min={iMin}, max={iMax}). Expected values are 0 and 1."
            )

        # Convert clustered pixels to vectorized polygons
        sFilename_shapefile = sFilename_raster.replace(".tif", ".shp")
        sFilename_geojson = sFilename_raster.replace(".tif", ".geojson")

        s = generate_binary_structure(2, 2)
        labeled_array, _ = label(aData, structure=s)
        sFilename_raster_label = sFilename_raster.replace(".tif", "_label.tif")
        pDriver_tif = gdal.GetDriverByName("GTiff")
        options = ["COMPRESS=DEFLATE", "PREDICTOR=2"]
        pDataset = pDriver_tif.Create(
            sFilename_raster_label, ncolumn, nrow, 1, gdal.GDT_Int16, options
        )
        pDataset.SetGeoTransform(pTransform)
        pDataset.SetProjection(pProjection)
        pBand = pDataset.GetRasterBand(1)
        pBand.WriteArray(labeled_array)
        pBand.SetNoDataValue(0)
        pBand.FlushCache()
        pDataset = None

        vectorize_raster(sFilename_raster_label, sFilename_shapefile)

        # Convert shapefile to geojson
        convert_vector_format(sFilename_shapefile, sFilename_geojson)

        pDriver_geojson = ogr.GetDriverByName("GeoJSON")
        pDataSource_vector = pDriver_geojson.Open(sFilename_geojson, 0)
        if pDataSource_vector is None:
            raise RuntimeError(f"Failed to open vector file: {sFilename_geojson}")

        pLayer_vector = pDataSource_vector.GetLayer()
        nFeature = pLayer_vector.GetFeatureCount()
        aFilename_raster_out = []

        for i in range(nFeature):
            sPart = f"{i + 1:08d}"
            pFeature = pLayer_vector.GetFeature(i)
            pGeometry = pFeature.GetGeometryRef()

            if pGeometry.GetGeometryName() != "POLYGON":
                continue

            pRing = pGeometry.GetGeometryRef(0)
            nVertex = pRing.GetPointCount()
            if nVertex < 3:
                continue

            aVertex = []
            for j in range(nVertex):
                pPoint = pRing.GetPoint(j)
                point0 = {
                    "dLongitude_degree": pPoint[0],
                    "dLatitude_degree": pPoint[1],
                }
                aVertex.append(pypoint(point0))

            aEdge = []
            for k in range(0, nVertex - 1):
                aEdge.append(pyline(aVertex[k], aVertex[k + 1]))

            pPolygon = pypolygon(aEdge)

            sFilename_out_dummy = (
                os.path.join(sFolder_out, f"temp{sPart}.geojson")
                if sFolder_out
                else f"temp{sPart}.geojson"
            )
            pPolygon.calculate_buffer_zone_polygon(
                buffer_radius, sFilename_out=sFilename_out_dummy
            )

            sFilename_raster_out = sFilename_out_dummy.replace(".geojson", ".tif")
            rasterize_vector(
                sFilename_out_dummy,
                sFilename_raster_out,
                dResolution_x,
                dResolution_y,
                iFlag_boundary_only_in=None,
                iFlag_use_field_value_in=None,
                sAttribute_name_in=None,
                dMissing_value_in=None,
                dField_value_in=None,
                dFill_value_in=None,
                iDataType_out=None,
                dMin_x_in=None,
                dMax_x_in=None,
                dMin_y_in=None,
                dMax_y_in=None,
                nRow_in=None,
                nColumn_in=None,
                pProjection_target_in=None,
            )

            aFilename_raster_out.append(sFilename_raster_out)

        pDataSource_vector = None

        # Merge all individual buffered raster files
        sFilename_mask = sFilename_raster
        merge_raster_files(
            aFilename_raster_out,
            sFilename_out,
            dResolution_x,
            dResolution_y,
            sFilename_mask,
        )

        return sFilename_out

    # Alias for compatibility with previous naming
    calculate_binary_mash_buffer_zone = calculate_binary_mask_buffer_zone
