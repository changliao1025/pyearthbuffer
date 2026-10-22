"""Dissolve and polygon decomposition utilities for buffer zones."""

import logging
from typing import Optional

from osgeo import ogr
from pyearth.gis.geometry.calculate_polygon_area import calculate_polygon_area
from pyearth.gis.location.get_geometry_coordinates import get_geometry_coordinates

logger = logging.getLogger(__name__)


def extract_outer_ring_polygon(geometry: ogr.Geometry) -> Optional[ogr.Geometry]:
    """Return a polygon built from the exterior ring of the input geometry.

    Args:
        geometry: Input POLYGON or MULTIPOLYGON geometry.

    Returns:
        Optional[ogr.Geometry]: Exterior ring polygon, or None on failure.
    """
    if geometry is None or geometry.IsEmpty():
        return None

    geom_name = geometry.GetGeometryName().upper()

    polygon = None
    if geom_name == "POLYGON":
        polygon = geometry
    elif geom_name == "MULTIPOLYGON":
        max_area = -1.0
        for i in range(geometry.GetGeometryCount()):
            part = geometry.GetGeometryRef(i)
            if part is None:
                continue
            coords = get_geometry_coordinates(part)
            area = calculate_polygon_area(coords, iFlag_algorithm=2)
            if area > max_area:
                max_area = area
                polygon = part
    else:
        return None

    if polygon is None:
        return None

    outer_ring = polygon.GetGeometryRef(0)
    if outer_ring is None:
        return None

    outer_polygon = ogr.Geometry(ogr.wkbPolygon)
    outer_polygon.AddGeometry(outer_ring.Clone())
    return outer_polygon


def dissolve_geometries(geometries: list[ogr.Geometry]) -> Optional[ogr.Geometry]:
    """Dissolve (union) a collection of geometries into a unified geometry.

    Args:
        geometries: List of OGR Geometry objects to union.

    Returns:
        Optional[ogr.Geometry]: Merged geometry, or None if input is empty.
    """
    if not geometries:
        return None

    # Filter out None and empty
    valid_geoms = [g for g in geometries if g is not None and not g.IsEmpty()]
    if not valid_geoms:
        return None

    try:
        unified = valid_geoms[0].Clone()
        for i, geom in enumerate(valid_geoms[1:], start=1):
            try:
                temp = unified.Union(geom)
                if temp is not None:
                    unified = temp
                else:
                    logger.warning(f"Union returned None at index {i}.")
            except Exception as exc:
                logger.warning(f"Failed to union geometry at index {i}: {exc}")

        if unified is None or unified.IsEmpty():
            return None

        if not unified.IsValid():
            unified = unified.Buffer(0)

        return unified
    except Exception as exc:
        logger.error(f"Error during geometry dissolution: {exc}")
        return None


def split_multipolygon_to_polygons(geometry: ogr.Geometry) -> list[ogr.Geometry]:
    """Split a MULTIPOLYGON geometry into individual POLYGON geometries.

    Args:
        geometry: Input POLYGON or MULTIPOLYGON geometry.

    Returns:
        list[ogr.Geometry]: List of individual POLYGON parts.
    """
    polygons: list[ogr.Geometry] = []
    if geometry is None or geometry.IsEmpty():
        return polygons

    geom_type = geometry.GetGeometryName().upper()

    if geom_type == "POLYGON":
        polygons.append(geometry.Clone())
    elif geom_type == "MULTIPOLYGON":
        for i in range(geometry.GetGeometryCount()):
            part = geometry.GetGeometryRef(i)
            if part is not None and not part.IsEmpty():
                polygons.append(part.Clone())
    else:
        logger.warning(f"Geometry type {geom_type} is not a Polygon/MultiPolygon.")

    return polygons
