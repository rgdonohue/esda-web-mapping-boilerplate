import json
import math
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from app.schemas.geospatial import (
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    GeoJSONType,
    LineStringGeometry,
    PointGeometry,
    PolygonGeometry,
)
from app.utils.enhanced_logging import get_logger

logger = get_logger(__name__)


class DistanceUnit(str, Enum):
    """Units for distance calculations"""

    METERS = "meters"
    KILOMETERS = "kilometers"
    MILES = "miles"
    NAUTICAL_MILES = "nautical_miles"
    FEET = "feet"


# Earth radius in different units
EARTH_RADIUS = {
    DistanceUnit.METERS: 6371000,
    DistanceUnit.KILOMETERS: 6371,
    DistanceUnit.MILES: 3958.8,
    DistanceUnit.NAUTICAL_MILES: 3440.1,
    DistanceUnit.FEET: 20902231,
}


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians"""
    return degrees * (math.pi / 180)


def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees"""
    return radians * (180 / math.pi)


def haversine_distance(
    point1: Tuple[float, float],
    point2: Tuple[float, float],
    unit: DistanceUnit = DistanceUnit.METERS,
) -> float:
    """Calculate the great-circle distance between two points on the Earth's surface.

    Args:
        point1: Tuple of (longitude, latitude) in decimal degrees
        point2: Tuple of (longitude, latitude) in decimal degrees
        unit: Unit of distance (default: meters)

    Returns:
        Distance between the points in the specified unit
    """
    # Extract coordinates
    lon1, lat1 = point1
    lon2, lat2 = point2

    # Convert to radians
    lat1_rad = degrees_to_radians(lat1)
    lon1_rad = degrees_to_radians(lon1)
    lat2_rad = degrees_to_radians(lat2)
    lon2_rad = degrees_to_radians(lon2)

    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = EARTH_RADIUS[unit] * c

    return distance


def calculate_bbox(features: List[Dict[str, Any]]) -> List[float]:
    """Calculate the bounding box for a collection of GeoJSON features.

    Args:
        features: List of GeoJSON features

    Returns:
        Bounding box as [min_lon, min_lat, max_lon, max_lat]
    """
    if not features:
        return [0, 0, 0, 0]

    # Initialize with extreme values
    min_lon = 180
    min_lat = 90
    max_lon = -180
    max_lat = -90

    for feature in features:
        # Skip features without geometry
        if "geometry" not in feature or not feature["geometry"]:
            continue

        geometry = feature["geometry"]
        geometry_type = geometry.get("type")
        coordinates = geometry.get("coordinates", [])

        if not coordinates:
            continue

        # Process based on geometry type
        if geometry_type == GeoJSONType.Point:
            lon, lat = coordinates
            min_lon = min(min_lon, lon)
            min_lat = min(min_lat, lat)
            max_lon = max(max_lon, lon)
            max_lat = max(max_lat, lat)

        elif geometry_type == GeoJSONType.LineString:
            for point in coordinates:
                lon, lat = point
                min_lon = min(min_lon, lon)
                min_lat = min(min_lat, lat)
                max_lon = max(max_lon, lon)
                max_lat = max(max_lat, lat)

        elif geometry_type == GeoJSONType.Polygon:
            for ring in coordinates:
                for point in ring:
                    lon, lat = point
                    min_lon = min(min_lon, lon)
                    min_lat = min(min_lat, lat)
                    max_lon = max(max_lon, lon)
                    max_lat = max(max_lat, lat)

        elif geometry_type == GeoJSONType.MultiPoint:
            for point in coordinates:
                lon, lat = point
                min_lon = min(min_lon, lon)
                min_lat = min(min_lat, lat)
                max_lon = max(max_lon, lon)
                max_lat = max(max_lat, lat)

        elif geometry_type == GeoJSONType.MultiLineString:
            for line in coordinates:
                for point in line:
                    lon, lat = point
                    min_lon = min(min_lon, lon)
                    min_lat = min(min_lat, lat)
                    max_lon = max(max_lon, lon)
                    max_lat = max(max_lat, lat)

        elif geometry_type == GeoJSONType.MultiPolygon:
            for polygon in coordinates:
                for ring in polygon:
                    for point in ring:
                        lon, lat = point
                        min_lon = min(min_lon, lon)
                        min_lat = min(min_lat, lat)
                        max_lon = max(max_lon, lon)
                        max_lat = max(max_lat, lat)

    return [min_lon, min_lat, max_lon, max_lat]


def point_in_bbox(point: Tuple[float, float], bbox: List[float]) -> bool:
    """Check if a point is within a bounding box.

    Args:
        point: Tuple of (longitude, latitude) in decimal degrees
        bbox: Bounding box as [min_lon, min_lat, max_lon, max_lat]

    Returns:
        True if the point is within the bounding box, False otherwise
    """
    lon, lat = point
    min_lon, min_lat, max_lon, max_lat = bbox

    return (min_lon <= lon <= max_lon) and (min_lat <= lat <= max_lat)


