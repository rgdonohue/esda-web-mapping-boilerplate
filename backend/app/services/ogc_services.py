import json
from typing import Any, Dict, List, Optional, Tuple, Union

import geopandas as gpd
import pyproj
from fastapi import HTTPException
from owslib.wfs import WebFeatureService
from owslib.wms import WebMapService
from shapely.geometry import mapping, shape

from app.models.geojson_models import GeoJSONFeature, GeoJSONFeatureCollection
from app.models.ogc_models import (
    OGCException,
    OGCServiceType,
    OGCVersion,
    WFSGetCapabilitiesResponse,
    WFSGetFeatureRequest,
    WMSGetCapabilitiesResponse,
    WMSGetMapRequest,
)
from app.utils.enhanced_logging import get_logger
from app.utils.geospatial import calculate_bbox, parse_bbox_string

logger = get_logger(__name__)

# Supported CRS list
SUPPORTED_CRS = [
    "EPSG:4326",  # WGS 84
    "EPSG:3857",  # Web Mercator
    "EPSG:3395",  # World Mercator
    "CRS:84",  # WGS 84 longitude-latitude
]

# Supported output formats
SUPPORTED_WMS_FORMATS = ["image/png", "image/jpeg", "image/gif", "image/tiff"]

SUPPORTED_WFS_FORMATS = ["application/json", "application/gml+xml", "text/xml", "csv"]


class OGCServiceException(Exception):
    """Exception raised for OGC service errors."""

    def __init__(self, code: str, text: str, locator: Optional[str] = None):
        self.exception_code = code
        self.exception_text = text
        self.locator = locator
        super().__init__(text)


class CoordinateTransformer:
    """Utility class for coordinate transformations between different CRS."""

    @staticmethod
    def transform_bbox(bbox: List[float], source_crs: str, target_crs: str) -> List[float]:
        """Transform a bounding box from source CRS to target CRS.

        Args:
            bbox: Bounding box as [minx, miny, maxx, maxy]
            source_crs: Source coordinate reference system
            target_crs: Target coordinate reference system

        Returns:
            Transformed bounding box as [minx, miny, maxx, maxy]
        """
        try:
            # Create transformer
            transformer = pyproj.Transformer.from_crs(source_crs, target_crs, always_xy=True)

            # Extract coordinates
            minx, miny, maxx, maxy = bbox

            # Transform lower-left corner
            ll_x, ll_y = transformer.transform(minx, miny)

            # Transform upper-right corner
            ur_x, ur_y = transformer.transform(maxx, maxy)

            return [ll_x, ll_y, ur_x, ur_y]
        except Exception as e:
            logger.error(f"Error transforming bbox: {str(e)}")
            raise OGCServiceException(
                code="InvalidCRS",
                text=f"Error transforming coordinates: {str(e)}",
                locator="transform_bbox",
            )

    @staticmethod
    def transform_geometry(
        geometry: Dict[str, Any], source_crs: str, target_crs: str
    ) -> Dict[str, Any]:
        """Transform a GeoJSON geometry from source CRS to target CRS.

        Args:
            geometry: GeoJSON geometry object
            source_crs: Source coordinate reference system
            target_crs: Target coordinate reference system

        Returns:
            Transformed GeoJSON geometry
        """
        try:
            # Convert to shapely geometry
            shp_geom = shape(geometry)

            # Create GeoDataFrame with the geometry
            gdf = gpd.GeoDataFrame(geometry=[shp_geom], crs=source_crs)

            # Reproject to target CRS
            gdf = gdf.to_crs(target_crs)

            # Convert back to GeoJSON
            transformed_geom = mapping(gdf.geometry.iloc[0])

            return transformed_geom
        except Exception as e:
            logger.error(f"Error transforming geometry: {str(e)}")
            raise OGCServiceException(
                code="InvalidGeometry",
                text=f"Error transforming geometry: {str(e)}",
                locator="transform_geometry",
            )


