"""Object-based geodesic buffer operations for vector geometries."""

import logging
from typing import Any, Union

import numpy as np
from osgeo import ogr
from pyearth.toolbox.mesh.line import pyline
from pyearth.toolbox.mesh.point import pypoint
from pyearth.toolbox.mesh.polygon import pypolygon
from pyearth.toolbox.mesh.polyline import pypolyline

from pyearthbuffer.core.formats import from_ogr_geometry, to_ogr_geometry
from pyearthbuffer.core.validation import validate_distance, validate_num_points
from pyearthbuffer.vector.dissolve import (
    dissolve_geometries,
    extract_outer_ring_polygon,
)

logger = logging.getLogger(__name__)


def _buffer_point_ogr(geom: ogr.Geometry, distance: float, num_points: int = 60) -> ogr.Geometry:
    """Calculate geodesic buffer around an OGR Point geometry."""
    lon = geom.GetX()
    lat = geom.GetY()
    point_dict = {"dLongitude_degree": lon, "dLatitude_degree": lat}
    p_point = pypoint(point_dict)
    s_wkt, _ = p_point.calculate_buffer_zone_circle(distance, nPoint=num_points)
    out_geom = ogr.CreateGeometryFromWkt(s_wkt)
    if out_geom is None or out_geom.IsEmpty():
        raise RuntimeError(f"Failed to create point buffer geometry for ({lon}, {lat}).")
    return out_geom


def _buffer_multipoint_ogr(geom: ogr.Geometry, distance: float, num_points: int = 60) -> ogr.Geometry:
    """Calculate geodesic buffer around an OGR MultiPoint geometry."""
    n_pts = geom.GetGeometryCount()
    buffered_parts = []
    for i in range(n_pts):
        pt_geom = geom.GetGeometryRef(i)
        if pt_geom and not pt_geom.IsEmpty():
            buffered_parts.append(_buffer_point_ogr(pt_geom, distance, num_points))

    dissolved = dissolve_geometries(buffered_parts)
    if dissolved is None or dissolved.IsEmpty():
        raise RuntimeError("Failed to union MultiPoint buffer zones.")
    return dissolved


def _buffer_line_ogr(geom: ogr.Geometry, distance: float) -> ogr.Geometry:
    """Calculate geodesic buffer corridor around an OGR LineString geometry."""
    n_points = geom.GetPointCount()
    if n_points < 2:
        raise ValueError(f"LineString must contain at least 2 points, got {n_points}.")

    a_points = []
    for i in range(n_points):
        lon = geom.GetX(i)
        lat = geom.GetY(i)
        pt_dict = {"dLongitude_degree": lon, "dLatitude_degree": lat}
        a_points.append(pypoint(pt_dict))

    # Build edges skipping consecutive duplicates
    a_edges = []
    for i in range(len(a_points) - 1):
        if a_points[i] != a_points[i + 1]:
            a_edges.append(pyline(a_points[i], a_points[i + 1]))

    if not a_edges:
        raise ValueError("LineString contains no valid non-zero segments.")

    p_polyline = pypolyline(a_edges)
    s_wkt, _, _ = p_polyline.calculate_buffer_zone_polygon(distance)
    out_geom = ogr.CreateGeometryFromWkt(s_wkt)
    if out_geom is None or out_geom.IsEmpty():
        raise RuntimeError("Failed to create LineString buffer corridor.")
    return out_geom


def _buffer_multiline_ogr(geom: ogr.Geometry, distance: float) -> ogr.Geometry:
    """Calculate geodesic buffer around an OGR MultiLineString geometry."""
    n_lines = geom.GetGeometryCount()
    buffered_parts = []
    for i in range(n_lines):
        line_part = geom.GetGeometryRef(i)
        if line_part and not line_part.IsEmpty():
            buffered_parts.append(_buffer_line_ogr(line_part, distance))

    dissolved = dissolve_geometries(buffered_parts)
    if dissolved is None or dissolved.IsEmpty():
        raise RuntimeError("Failed to union MultiLineString buffer corridors.")
    return dissolved