def buffer_point(
    point: Tuple[float, float],
    distance: float,
    unit: DistanceUnit = DistanceUnit.METERS,
    num_points: int = 32,
) -> Dict[str, Any]:
    """Create a circular buffer around a point.

    Args:
        point: Tuple of (longitude, latitude) in decimal degrees
        distance: Buffer distance
        unit: Unit of distance (default: meters)
        num_points: Number of points to use for the circle (default: 32)

    Returns:
        GeoJSON Polygon representing the buffer
    """
    lon, lat = point

    # Convert distance to radians
    distance_rad = distance / EARTH_RADIUS[unit]

    # Create circle points
    coordinates = []
    for i in range(num_points + 1):  # +1 to close the polygon
        angle = 2 * math.pi * i / num_points
        lat_rad = degrees_to_radians(lat)
        lon_rad = degrees_to_radians(lon)

        # Calculate new point
        new_lat_rad = math.asin(
            math.sin(lat_rad) * math.cos(distance_rad)
            + math.cos(lat_rad) * math.sin(distance_rad) * math.cos(angle)
        )
        new_lon_rad = lon_rad + math.atan2(
            math.sin(angle) * math.sin(distance_rad) * math.cos(lat_rad),
            math.cos(distance_rad) - math.sin(lat_rad) * math.sin(new_lat_rad),
        )

        # Convert back to degrees
        new_lat = radians_to_degrees(new_lat_rad)
        new_lon = radians_to_degrees(new_lon_rad)

        coordinates.append([new_lon, new_lat])

    # Create GeoJSON polygon
    return {"type": GeoJSONType.Polygon, "coordinates": [coordinates]}


def simplify_geometry(geometry: Dict[str, Any], tolerance: float = 0.00001) -> Dict[str, Any]:
    """Simplify a geometry using the Douglas-Peucker algorithm.

    This is a simple implementation for demonstration. For production use,
    consider using a library like Shapely.

    Args:
        geometry: GeoJSON geometry object
        tolerance: Simplification tolerance

    Returns:
        Simplified GeoJSON geometry
    """
    # This is a placeholder implementation
    # In a real application, you would use a library like Shapely
    return geometry


def parse_bbox_string(bbox_str: str) -> List[float]:
    """Parse a bbox string into a list of floats.

    Args:
        bbox_str: Bounding box string in format "min_lon,min_lat,max_lon,max_lat"

    Returns:
        Bounding box as [min_lon, min_lat, max_lon, max_lat]
    """
    try:
        bbox = [float(x) for x in bbox_str.split(",")]
        if len(bbox) != 4:
            raise ValueError("Bounding box must have 4 values")
        return bbox
    except Exception as e:
        logger.error(f"Error parsing bbox string: {str(e)}")
        raise ValueError(
            f"Invalid bbox format: {bbox_str}. Expected format: min_lon,min_lat,max_lon,max_lat"
        )


def parse_point_string(point_str: str) -> Tuple[float, float]:
    """Parse a point string into a tuple of floats.

    Args:
        point_str: Point string in format "lon,lat"

    Returns:
        Point as (lon, lat)
    """
    try:
        coords = [float(x) for x in point_str.split(",")]
        if len(coords) != 2:
            raise ValueError("Point must have 2 values")
        return (coords[0], coords[1])
    except Exception as e:
        logger.error(f"Error parsing point string: {str(e)}")
        raise ValueError(f"Invalid point format: {point_str}. Expected format: lon,lat")


def geojson_to_dict(geojson_obj: Union[GeoJSONFeature, GeoJSONFeatureCollection]) -> Dict[str, Any]:
    """Convert a GeoJSON Pydantic model to a dictionary.

    Args:
        geojson_obj: GeoJSON Pydantic model

    Returns:
        Dictionary representation of the GeoJSON object
    """
    return json.loads(geojson_obj.json())


def dict_to_geojson(
    geojson_dict: Dict[str, Any],
) -> Union[GeoJSONFeature, GeoJSONFeatureCollection]:
    """Convert a dictionary to a GeoJSON Pydantic model.

    Args:
        geojson_dict: Dictionary representation of a GeoJSON object

    Returns:
        GeoJSON Pydantic model
    """
    if geojson_dict.get("type") == GeoJSONType.Feature:
        return GeoJSONFeature(**geojson_dict)
    elif geojson_dict.get("type") == GeoJSONType.FeatureCollection:
        return GeoJSONFeatureCollection(**geojson_dict)
    else:
        raise ValueError(f"Unsupported GeoJSON type: {geojson_dict.get('type')}")
