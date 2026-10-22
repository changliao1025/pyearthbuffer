"""Example: Creating geodesic polygon buffer zones using pyearthbuffer."""

import json
import os

from pyearthbuffer import buffer

# Setup output folders
data_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data")
)
out_folder = os.path.join(data_folder, "pypolygon")
os.makedirs(out_folder, exist_ok=True)

# Define polygon in WKT
polygon_wkt = (
    "POLYGON ((-73.0 40.0, -73.0 42.0, -71.0 42.0, -72.0 41.0, -72.5 40.0, -73.0 40.0))"
)
buffer_distance = 50000.0  # 50 km buffer

# Buffer polygon to GeoJSON
buffered_polygon_json = buffer(
    polygon_wkt, distance=buffer_distance, output_format="geojson"
)

out_file = os.path.join(out_folder, "polygon_buffer.geojson")
feature = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "name": "Protected Zone Buffer",
                "buffer_m": buffer_distance,
            },
            "geometry": buffered_polygon_json,
        }
    ],
}
with open(out_file, "w") as f:
    json.dump(feature, f, indent=2)

print(f"Saved buffered polygon to: {out_file}")
