from pydantic import BaseModel
from typing import List, Dict, Any, Literal, Union

class GeoJSONGeometry(BaseModel):
    type: str
    coordinates: Union[List[float], List[List[float]], List[List[List[float]]]]

class GeoJSONFeature(BaseModel):
    type: Literal["Feature"]
    geometry: GeoJSONGeometry
    properties: Dict[str, Any]

class GeoJSONFeatureCollection(BaseModel):
    type: Literal["FeatureCollection"]
    features: List[GeoJSONFeature]