class WMSService:
    """Web Map Service implementation."""

    @staticmethod
    async def get_capabilities() -> WMSGetCapabilitiesResponse:
        """Generate WMS GetCapabilities response.

        Returns:
            WMS GetCapabilities response
        """
        try:
            # In a real implementation, this would be populated from a database or configuration
            layers = [
                {
                    "name": "basemap",
                    "title": "Base Map",
                    "abstract": "Base map layer",
                    "queryable": False,
                    "opaque": False,
                    "bbox": [-180, -90, 180, 90],
                    "crs": SUPPORTED_CRS,
                    "styles": ["default"],
                },
                {
                    "name": "data_layer",
                    "title": "Data Layer",
                    "abstract": "Sample data layer",
                    "queryable": True,
                    "opaque": False,
                    "bbox": [-180, -90, 180, 90],
                    "crs": SUPPORTED_CRS,
                    "styles": ["default", "highlight"],
                },
            ]

            return WMSGetCapabilitiesResponse(
                version=OGCVersion.WMS_1_3_0,
                layers=layers,
                formats=SUPPORTED_WMS_FORMATS,
                crs=SUPPORTED_CRS,
                service_metadata={
                    "title": "ESDA Web Mapping WMS Service",
                    "abstract": "WMS service for geospatial data visualization",
                    "keywords": ["WMS", "GIS", "Mapping"],
                    "contact_information": {
                        "person_primary": {"person_name": "Administrator", "organization": "ESDA"},
                        "contact_email": "admin@example.com",
                    },
                    "access_constraints": "None",
                },
            )
        except Exception as e:
            logger.error(f"Error generating WMS capabilities: {str(e)}")
            raise OGCServiceException(
                code="OperationNotSupported",
                text=f"Error generating capabilities: {str(e)}",
                locator="GetCapabilities",
            )

    @staticmethod
    async def get_map(request: WMSGetMapRequest) -> bytes:
        """Process WMS GetMap request and generate map image.

        Args:
            request: WMS GetMap request parameters

        Returns:
            Map image as bytes
        """
        try:
            # Parse and validate parameters
            if request.crs not in SUPPORTED_CRS:
                raise OGCServiceException(
                    code="InvalidCRS", text=f"Unsupported CRS: {request.crs}", locator="GetMap"
                )

            if request.format not in SUPPORTED_WMS_FORMATS:
                raise OGCServiceException(
                    code="InvalidFormat",
                    text=f"Unsupported format: {request.format}",
                    locator="GetMap",
                )

            # Parse bbox
            bbox = parse_bbox_string(request.bbox)

            # In a real implementation, this would generate an actual map image
            # For now, we'll just return a placeholder message
            logger.info(f"WMS GetMap request processed for layers: {request.layers}")

            # This is a placeholder - in a real implementation, you would:
            # 1. Fetch the requested layers from a data source
            # 2. Render them to an image using a library like Mapnik or Cairo
            # 3. Return the image bytes

            # For demonstration, we're just returning a message
            # In a real implementation, this would be an image
            return b"WMS GetMap response would be an image"

        except OGCServiceException as e:
            raise e
        except Exception as e:
            logger.error(f"Error processing WMS GetMap request: {str(e)}")
            raise OGCServiceException(
                code="OperationProcessingFailed",
                text=f"Error processing GetMap request: {str(e)}",
                locator="GetMap",
            )


