from typing import List, Dict, Any, Optional, Union, Tuple
from pydantic import BaseModel, Field, validator, root_validator
import re
import json
from enum import Enum

from app.schemas.geospatial import (
    GeoJSONType, 
    PointGeometry, 
    LineStringGeometry, 
    PolygonGeometry,
    GeoJSONFeature,
    GeoJSONFeatureCollection
)

# Coordinate Reference System (CRS) validation
class CRSType(str, Enum):
    NAME = "name"
    LINK = "link"

class NamedCRS(BaseModel):
    type: str = Field("name")
    properties: Dict[str, str] = Field(...)
    
    @validator('properties')
    def validate_properties(cls, v):
        if 'name' not in v:
            raise ValueError("CRS name properties must contain a 'name' field")
        
        # Validate EPSG code format
        name = v['name']
        if not re.match(r'^EPSG:\d+$', name):
            raise ValueError(f"Invalid CRS name format: {name}. Expected format: 'EPSG:code'")
        
        return v

class LinkedCRS(BaseModel):
    type: str = Field("link")
    properties: Dict[str, str] = Field(...)
    
    @validator('properties')
    def validate_properties(cls, v):
        if 'href' not in v:
            raise ValueError("CRS link properties must contain an 'href' field")
        if 'type' not in v:
            raise ValueError("CRS link properties must contain a 'type' field")
        return v

# Union type for CRS
CRS = Union[NamedCRS, LinkedCRS]

# Enhanced GeoJSON validation models
class EnhancedGeoJSONFeature(GeoJSONFeature):
    id: Optional[Union[str, int]] = None
    bbox: Optional[List[float]] = None
    crs: Optional[CRS] = None
    
    @validator('bbox')
    def validate_bbox(cls, v):
        if v is not None:
            if len(v) != 4 and len(v) != 6:  # 2D or 3D bounding box
                raise ValueError("Bounding box must have 4 values (2D) or 6 values (3D)")
            
            if len(v) == 4:
                min_lon, min_lat, max_lon, max_lat = v
                if min_lon > max_lon or min_lat > max_lat:
                    raise ValueError("Invalid bounding box: min values must be less than max values")
            elif len(v) == 6:
                min_lon, min_lat, min_z, max_lon, max_lat, max_z = v
                if min_lon > max_lon or min_lat > max_lat or min_z > max_z:
                    raise ValueError("Invalid bounding box: min values must be less than max values")
        return v
    
    @root_validator
    def validate_feature(cls, values):
        # Additional validation logic for the entire feature
        return values

class EnhancedGeoJSONFeatureCollection(GeoJSONFeatureCollection):
    bbox: Optional[List[float]] = None
    crs: Optional[CRS] = None
    
    @validator('bbox')
    def validate_bbox(cls, v):
        if v is not None:
            if len(v) != 4 and len(v) != 6:  # 2D or 3D bounding box
                raise ValueError("Bounding box must have 4 values (2D) or 6 values (3D)")
            
            if len(v) == 4:
                min_lon, min_lat, max_lon, max_lat = v
                if min_lon > max_lon or min_lat > max_lat:
                    raise ValueError("Invalid bounding box: min values must be less than max values")
            elif len(v) == 6:
                min_lon, min_lat, min_z, max_lon, max_lat, max_z = v
                if min_lon > max_lon or min_lat > max_lat or min_z > max_z:
                    raise ValueError("Invalid bounding box: min values must be less than max values")
        return v