def _buffer_single_polygon_ogr(geom: ogr.Geometry, distance: float) -> ogr.Geometry:
    """Calculate geodesic buffer around a single OGR Polygon exterior boundary."""
    ring = geom.GetGeometryRef(0)
    if ring is None:
        raise ValueError("Polygon has no exterior ring.")

    n_points = ring.GetPointCount()
    if n_points < 4:
        raise ValueError(f"Polygon ring has fewer than 4 points ({n_points}).")

    coords = np.array([[ring.GetX(i), ring.GetY(i)] for i in range(n_points)])
    # Clip coordinates to valid ranges
    coords[:, 0] = np.clip(coords[:, 0], -180.0, 180.0)
    coords[:, 1] = np.clip(coords[:, 1], -90.0, 90.0)

    n_unique_pts = len(coords) - 1
    a_point = [
        pypoint({"dLongitude_degree": coords[j, 0], "dLatitude_degree": coords[j, 1]})
        for j in range(n_unique_pts)
    ]

    # Filter consecutive duplicate points
    filtered_points = []
    for pt in a_point:
        if not filtered_points or pt != filtered_points[-1]:
            filtered_points.append(pt)

    if len(filtered_points) < 3:
        raise ValueError("Degenerate polygon with fewer than 3 unique vertices.")

    a_edge = [
        pyline(filtered_points[j], filtered_points[j + 1])
        for j in range(len(filtered_points) - 1)
    ]
    a_edge.append(pyline(filtered_points[-1], filtered_points[0]))

    d_lon_center = float(np.mean(coords[:, 0]))
    d_lat_center = float(np.mean(coords[:, 1]))
    p_poly = pypolygon(
        d_lon_center,
        d_lat_center,
        a_edge,
        filtered_points + [filtered_points[0]],
    )

    s_wkt, _, _ = p_poly.calculate_buffer_zone_polygon(distance)
    if not s_wkt:
        raise RuntimeError("Polygon buffer calculation returned empty WKT.")

    buffer_geom = ogr.CreateGeometryFromWkt(s_wkt)
    outer = extract_outer_ring_polygon(buffer_geom)
    if outer is None or outer.IsEmpty():
        raise RuntimeError("Failed to extract outer boundary from buffered polygon.")
    return outer


def _buffer_polygon_ogr(geom: ogr.Geometry, distance: float) -> ogr.Geometry:
    """Calculate geodesic buffer around an OGR Polygon geometry."""
    return _buffer_single_polygon_ogr(geom, distance)


def _buffer_multipolygon_ogr(geom: ogr.Geometry, distance: float) -> ogr.Geometry:
    """Calculate geodesic buffer around an OGR MultiPolygon geometry."""
    n_parts = geom.GetGeometryCount()
    buffered_parts = []
    for i in range(n_parts):
        poly_part = geom.GetGeometryRef(i)
        if poly_part and not poly_part.IsEmpty():
            try:
                buffered_parts.append(_buffer_single_polygon_ogr(poly_part, distance))
            except Exception as exc:
                logger.warning(f"Failed to buffer polygon part {i}: {exc}")

    dissolved = dissolve_geometries(buffered_parts)
    if dissolved is None or dissolved.IsEmpty():
        raise RuntimeError("Failed to union MultiPolygon buffer zones.")
    return dissolved


