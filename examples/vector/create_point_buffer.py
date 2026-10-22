"""Example: Creating geodesic point buffer zones using pyearthbuffer."""

import json
import os

from pyearthbuffer import buffer, buffer_file

# Setup output folders
data_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data")
)
out_folder = os.path.join(data_folder, "point")
os.makedirs(out_folder, exist_ok=True)

# 1. Object-based point buffering
point_coords = (-73.935242, 40.730610)  # NYC (lon, lat)
buffer_radius = 10000.0  # 10 km

# Buffer to WKT
wkt_buffer = buffer(point_coords, distance=buffer_radius)
print("Point buffer WKT (first 60 chars):", wkt_buffer[:60])

# Buffer to GeoJSON
geojson_buffer = buffer(point_coords, distance=buffer_radius, output_format="geojson")

# Save to file
out_geojson_file = os.path.join(out_folder, "point_buffer.geojson")
feature = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "NYC 10km buffer", "radius_m": buffer_radius},
            "geometry": geojson_buffer,
        }
    ],
}
with open(out_geojson_file, "w") as f:
    json.dump(feature, f, indent=2)

print(f"Saved buffered point to: {out_geojson_file}")

# 2. File-based point buffering
batch_out_file = os.path.join(out_folder, "point_buffer_batch.geojson")
n_buffered = buffer_file(
    out_geojson_file,
    batch_out_file,
    distance=5000.0,
    preserve_attributes=True,
)
print(f"File buffer completed: {n_buffered} features written to {batch_out_file}")
