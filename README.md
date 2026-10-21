# pyearthbuffer

Geographic Coordinate System (GCS) Buffer Operations in Python.

If you find this package useful, please cite it in your work.
You can also support it by [buying me a coffee](https://www.buymeacoffee.com/changliao) or sponsoring it on [GitHub](https://github.com/sponsors/changliao1025).

## Dependencies

`pyearthbuffer` depends on the following packages:

1. `numpy`
2. `gdal`
3. `scipy`
4. `geographiclib`
5. `matplotlib`
6. `cartopy`
7. `pyearth`

## Documentation

Please refer to the [documentation](https://pyearthbuffer.readthedocs.io) for details on how to get started using the `pyearthbuffer` package.

## Installation

`pyearthbuffer` depends on several geospatial packages including `gdal`, which are most reliably installed through `conda`:

```bash
conda install -c conda-forge pyearthbuffer
```

Or install from source in editable mode:

```bash
pip install -e .
```

## Features

`pyearthbuffer` provides geodesic buffer operations on the WGS84 ellipsoid:

1. **Vector-based buffer calculations**:
   - Point buffers (`create_point_buffer_zone` or `pypoint.calculate_buffer_zone`)
   - Line and Polyline buffers (`create_polyline_buffer_zone` or `pypolyline.calculate_buffer_zone_polygon`)
   - Polygon buffers (`create_buffer_zone_polygon_file` or `pypolygon.calculate_buffer_zone_polygon`)
2. **Raster-based buffer calculations**:
   - Binary mask buffer zone calculation (`RasterBuffer` / `gcstiff.calculate_binary_mask_buffer_zone`)

## Acknowledgment

This research was supported as part of the Next Generation Ecosystem Experiments-Tropics, funded by the U.S. Department of Energy, Office of Science, Office of Biological and Environmental Research at Pacific Northwest National Laboratory. The study was also partly supported by U.S. Department of Energy Office of Science Biological and Environmental Research through the Earth and Environmental System Modeling program as part of the Energy Exascale Earth System Model (E3SM) project.

## License

BSD 3-Clause License. See [LICENSE.md](LICENSE.md) for details.
