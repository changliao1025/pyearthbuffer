"""Example: Creating multi-segment polyline buffer corridors using pyearthbuffer."""

import json
import os

from pyearthbuffer import gcsbuffer

# Setup output folders
data_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data")
)
out_folder = os.path.join(data_folder, "pypolyline")
os.makedirs(out_folder, exist_ok=True)

# Define polyline in WKT
polyline_wkt = "LINESTRING (-73.0 40.0, -73.0 41.0, -72.0 41.0)"
buffer_distance = 1000.0  # 1 km corridor half-width

# Buffer polyline
corridor_json = gcsbuffer(
    polyline_wkt, distance=buffer_distance, output_format="geojson"
)

out_file = os.path.join(out_folder, "polyline_buffer.geojson")
feature = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "name": "Highway Route",
                "corridor_half_width_m": buffer_distance,
            },
            "geometry": corridor_json,
        }
    ],
}
with open(out_file, "w") as f:
    json.dump(feature, f, indent=2)

print(f"Saved buffered polyline corridor to: {out_file}")
