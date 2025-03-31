from typing import Any, Dict, List, Literal, Union

from pydantic import BaseModel


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