# Enhanced spatial query parameters
class EnhancedSpatialQueryParams(BaseModel):
    bbox: Optional[str] = Field(
        None, 
        description="Bounding box in format: minLon,minLat,maxLon,maxLat or minLon,minLat,minZ,maxLon,maxLat,maxZ"
    )
    distance: Optional[float] = Field(
        None,
        description="Distance in meters for proximity queries",
        gt=0
    )
    coordinates: Optional[str] = Field(
        None,
        description="Point coordinates in format: lon,lat or lon,lat,z"
    )
    projection: Optional[str] = Field(
        None,
        description="Coordinate reference system (e.g., EPSG:4326)"
    )
    
    @validator('bbox')
    def validate_bbox(cls, v):
        if v:
            try:
                coords = [float(x) for x in v.split(',')]
                if len(coords) != 4 and len(coords) != 6:
                    raise ValueError("Bounding box must have 4 values (2D) or 6 values (3D)")
                
                if len(coords) == 4:
                    min_lon, min_lat, max_lon, max_lat = coords
                    if min_lon < -180 or max_lon > 180 or min_lat < -90 or max_lat > 90:
                        raise ValueError("Coordinates out of bounds")
                    if min_lon > max_lon or min_lat > max_lat:
                        raise ValueError("Min values must be less than max values")
                elif len(coords) == 6:
                    min_lon, min_lat, min_z, max_lon, max_lat, max_z = coords
                    if min_lon < -180 or max_lon > 180 or min_lat < -90 or max_lat > 90:
                        raise ValueError("Coordinates out of bounds")
                    if min_lon > max_lon or min_lat > max_lat or min_z > max_z:
                        raise ValueError("Min values must be less than max values")
            except ValueError as e:
                raise ValueError(f"Invalid bbox format: {str(e)}")
        return v
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        if v:
            try:
                coords = [float(x) for x in v.split(',')]
                if len(coords) != 2 and len(coords) != 3:
                    raise ValueError("Coordinates must have 2 values (2D) or 3 values (3D)")
                
                lon = coords[0]
                lat = coords[1]
                if lon < -180 or lon > 180 or lat < -90 or lat > 90:
                    raise ValueError("Coordinates out of bounds")
            except ValueError as e:
                raise ValueError(f"Invalid coordinates format: {str(e)}")
        return v
    
    @validator('projection')
    def validate_projection(cls, v):
        if v and not re.match(r'^EPSG:\d+$', v):
            raise ValueError(f"Invalid projection format: {v}. Expected format: 'EPSG:code'")
        return v

# Utility functions for geospatial validation
def validate_geojson_string(geojson_str: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
    """Validate a GeoJSON string and return validation status, error message, and parsed object"""
    try:
        # Parse JSON
        geojson = json.loads(geojson_str)
        
        # Check if it has a type field
        if 'type' not in geojson:
            return False, "Missing 'type' field", None
        
        # Validate based on type
        geojson_type = geojson['type']
        
        if geojson_type == GeoJSONType.Feature:
            # Validate as Feature
            EnhancedGeoJSONFeature(**geojson)
            return True, None, geojson
        
        elif geojson_type == GeoJSONType.FeatureCollection:
            # Validate as FeatureCollection
            EnhancedGeoJSONFeatureCollection(**geojson)
            return True, None, geojson
        
        elif geojson_type in [t.value for t in GeoJSONType]:
            # It's a valid GeoJSON type but not a Feature or FeatureCollection
            # For simplicity, we're not validating all geometry types here
            return True, None, geojson
        
        else:
            return False, f"Invalid GeoJSON type: {geojson_type}", None
            
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}", None
    except ValueError as e:
        return False, f"Validation error: {str(e)}", None
    except Exception as e:
        return False, f"Unexpected error: {str(e)}", None

def calculate_bbox_from_geojson(geojson: Dict[str, Any]) -> List[float]:
    """Calculate bounding box from a GeoJSON object"""
    # Implementation would extract all coordinates and find min/max values
    # This is a simplified placeholder
    return [0, 0, 0, 0]  # [min_lon, min_lat, max_lon, max_lat]

def validate_topological_relationship(geojson1: Dict[str, Any], geojson2: Dict[str, Any], relationship: str) -> bool:
    """Validate if two GeoJSON objects have the specified topological relationship"""
    # Implementation would check relationships like 'contains', 'intersects', etc.
    # This would typically use a spatial library like Shapely
    # This is a simplified placeholder
    return True