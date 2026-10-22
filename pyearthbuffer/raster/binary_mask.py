"""Raster buffer operations for Geographic Coordinate Systems (Experimental)."""

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


class RasterBuffer:
    """Geographic Coordinate System GeoTIFF buffer handler (Experimental).

    Args:
        raster_file (str): Path to input binary mask GeoTIFF file.
    """

    raster_file: str

    def __init__(self, raster_file: str):
        if not os.path.exists(raster_file):
            raise FileNotFoundError(f"The raster file does not exist: {raster_file}")
        self.raster_file = os.path.abspath(raster_file)

    def calculate_binary_mask_buffer_zone(
        self,
        buffer_radius: float,
        output_file: str,
    ) -> Optional[str]:
        """Calculate buffer zone for binary mask raster.

        Args:
            buffer_radius (float): Buffer radius in meters.
            output_file (str): Path to output raster file.

        Returns:
            Optional[str]: Path to output raster file, or None on failure.
        """
        out_folder = os.path.dirname(output_file)
        if out_folder:
            os.makedirs(out_folder, exist_ok=True)

        raster_file = self.raster_file
        dummy = gdal_read_geotiff_file(raster_file)
        a_data = dummy["dataOut"]

        n_col = dummy["ncolumn"]
        n_row = dummy["nrow"]
        res_x = dummy["pixelWidth"]
        res_y = -dummy["pixelHeight"]
        projection = dummy["projection"]
        geotransform = dummy["geotransform"]

        min_val = np.min(a_data)
        max_val = np.max(a_data)

        if min_val != 0 or max_val != 1:
            raise ValueError(
                f"The raster data is not a binary mask (min={min_val}, max={max_val}). Expected values are 0 and 1."
            )

        label_file = raster_file.replace(".tif", "_label.tif")
        shp_file = raster_file.replace(".tif", ".shp")
        geojson_file = raster_file.replace(".tif", ".geojson")

        s = generate_binary_structure(2, 2)
        labeled_array, _ = label(a_data, structure=s)

        p_driver_tif = gdal.GetDriverByName("GTiff")
        options = ["COMPRESS=DEFLATE", "PREDICTOR=2"]
        p_ds = p_driver_tif.Create(
            label_file, n_col, n_row, 1, gdal.GDT_Int16, options
        )
        p_ds.SetGeoTransform(geotransform)
        p_ds.SetProjection(projection)
        p_band = p_ds.GetRasterBand(1)
        p_band.WriteArray(labeled_array)
        p_band.SetNoDataValue(0)
        p_band.FlushCache()
        p_ds = None

        vectorize_raster(label_file, shp_file)
        convert_vector_format(shp_file, geojson_file)

        p_driver_json = ogr.GetDriverByName("GeoJSON")
        p_vector_ds = p_driver_json.Open(geojson_file, 0)
        if p_vector_ds is None:
            raise RuntimeError(f"Failed to open vector file: {geojson_file}")

        p_layer = p_vector_ds.GetLayer()
        n_features = p_layer.GetFeatureCount()
        buffered_raster_files = []

        for i in range(n_features):
            part_str = f"{i + 1:08d}"
            feat = p_layer.GetFeature(i)
            geom = feat.GetGeometryRef()

            if geom.GetGeometryName().upper() != "POLYGON":
                continue

            ring = geom.GetGeometryRef(0)
            n_vertex = ring.GetPointCount()
            if n_vertex < 3:
                continue

            vertices = []
            coords = []
            for j in range(n_vertex):
                pt = ring.GetPoint(j)
                coords.append([pt[0], pt[1]])
                pt_dict = {
                    "dLongitude_degree": pt[0],
                    "dLatitude_degree": pt[1],
                }
                vertices.append(pypoint(pt_dict))

            coords_arr = np.array(coords)
            edges = []
            for k in range(0, len(vertices) - 1):
                if vertices[k] != vertices[k + 1]:
                    edges.append(pyline(vertices[k], vertices[k + 1]))

            if not edges:
                continue

            edges.append(pyline(vertices[-1], vertices[0]))

            lon_center = float(np.mean(coords_arr[:, 0]))
            lat_center = float(np.mean(coords_arr[:, 1]))
            p_polygon = pypolygon(lon_center, lat_center, edges, vertices + [vertices[0]])

            dummy_geojson = (
                os.path.join(out_folder, f"temp{part_str}.geojson")
                if out_folder
                else f"temp{part_str}.geojson"
            )
            p_polygon.calculate_buffer_zone_polygon(
                buffer_radius, sFilename_out=dummy_geojson
            )

            dummy_tif = dummy_geojson.replace(".geojson", ".tif")
            rasterize_vector(
                dummy_geojson,
                dummy_tif,
                res_x,
                res_y,
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
            buffered_raster_files.append(dummy_tif)

        p_vector_ds = None

        merge_raster_files(
            buffered_raster_files,
            output_file,
            res_x,
            res_y,
            raster_file,
        )

        return output_file
