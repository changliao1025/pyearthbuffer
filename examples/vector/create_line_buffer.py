"""Example: Creating geodesic line buffer corridors using pyearthbuffer."""

import json
import os

from pyearthbuffer import buffer

# Setup output folders
data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
out_folder = os.path.join(data_folder, "pyline")
os.makedirs(out_folder, exist_ok=True)

# Define line in WKT format
line_wkt = "LINESTRING (-73.935242 40.730610, -73.995242 40.790610)"
buffer_distance = 1000.0  # 1 km corridor half-width

# Buffer line to GeoJSON
geojson_corridor = buffer(line_wkt, distance=buffer_distance, output_format="geojson")

out_file = os.path.join(out_folder, "line_buffer.geojson")
feature = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "Road Corridor", "buffer_distance_m": buffer_distance},
            "geometry": geojson_corridor,
        }
    ],
}
with open(out_file, "w") as f:
    json.dump(feature, f, indent=2)

print(f"Saved buffered line corridor to: {out_file}")
