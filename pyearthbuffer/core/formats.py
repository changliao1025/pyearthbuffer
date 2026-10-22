"""Geometry format conversion and normalization utilities."""

import json
from typing import Any, Union

from osgeo import ogr, osr

from pyearthbuffer.core.validation import validate_coordinates


def ensure_wgs84_spatial_ref() -> osr.SpatialReference:
    """Return an EPSG:4326 spatial reference system."""
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    return srs


def to_ogr_geometry(geom_input: Any) -> ogr.Geometry:
    """Normalize input geometry into an OGR Geometry object.

    Supports:
    - ogr.Geometry (returns a clone)
    - WKT string (e.g. 'POINT (-74.0 40.7)')
    - GeoJSON mapping (dict) or GeoJSON string
    - Coordinate tuple/list of 2 numbers: (lon, lat) -> POINT

    Args:
        geom_input: The input geometry representation.

    Returns:
        ogr.Geometry: An OGR Geometry in WGS84 coordinates.

    Raises:
        TypeError: If input type is not supported.
        ValueError: If parsing fails or geometry is invalid.
    """
    if geom_input is None:
        raise TypeError("Geometry input cannot be None.")

    # 1. Already an ogr.Geometry
    if isinstance(geom_input, ogr.Geometry):
        geom = geom_input.Clone()
        if geom.IsEmpty():
            raise ValueError("Input geometry is empty.")
        return geom

    # 2. Coordinate tuple/list: (lon, lat)
    if isinstance(geom_input, (tuple, list)):
        if len(geom_input) == 2 and all(isinstance(c, (int, float)) for c in geom_input):
            lon, lat = validate_coordinates(geom_input[0], geom_input[1])
            pt = ogr.Geometry(ogr.wkbPoint)
            pt.AddPoint(lon, lat)
            return pt
        raise ValueError(
            f"Ambiguous coordinate sequence with {len(geom_input)} elements. "
            "Use WKT or GeoJSON for complex geometries."
        )

    # 3. GeoJSON dictionary
    if isinstance(geom_input, dict):
        if "type" not in geom_input:
            raise ValueError("GeoJSON dictionary must contain a 'type' field.")
        geom_json_str = json.dumps(geom_input)
        geom = ogr.CreateGeometryFromJson(geom_json_str)
        if geom is None:
            raise ValueError("Failed to parse GeoJSON dictionary into geometry.")
        return geom

    # 4. String (WKT or GeoJSON string)
    if isinstance(geom_input, str):
        s_input = geom_input.strip()
        if not s_input:
            raise ValueError("Geometry string cannot be empty.")

        # Check if JSON
        if s_input.startswith("{") and s_input.endswith("}"):
            geom = ogr.CreateGeometryFromJson(s_input)
            if geom is not None and not geom.IsEmpty():
                return geom
            raise ValueError("Failed to parse GeoJSON string into geometry.")

        # Try WKT
        try:
            geom = ogr.CreateGeometryFromWkt(s_input)
        except Exception as exc:
            raise ValueError(f"Failed to parse WKT string: {exc}") from exc

        if geom is None or geom.IsEmpty():
            raise ValueError(f"Invalid or empty WKT string: {s_input}")
        return geom

    raise TypeError(
        f"Unsupported geometry type: {type(geom_input).__name__}. "
        "Expected WKT string, GeoJSON dict, OGR Geometry, or (lon, lat) tuple."
    )


def from_ogr_geometry(
    ogr_geom: ogr.Geometry, output_format: str = "wkt"
) -> Union[str, dict[str, Any], ogr.Geometry]:
    """Format an OGR Geometry into the requested output format.

    Args:
        ogr_geom: The OGR Geometry to convert.
        output_format: Target format: "wkt", "geojson", or "ogr".

    Returns:
        Union[str, dict, ogr.Geometry]: Formatted geometry.

    Raises:
        ValueError: If output_format is not recognized.
    """
    if ogr_geom is None:
        raise ValueError("Cannot format None geometry.")

    fmt = output_format.strip().lower()

    if fmt == "ogr":
        return ogr_geom.Clone()

    if fmt == "wkt":
        ogr_geom.FlattenTo2D()
        return ogr_geom.ExportToWkt()

    if fmt == "geojson":
        ogr_geom.FlattenTo2D()
        json_str = ogr_geom.ExportToJson()
        return json.loads(json_str)

    raise ValueError(
        f"Unsupported output format: '{output_format}'. "
        "Supported formats are 'wkt', 'geojson', and 'ogr'."
    )