class WFSService:
    """Web Feature Service implementation."""

    @staticmethod
    async def get_capabilities() -> WFSGetCapabilitiesResponse:
        """Generate WFS GetCapabilities response.

        Returns:
            WFS GetCapabilities response
        """
        try:
            # In a real implementation, this would be populated from a database or configuration
            feature_types = [
                {
                    "name": "points_of_interest",
                    "title": "Points of Interest",
                    "abstract": "Sample points of interest",
                    "keywords": ["POI", "points", "locations"],
                    "bbox": [-180, -90, 180, 90],
                    "crs": SUPPORTED_CRS,
                    "properties": [
                        {"name": "id", "type": "integer"},
                        {"name": "name", "type": "string"},
                        {"name": "category", "type": "string"},
                        {"name": "description", "type": "string"},
                    ],
                },
                {
                    "name": "boundaries",
                    "title": "Administrative Boundaries",
                    "abstract": "Sample administrative boundaries",
                    "keywords": ["boundaries", "administrative", "regions"],
                    "bbox": [-180, -90, 180, 90],
                    "crs": SUPPORTED_CRS,
                    "properties": [
                        {"name": "id", "type": "integer"},
                        {"name": "name", "type": "string"},
                        {"name": "level", "type": "integer"},
                        {"name": "population", "type": "integer"},
                    ],
                },
            ]

            return WFSGetCapabilitiesResponse(
                version=OGCVersion.WFS_2_0_0,
                feature_types=feature_types,
                formats=SUPPORTED_WFS_FORMATS,
                crs=SUPPORTED_CRS,
                service_metadata={
                    "title": "ESDA Web Mapping WFS Service",
                    "abstract": "WFS service for geospatial data access",
                    "keywords": ["WFS", "GIS", "Features"],
                    "contact_information": {
                        "person_primary": {"person_name": "Administrator", "organization": "ESDA"},
                        "contact_email": "admin@example.com",
                    },
                    "access_constraints": "None",
                },
            )
        except Exception as e:
            logger.error(f"Error generating WFS capabilities: {str(e)}")
            raise OGCServiceException(
                code="OperationNotSupported",
                text=f"Error generating capabilities: {str(e)}",
                locator="GetCapabilities",
            )

    @staticmethod
    async def get_feature(request: WFSGetFeatureRequest) -> GeoJSONFeatureCollection:
        """Process WFS GetFeature request and return features.

        Args:
            request: WFS GetFeature request parameters

        Returns:
            GeoJSON FeatureCollection containing the requested features
        """
        try:
            # Parse and validate parameters
            if request.crs and request.crs not in SUPPORTED_CRS:
                raise OGCServiceException(
                    code="InvalidCRS", text=f"Unsupported CRS: {request.crs}", locator="GetFeature"
                )

            if request.output_format not in SUPPORTED_WFS_FORMATS:
                raise OGCServiceException(
                    code="InvalidFormat",
                    text=f"Unsupported format: {request.output_format}",
                    locator="GetFeature",
                )

            # Parse bbox if provided
            bbox = None
            if request.bbox:
                bbox = parse_bbox_string(request.bbox)

            # In a real implementation, this would fetch features from a database
            # For now, we'll just return sample features
            logger.info(f"WFS GetFeature request processed for types: {request.type_names}")

            # Sample features - in a real implementation, these would come from a database
            features = []

            if "points_of_interest" in request.type_names:
                features.extend(
                    [
                        GeoJSONFeature(
                            type="Feature",
                            geometry={"type": "Point", "coordinates": [-73.985428, 40.748817]},
                            properties={
                                "id": 1,
                                "name": "Empire State Building",
                                "category": "landmark",
                                "description": "Famous skyscraper in New York City",
                            },
                        ),
                        GeoJSONFeature(
                            type="Feature",
                            geometry={"type": "Point", "coordinates": [-74.013961, 40.704543]},
                            properties={
                                "id": 2,
                                "name": "Statue of Liberty",
                                "category": "landmark",
                                "description": "Famous statue in New York Harbor",
                            },
                        ),
                    ]
                )

            if "boundaries" in request.type_names:
                features.extend(
                    [
                        GeoJSONFeature(
                            type="Feature",
                            geometry={
                                "type": "Polygon",
                                "coordinates": [
                                    [
                                        [-74.0259, 40.7127],
                                        [-73.9397, 40.7127],
                                        [-73.9397, 40.7903],
                                        [-74.0259, 40.7903],
                                        [-74.0259, 40.7127],
                                    ]
                                ],
                            },
                            properties={
                                "id": 1,
                                "name": "Manhattan",
                                "level": 2,
                                "population": 1628706,
                            },
                        )
                    ]
                )

            # Apply bbox filter if provided
            if bbox:
                filtered_features = []
                for feature in features:
                    # This is a simplified check - in a real implementation,
                    # you would use a proper spatial library to check intersection
                    geom = feature.geometry
                    if geom["type"] == "Point":
                        lon, lat = geom["coordinates"]
                        if bbox[0] <= lon <= bbox[2] and bbox[1] <= lat <= bbox[3]:
                            filtered_features.append(feature)
                    else:
                        # For non-point geometries, we'd need more complex intersection checks
                        # For simplicity, we'll include them all in this example
                        filtered_features.append(feature)
                features = filtered_features

            # Apply count limit if provided
            if request.count and len(features) > request.count:
                features = features[: request.count]

            return GeoJSONFeatureCollection(type="FeatureCollection", features=features)

        except OGCServiceException as e:
            raise e
        except Exception as e:
            logger.error(f"Error processing WFS GetFeature request: {str(e)}")
            raise OGCServiceException(
                code="OperationProcessingFailed",
                text=f"Error processing GetFeature request: {str(e)}",
                locator="GetFeature",
            )
