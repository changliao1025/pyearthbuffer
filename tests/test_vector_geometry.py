"""Unit tests for object-based vector geodesic buffer operations."""

import pytest
from osgeo import ogr

from pyearthbuffer import (
    buffer,
    buffer_line,
    buffer_point,
    buffer_polygon,
)


class TestPointBuffer:
    """Tests for buffering point geometries."""

    def test_buffer_point_from_tuple(self):
        result_wkt = buffer((-74.006, 40.7128), distance=1000.0)
        assert isinstance(result_wkt, str)
        assert result_wkt.startswith("POLYGON")

    def test_buffer_point_from_wkt(self):
        wkt_in = "POINT (-74.0060 40.7128)"
        result_wkt = buffer(wkt_in, distance=500.0)
        assert isinstance(result_wkt, str)
        assert result_wkt.startswith("POLYGON")

    def test_buffer_point_geojson_output(self):
        result_json = buffer((-74.006, 40.7128), distance=1000.0, output_format="geojson")
        assert isinstance(result_json, dict)
        assert result_json["type"] == "Polygon"
        assert len(result_json["coordinates"][0]) >= 30

    def test_buffer_point_ogr_output(self):
        result_ogr = buffer((-74.006, 40.7128), distance=1000.0, output_format="ogr")
        assert isinstance(result_ogr, ogr.Geometry)
        assert result_ogr.GetGeometryName() == "POLYGON"

    def test_buffer_point_specific_function(self):
        res = buffer_point("POINT (0.0 51.5)", distance=200.0)
        assert isinstance(res, str)
        assert res.startswith("POLYGON")

    def test_buffer_point_rejects_non_point(self):
        with pytest.raises(ValueError, match="Expected POINT"):
            buffer_point("LINESTRING (0 0, 1 1)", distance=100.0)


class TestLineBuffer:
    """Tests for buffering line geometries."""

    def test_buffer_line_from_wkt(self):
        line_wkt = "LINESTRING (-74.006 40.7128, -73.990 40.7200)"
        result_wkt = buffer(line_wkt, distance=50.0)
        assert isinstance(result_wkt, str)
        assert result_wkt.startswith("POLYGON")

    def test_buffer_line_specific_function(self):
        line_wkt = "LINESTRING (0.0 51.5, 0.1 51.6)"
        result_wkt = buffer_line(line_wkt, distance=100.0)
        assert isinstance(result_wkt, str)
        assert result_wkt.startswith("POLYGON")

    def test_buffer_line_rejects_non_line(self):
        with pytest.raises(ValueError, match="Expected LINESTRING"):
            buffer_line("POINT (0 0)", distance=50.0)

    def test_buffer_line_rejects_single_point(self):
        with pytest.raises(ValueError, match="at least 2 points"):
            buffer_line("LINESTRING (0 0)", distance=50.0)


class TestPolygonBuffer:
    """Tests for buffering polygon geometries."""

    def test_buffer_polygon_from_wkt(self):
        poly_wkt = "POLYGON ((-74.0 40.7, -74.0 40.8, -73.9 40.8, -73.9 40.7, -74.0 40.7))"
        result_wkt = buffer(poly_wkt, distance=500.0)
        assert isinstance(result_wkt, str)
        assert result_wkt.startswith("POLYGON")

    def test_buffer_polygon_specific_function(self):
        poly_wkt = "POLYGON ((-74.0 40.7, -74.0 40.8, -73.9 40.8, -73.9 40.7, -74.0 40.7))"
        result_wkt = buffer_polygon(poly_wkt, distance=500.0)
        assert isinstance(result_wkt, str)
        assert result_wkt.startswith("POLYGON")

    def test_buffer_polygon_rejects_non_polygon(self):
        with pytest.raises(ValueError, match="Expected POLYGON"):
            buffer_polygon("POINT (0 0)", distance=500.0)


class TestValidationAndErrors:
    """Tests for input validation and error handling."""

    def test_negative_distance_raises_value_error(self):
        with pytest.raises(ValueError, match="must be positive"):
            buffer((-74.0, 40.7), distance=-100.0)

    def test_zero_distance_raises_value_error(self):
        with pytest.raises(ValueError, match="must be positive"):
            buffer((-74.0, 40.7), distance=0.0)

    def test_non_numeric_distance_raises_type_error(self):
        with pytest.raises(TypeError, match="must be numeric"):
            buffer((-74.0, 40.7), distance="invalid")

    def test_invalid_coordinates_range_raises_error(self):
        with pytest.raises(ValueError, match="Longitude must be in range"):
            buffer((250.0, 40.0), distance=100.0)

    def test_invalid_output_format_raises_error(self):
        with pytest.raises(ValueError, match="Unsupported output format"):
            buffer((-74.0, 40.7), distance=100.0, output_format="shapefile")
