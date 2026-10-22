"""Unit tests for file-based vector geodesic buffer operations."""

import json
from pathlib import Path

import pytest
from osgeo import ogr

from pyearthbuffer import (
    gcsbuffer_file,
    gcsbuffer_line_file,
    gcsbuffer_point_file,
    gcsbuffer_polygon_file,
)


@pytest.fixture
def sample_points_geojson(tmp_path: Path) -> Path:
    data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Point A", "val": 10},
                "geometry": {"type": "Point", "coordinates": [-74.006, 40.7128]},
            },
            {
                "type": "Feature",
                "properties": {"name": "Point B", "val": 20},
                "geometry": {"type": "Point", "coordinates": [-73.990, 40.7200]},
            },
        ],
    }
    file_path = tmp_path / "points.geojson"
    file_path.write_text(json.dumps(data))
    return file_path


@pytest.fixture
def sample_lines_geojson(tmp_path: Path) -> Path:
    data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"route": "Route 1"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[-74.006, 40.7128], [-73.990, 40.7200]],
                },
            }
        ],
    }
    file_path = tmp_path / "lines.geojson"
    file_path.write_text(json.dumps(data))
    return file_path


@pytest.fixture
def sample_polygons_geojson(tmp_path: Path) -> Path:
    data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"zone": "Zone 1"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-74.0, 40.7],
                            [-74.0, 40.8],
                            [-73.9, 40.8],
                            [-73.9, 40.7],
                            [-74.0, 40.7],
                        ]
                    ],
                },
            }
        ],
    }
    file_path = tmp_path / "polygons.geojson"
    file_path.write_text(json.dumps(data))
    return file_path


class TestVectorFileBuffer:
    """Tests for vector file buffering."""

    def test_buffer_points_file(self, sample_points_geojson: Path, tmp_path: Path):
        output_file = tmp_path / "points_buffered.geojson"
        count = gcsbuffer_file(sample_points_geojson, output_file, distance=1000.0)

        assert count == 2
        assert output_file.exists()

        ds = ogr.Open(str(output_file))
        layer = ds.GetLayer()
        assert layer.GetFeatureCount() == 2

        feat = layer.GetNextFeature()
        assert feat.GetGeometryRef().GetGeometryName() == "POLYGON"
        assert feat.GetField("name") == "Point A"
        assert feat.GetField("val") == 10
        ds = None

    def test_buffer_lines_file(self, sample_lines_geojson: Path, tmp_path: Path):
        output_file = tmp_path / "lines_buffered.geojson"
        count = gcsbuffer_line_file(sample_lines_geojson, output_file, distance=100.0)

        assert count == 1
        assert output_file.exists()

        ds = ogr.Open(str(output_file))
        layer = ds.GetLayer()
        feat = layer.GetNextFeature()
        assert feat.GetGeometryRef().GetGeometryName() == "POLYGON"
        assert feat.GetField("route") == "Route 1"
        ds = None

    def test_buffer_polygons_file(self, sample_polygons_geojson: Path, tmp_path: Path):
        output_file = tmp_path / "polygons_buffered.geojson"
        count = gcsbuffer_polygon_file(
            sample_polygons_geojson, output_file, distance=500.0
        )

        assert count == 1
        assert output_file.exists()

        ds = ogr.Open(str(output_file))
        layer = ds.GetLayer()
        feat = layer.GetNextFeature()
        assert feat.GetGeometryRef().GetGeometryName() == "POLYGON"
        assert feat.GetField("zone") == "Zone 1"
        ds = None

    def test_buffer_file_with_dissolve(
        self, sample_points_geojson: Path, tmp_path: Path
    ):
        output_file = tmp_path / "points_dissolved.geojson"
        # 100km distance ensures point buffers overlap and dissolve into 1 unified polygon
        count = gcsbuffer_file(
            sample_points_geojson, output_file, distance=100000.0, dissolve=True
        )

        assert count >= 1
        assert output_file.exists()

        ds = ogr.Open(str(output_file))
        layer = ds.GetLayer()
        feat = layer.GetNextFeature()
        assert feat.GetGeometryRef().GetGeometryName() == "POLYGON"
        assert feat.GetField("buffer_dist") == 100000.0
        ds = None

    def test_buffer_file_missing_input_raises_error(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            gcsbuffer_file(
                tmp_path / "nonexistent.geojson",
                tmp_path / "out.geojson",
                distance=100.0,
            )

    def test_buffer_file_negative_distance_raises_error(
        self, sample_points_geojson: Path, tmp_path: Path
    ):
        with pytest.raises(ValueError, match="must be positive"):
            gcsbuffer_file(
                sample_points_geojson, tmp_path / "out.geojson", distance=-50.0
            )
