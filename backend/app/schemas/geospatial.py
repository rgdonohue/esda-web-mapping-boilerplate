from typing import List, Dict, Any, Literal, Union, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

# GeoJSON Types
class GeoJSONType(str, Enum):
    Point = "Point"
    MultiPoint = "MultiPoint"
    LineString = "LineString"
    MultiLineString = "MultiLineString"
    Polygon = "Polygon"
    MultiPolygon = "MultiPolygon"
    GeometryCollection = "GeometryCollection"
    Feature = "Feature"
    FeatureCollection = "FeatureCollection"

# Base Geometry Models
class PointGeometry(BaseModel):
    type: Literal[GeoJSONType.Point]
    coordinates: List[float] = Field(..., min_items=2, max_items=3)
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        if len(v) < 2 or len(v) > 3:
            raise ValueError('Point coordinates must have 2 or 3 elements [lon, lat, (optional)elevation]')
        lon, lat = v[0], v[1]
        if lon < -180 or lon > 180:
            raise ValueError('Longitude must be between -180 and 180')
        if lat < -90 or lat > 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v

class LineStringGeometry(BaseModel):
    type: Literal[GeoJSONType.LineString]
    coordinates: List[List[float]] = Field(..., min_items=2)
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        if len(v) < 2:
            raise ValueError('LineString must have at least 2 positions')
        for point in v:
            if len(point) < 2 or len(point) > 3:
                raise ValueError('Each position must have 2 or 3 elements [lon, lat, (optional)elevation]')
        return v

class PolygonGeometry(BaseModel):
    type: Literal[GeoJSONType.Polygon]
    coordinates: List[List[List[float]]] = Field(..., min_items=1)
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        for ring in v:
            if len(ring) < 4:
                raise ValueError('Each polygon ring must have at least 4 positions (first and last are the same)')
            if ring[0] != ring[-1]:
                raise ValueError('First and last positions in a polygon ring must be the same')
        return v

class MultiPointGeometry(BaseModel):
    type: Literal[GeoJSONType.MultiPoint]
    coordinates: List[List[float]]

class MultiLineStringGeometry(BaseModel):
    type: Literal[GeoJSONType.MultiLineString]
    coordinates: List[List[List[float]]]

class MultiPolygonGeometry(BaseModel):
    type: Literal[GeoJSONType.MultiPolygon]
    coordinates: List[List[List[List[float]]]]

# Union type for all geometry types
Geometry = Union[
    PointGeometry,
    LineStringGeometry,
    PolygonGeometry,
    MultiPointGeometry,
    MultiLineStringGeometry,
    MultiPolygonGeometry
]

# Feature Models
class GeoJSONFeature(BaseModel):
    type: Literal[GeoJSONType.Feature]
    geometry: Geometry
    properties: Dict[str, Any] = Field(default_factory=dict)
    id: Optional[Union[str, int]] = None

class GeoJSONFeatureCollection(BaseModel):
    type: Literal[GeoJSONType.FeatureCollection]
    features: List[GeoJSONFeature]
    bbox: Optional[List[float]] = None

# Schema for spatial query parameters
class SpatialQueryParams(BaseModel):
    bbox: Optional[str] = Field(
        None, 
        description="Bounding box in format: minLon,minLat,maxLon,maxLat"
    )
    distance: Optional[float] = Field(
        None,
        description="Distance in meters for proximity queries"
    )
    coordinates: Optional[str] = Field(
        None,
        description="Point coordinates in format: lon,lat"
    )
    
    @validator('bbox')
    def validate_bbox(cls, v):
        if v:
            try:
                coords = [float(x) for x in v.split(',')]
                if len(coords) != 4:
                    raise ValueError()
                min_lon, min_lat, max_lon, max_lat = coords
                if min_lon < -180 or max_lon > 180 or min_lat < -90 or max_lat > 90:
                    raise ValueError()
                if min_lon > max_lon or min_lat > max_lat:
                    raise ValueError()
            except:
                raise ValueError('Invalid bbox format. Use: minLon,minLat,maxLon,maxLat')
        return v
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        if v:
            try:
                coords = [float(x) for x in v.split(',')]
                if len(coords) != 2:
                    raise ValueError()
                lon, lat = coords
                if lon < -180 or lon > 180 or lat < -90 or lat > 90:
                    raise ValueError()
            except:
                raise ValueError('Invalid coordinates format. Use: lon,lat')
        return v