def buffer(
    geometry: Union[str, dict[str, Any], ogr.Geometry, tuple, list],
    distance: float,
    *,
    num_points: int = 60,
    output_format: str = "wkt",
) -> Union[str, dict[str, Any], ogr.Geometry]:
    """Calculate a geodesic buffer zone around a geometric feature on WGS84.

    Automatically identifies the geometry type (Point, MultiPoint, LineString,
    MultiLineString, Polygon, MultiPolygon) and applies geodesic buffering on the
    WGS84 ellipsoid.

    Args:
        geometry: Input geometry representation (WKT string, GeoJSON mapping/string,
            OGR Geometry instance, or coordinate sequence).
        distance: Buffer distance in meters. Must be positive.
        num_points: Number of points approximating circular arcs (for points and line caps).
        output_format: Format of returned geometry: "wkt" (default), "geojson", or "ogr".

    Returns:
        Union[str, dict, ogr.Geometry]: Buffered polygon in the requested format.

    Raises:
        TypeError: If distance or geometry inputs are invalid types.
        ValueError: If distance <= 0 or geometry parsing fails.
    """
    valid_dist = validate_distance(distance)
    valid_n_pts = validate_num_points(num_points)
    ogr_geom = to_ogr_geometry(geometry)

    geom_type = ogr_geom.GetGeometryName().upper()

    if geom_type == "POINT":
        res_geom = _buffer_point_ogr(ogr_geom, valid_dist, valid_n_pts)
    elif geom_type == "MULTIPOINT":
        res_geom = _buffer_multipoint_ogr(ogr_geom, valid_dist, valid_n_pts)
    elif geom_type == "LINESTRING":
        res_geom = _buffer_line_ogr(ogr_geom, valid_dist)
    elif geom_type == "MULTILINESTRING":
        res_geom = _buffer_multiline_ogr(ogr_geom, valid_dist)
    elif geom_type == "POLYGON":
        res_geom = _buffer_polygon_ogr(ogr_geom, valid_dist)
    elif geom_type == "MULTIPOLYGON":
        res_geom = _buffer_multipolygon_ogr(ogr_geom, valid_dist)
    elif geom_type == "GEOMETRYCOLLECTION":
        parts = []
        for i in range(ogr_geom.GetGeometryCount()):
            sub = ogr_geom.GetGeometryRef(i)
            if sub and not sub.IsEmpty():
                sub_buffered = buffer(sub, valid_dist, num_points=valid_n_pts, output_format="ogr")
                parts.append(sub_buffered)
        res_geom = dissolve_geometries(parts)
        if res_geom is None or res_geom.IsEmpty():
            raise RuntimeError("Failed to buffer GeometryCollection.")
    else:
        raise ValueError(f"Unsupported geometry type for buffering: '{geom_type}'.")

    return from_ogr_geometry(res_geom, output_format=output_format)


def buffer_point(
    point: Union[str, dict[str, Any], ogr.Geometry, tuple, list],
    distance: float,
    *,
    num_points: int = 60,
    output_format: str = "wkt",
) -> Union[str, dict[str, Any], ogr.Geometry]:
    """Calculate a geodesic buffer zone around a point on WGS84."""
    ogr_geom = to_ogr_geometry(point)
    geom_name = ogr_geom.GetGeometryName().upper()
    if geom_name not in ("POINT", "MULTIPOINT"):
        raise ValueError(f"Expected POINT or MULTIPOINT, got {geom_name}.")
    return buffer(ogr_geom, distance, num_points=num_points, output_format=output_format)


def buffer_line(
    line: Union[str, dict[str, Any], ogr.Geometry, tuple, list],
    distance: float,
    *,
    output_format: str = "wkt",
) -> Union[str, dict[str, Any], ogr.Geometry]:
    """Calculate a geodesic buffer corridor around a line on WGS84."""
    ogr_geom = to_ogr_geometry(line)
    geom_name = ogr_geom.GetGeometryName().upper()
    if geom_name not in ("LINESTRING", "MULTILINESTRING"):
        raise ValueError(f"Expected LINESTRING or MULTILINESTRING, got {geom_name}.")
    return buffer(ogr_geom, distance, output_format=output_format)


def buffer_polygon(
    polygon: Union[str, dict[str, Any], ogr.Geometry],
    distance: float,
    *,
    output_format: str = "wkt",
) -> Union[str, dict[str, Any], ogr.Geometry]:
    """Calculate a geodesic buffer zone around a polygon on WGS84."""
    ogr_geom = to_ogr_geometry(polygon)
    geom_name = ogr_geom.GetGeometryName().upper()
    if geom_name not in ("POLYGON", "MULTIPOLYGON"):
        raise ValueError(f"Expected POLYGON or MULTIPOLYGON, got {geom_name}.")
    return buffer(ogr_geom, distance, output_format=output_format)
