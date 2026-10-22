"""File-based batch geodesic buffer operations for vector datasets."""

import logging
import os
from pathlib import Path
from typing import Optional, Union

from osgeo import ogr
from pyearth.gis.gdal.gdal_vector_format_support import get_vector_format_from_filename
from pyearth.gis.geometry.calculate_polygon_area import calculate_polygon_area
from pyearth.gis.location.get_geometry_coordinates import get_geometry_coordinates

from pyearthbuffer.core.formats import ensure_wgs84_spatial_ref
from pyearthbuffer.core.validation import validate_distance
from pyearthbuffer.vector.dissolve import (
    dissolve_geometries,
    split_multipolygon_to_polygons,
)
from pyearthbuffer.vector.geometry import buffer

logger = logging.getLogger(__name__)


def buffer_file(
    input_file: Union[str, Path],
    output_file: Union[str, Path],
    distance: float,
    *,
    dissolve: bool = False,
    min_area: Optional[float] = None,
    preserve_attributes: bool = True,
    output_driver: Optional[str] = None,
    overwrite: bool = True,
    verbose: bool = False,
) -> int:
    """Create geodesic buffer zones for all features in a vector dataset.

    Reads features from the input vector file, applies geodesic buffer
    calculations on the WGS84 ellipsoid for each feature, and writes the
    resulting buffer polygons to the output vector file.

    Supports Shapefile (.shp), GeoJSON (.geojson), GeoPackage (.gpkg),
    and other OGR-supported vector formats.

    Args:
        input_file: Path to source vector file.
        output_file: Path to destination vector file.
        distance: Buffer distance in meters.
        dissolve: If True, union/merge overlapping buffer geometries into
            distinct non-overlapping polygons.
        min_area: Optional minimum area threshold in square meters (for polygons).
            Polygons smaller than this threshold are skipped.
        preserve_attributes: If True and dissolve is False, copies attribute fields
            from input features to output features.
        output_driver: OGR driver name. If None, auto-detected from output file extension.
        overwrite: If True, removes existing destination file before writing.
        verbose: If True, logs progress updates.

    Returns:
        int: Total number of buffer features written to output.

    Raises:
        FileNotFoundError: If input_file does not exist.
        RuntimeError: If vector file I/O or driver creation fails.
        ValueError: If distance <= 0 or min_area < 0.
    """
    s_input = str(Path(input_file).resolve())
    s_output = str(Path(output_file).resolve())

    if not os.path.exists(s_input):
        raise FileNotFoundError(f"Input vector file not found: {s_input}")

    valid_dist = validate_distance(distance)

    if min_area is not None and min_area < 0:
        raise ValueError(f"min_area must be non-negative, got {min_area}.")

    # Resolve output directory
    output_dir = os.path.dirname(s_output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Determine driver
    if output_driver is None:
        try:
            output_driver_name = get_vector_format_from_filename(s_output)
        except Exception:
            output_driver_name = "GeoJSON"
    else:
        output_driver_name = output_driver

    p_driver = ogr.GetDriverByName(output_driver_name)
    if p_driver is None:
        raise RuntimeError(f"OGR Driver '{output_driver_name}' is not available.")

    # Open input
    p_in_ds = ogr.Open(s_input, 0)
    if p_in_ds is None:
        raise RuntimeError(f"Could not open input vector dataset: {s_input}")

    p_in_layer = p_in_ds.GetLayer()
    if p_in_layer is None:
        p_in_ds = None
        raise RuntimeError(f"No valid vector layer found in: {s_input}")

    n_features = p_in_layer.GetFeatureCount()
    if verbose:
        logger.info(f"Processing {n_features} features from {s_input} with distance {valid_dist}m.")

    # Overwrite check
    if os.path.exists(s_output):
        if overwrite:
            if verbose:
                logger.info(f"Overwriting existing file: {s_output}")
            try:
                os.remove(s_output)
            except Exception as exc:
                logger.warning(f"Failed to remove existing file {s_output}: {exc}")
        else:
            p_in_ds = None
            raise FileExistsError(f"Output file already exists and overwrite=False: {s_output}")

    # Create output dataset & layer
    p_out_ds = p_driver.CreateDataSource(s_output)
    if p_out_ds is None:
        p_in_ds = None
        raise RuntimeError(f"Failed to create output datasource: {s_output}")

    srs = ensure_wgs84_spatial_ref()
    layer_name = (
        os.path.splitext(os.path.basename(s_output))[0]
        if output_driver_name == "ESRI Shapefile"
        else "buffer"
    )
    p_out_layer = p_out_ds.CreateLayer(layer_name, srs=srs, geom_type=ogr.wkbPolygon)
    if p_out_layer is None:
        p_in_ds = None
        p_out_ds = None
        raise RuntimeError("Failed to create output vector layer.")

    in_layer_defn = p_in_layer.GetLayerDefn()

    # Define fields
    if not dissolve and preserve_attributes:
        for i in range(in_layer_defn.GetFieldCount()):
            field_defn = in_layer_defn.GetFieldDefn(i)
            p_out_layer.CreateField(field_defn)
    else:
        # For dissolved output, provide id and buffer_dist fields
        p_out_layer.CreateField(ogr.FieldDefn("id", ogr.OFTInteger))
        p_out_layer.CreateField(ogr.FieldDefn("buffer_dist", ogr.OFTReal))

    buffered_geometries = []
    n_buffered = 0
    p_feat = p_in_layer.GetNextFeature()
    feat_idx = 0

    while p_feat:
        feat_idx += 1
        geom = p_feat.GetGeometryRef()
        if geom is None or geom.IsEmpty():
            p_feat = p_in_layer.GetNextFeature()
            continue

        geom_name = geom.GetGeometryName().upper()

        # Check min_area filter for polygons
        if min_area is not None and "POLYGON" in geom_name:
            try:
                coords = get_geometry_coordinates(geom)
                if coords is not None and len(coords) > 0:
                    c_arr = coords[0] if isinstance(coords, list) and isinstance(coords[0], list) else coords
                    c_arr = coords if not isinstance(coords, list) else coords[0]
                    area = calculate_polygon_area(c_arr[:, 0], c_arr[:, 1], iFlag_algorithm=2)
                    if area < min_area:
                        p_feat = p_in_layer.GetNextFeature()
                        continue
            except Exception as exc:
                logger.debug(f"Failed to calculate area for feature {feat_idx}: {exc}")

        try:
            buf_geom = buffer(geom, valid_dist, output_format="ogr")
        except Exception as exc:
            logger.warning(f"Failed to buffer feature {feat_idx} ({geom_name}): {exc}")
            p_feat = p_in_layer.GetNextFeature()
            continue

        if dissolve:
            buffered_geometries.append(buf_geom)
        else:
            out_feat = ogr.Feature(p_out_layer.GetLayerDefn())
            out_feat.SetGeometry(buf_geom)
            if preserve_attributes:
                for i in range(in_layer_defn.GetFieldCount()):
                    out_feat.SetField(i, p_feat.GetField(i))
            p_out_layer.CreateFeature(out_feat)
            out_feat = None
            n_buffered += 1

        p_feat = p_in_layer.GetNextFeature()

    if dissolve:
        unified = dissolve_geometries(buffered_geometries)
        if unified is not None and not unified.IsEmpty():
            parts = split_multipolygon_to_polygons(unified)
            for idx, part in enumerate(parts, start=1):
                out_feat = ogr.Feature(p_out_layer.GetLayerDefn())
                out_feat.SetGeometry(part)
                out_feat.SetField("id", idx)
                out_feat.SetField("buffer_dist", valid_dist)
                p_out_layer.CreateFeature(out_feat)
                out_feat = None
                n_buffered += 1

    # Cleanup OGR handles
    p_in_ds = None
    p_out_ds = None

    if verbose:
        logger.info(f"Finished buffering. Created {n_buffered} buffer features in {s_output}.")

    return n_buffered


def buffer_point_file(
    input_file: Union[str, Path],
    output_file: Union[str, Path],
    distance: float,
    **kwargs,
) -> int:
    """Create geodesic buffer zones around points in a vector file."""
    return buffer_file(input_file, output_file, distance, **kwargs)


def buffer_line_file(
    input_file: Union[str, Path],
    output_file: Union[str, Path],
    distance: float,
    **kwargs,
) -> int:
    """Create geodesic buffer corridors around lines in a vector file."""
    return buffer_file(input_file, output_file, distance, **kwargs)


def buffer_polygon_file(
    input_file: Union[str, Path],
    output_file: Union[str, Path],
    distance: float,
    **kwargs,
) -> int:
    """Create geodesic buffer zones around polygons in a vector file."""
    return buffer_file(input_file, output_file, distance, **kwargs)
