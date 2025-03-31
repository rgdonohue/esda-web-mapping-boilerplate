from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Union, Optional
from enum import Enum

from app.models.geojson_models import GeoJSONFeature, GeoJSONFeatureCollection


class OGCServiceType(str, Enum):
    """OGC Service Types"""
    WMS = "WMS"
    WFS = "WFS"
    WCS = "WCS"


class OGCVersion(str, Enum):
    """Supported OGC Service Versions"""
    WMS_1_3_0 = "1.3.0"
    WFS_2_0_0 = "2.0.0"


class WMSGetCapabilitiesResponse(BaseModel):
    """Model for WMS GetCapabilities response"""
    service: Literal["WMS"] = "WMS"
    version: str
    layers: List[Dict[str, Any]]
    formats: List[str]
    crs: List[str]
    service_metadata: Dict[str, Any]


class WMSGetMapRequest(BaseModel):
    """Model for WMS GetMap request parameters"""
    service: Literal["WMS"] = "WMS"
    version: str = Field("1.3.0", description="WMS version")
    layers: str = Field(..., description="Comma-separated list of layer names")
    styles: str = Field("", description="Comma-separated list of style names")
    crs: str = Field(..., description="Coordinate Reference System")
    bbox: str = Field(..., description="Bounding box in format: minx,miny,maxx,maxy")
    width: int = Field(..., description="Width of the map in pixels")
    height: int = Field(..., description="Height of the map in pixels")
    format: str = Field("image/png", description="Output format")
    transparent: bool = Field(False, description="Transparency of the map")


class WFSGetCapabilitiesResponse(BaseModel):
    """Model for WFS GetCapabilities response"""
    service: Literal["WFS"] = "WFS"
    version: str
    feature_types: List[Dict[str, Any]]
    formats: List[str]
    crs: List[str]
    service_metadata: Dict[str, Any]


class WFSGetFeatureRequest(BaseModel):
    """Model for WFS GetFeature request parameters"""
    service: Literal["WFS"] = "WFS"
    version: str = Field("2.0.0", description="WFS version")
    type_names: str = Field(..., description="Comma-separated list of feature type names")
    count: Optional[int] = Field(None, description="Maximum number of features to return")
    bbox: Optional[str] = Field(None, description="Bounding box in format: minx,miny,maxx,maxy")
    crs: Optional[str] = Field(None, description="Coordinate Reference System")
    output_format: str = Field("application/json", description="Output format")


class WFSTransactionRequest(BaseModel):
    """Model for WFS Transaction request"""
    service: Literal["WFS"] = "WFS"
    version: str = Field("2.0.0", description="WFS version")
    operation: str = Field(..., description="Transaction operation: Insert, Update, Delete")
    type_name: str = Field(..., description="Feature type name")
    features: Union[GeoJSONFeature, List[GeoJSONFeature]] = Field(..., description="Features to process")


class OGCException(BaseModel):
    """Model for OGC Exception response"""
    exception_code: str
    exception_text: str
    locator: Optional[str] = None