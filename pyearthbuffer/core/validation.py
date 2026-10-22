"""Input validation utilities for geodesic buffer operations."""

from typing import Any


def validate_distance(distance: Any) -> float:
    """Validate that buffer distance is a positive number.

    Args:
        distance: Buffer distance in meters.

    Returns:
        float: Validated buffer distance.

    Raises:
        TypeError: If distance is None or cannot be converted to float.
        ValueError: If distance is less than or equal to zero.
    """
    if distance is None:
        raise TypeError("Buffer distance cannot be None.")

    try:
        dist = float(distance)
    except (ValueError, TypeError) as exc:
        raise TypeError(
            f"Buffer distance must be numeric, got {type(distance).__name__}."
        ) from exc

    if dist <= 0:
        raise ValueError(f"Buffer distance must be positive, got {dist}.")

    return dist


def validate_coordinates(lon: float, lat: float) -> tuple[float, float]:
    """Validate geographic coordinates on WGS84 ellipsoid.

    Args:
        lon: Longitude in degrees.
        lat: Latitude in degrees.

    Returns:
        tuple[float, float]: Validated (longitude, latitude) pair.

    Raises:
        TypeError: If coordinates are not numeric.
        ValueError: If latitude or longitude are outside valid ranges.
    """
    try:
        lon_f = float(lon)
        lat_f = float(lat)
    except (ValueError, TypeError) as exc:
        raise TypeError("Coordinates must be numeric.") from exc

    if not (-180.0 <= lon_f <= 180.0):
        raise ValueError(
            f"Longitude must be in range [-180, 180], got {lon_f}."
        )

    if not (-90.0 <= lat_f <= 90.0):
        raise ValueError(
            f"Latitude must be in range [-90, 90], got {lat_f}."
        )

    return lon_f, lat_f


def validate_num_points(num_points: int) -> int:
    """Validate the number of points approximating circular arcs.

    Args:
        num_points: Number of points.

    Returns:
        int: Validated number of points.

    Raises:
        ValueError: If num_points < 3.
    """
    n = int(num_points)
    if n < 3:
        raise ValueError(f"num_points must be at least 3, got {n}.")
    return n
