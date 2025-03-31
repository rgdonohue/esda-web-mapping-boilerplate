import io
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse, Response, StreamingResponse

from app.models.ogc_models import (
    OGCException,
    OGCServiceType,
    OGCVersion,
    WFSGetFeatureRequest,
    WMSGetMapRequest,
)
from app.services.ogc_services import (
    SUPPORTED_CRS,
    SUPPORTED_WFS_FORMATS,
    SUPPORTED_WMS_FORMATS,
    OGCServiceException,
    WFSService,
    WMSService,
)
from app.utils.cache import cached
from app.utils.enhanced_logging import get_logger
from app.utils.ogc_xml_formatter import (
    format_ogc_exception_xml,
    format_wfs_capabilities_xml,
    format_wms_capabilities_xml,
)

router = APIRouter()
logger = get_logger(__name__)

# WMS Endpoints


@router.get("/wms")
async def wms_get_capabilities(
    request: Request,
    service: str = Query("WMS", description="Service type"),
    version: str = Query("1.3.0", description="Service version"),
    request_type: str = Query("GetCapabilities", alias="request", description="Request type"),
    accept: Optional[str] = Header(None, description="Accept header for content negotiation"),
):
    """WMS GetCapabilities endpoint.

    This endpoint returns metadata about the WMS service, including available layers,
    supported formats, and coordinate reference systems.
    """
    logger.info(f"WMS GetCapabilities request received")

    try:
        if service != OGCServiceType.WMS:
            raise OGCServiceException(
                code="InvalidParameterValue", text=f"Invalid service: {service}", locator="service"
            )

        if request_type != "GetCapabilities":
            raise OGCServiceException(
                code="InvalidParameterValue",
                text=f"Invalid request: {request_type}",
                locator="request",
            )

        capabilities = await WMSService.get_capabilities()

        # Check if XML is requested (default for OGC services)
        wants_xml = True
        if accept:
            if "application/json" in accept and "application/xml" not in accept:
                wants_xml = False

        if wants_xml:
            xml_content = format_wms_capabilities_xml(capabilities)
            return Response(content=xml_content, media_type="application/xml")
        else:
            return JSONResponse(content=capabilities.dict())

    except OGCServiceException as e:
        logger.error(f"WMS GetCapabilities error: {str(e)}")

        if accept and "application/json" in accept:
            return JSONResponse(
                status_code=400,
                content=OGCException(
                    exception_code=e.exception_code,
                    exception_text=e.exception_text,
                    locator=e.locator,
                ).dict(),
            )
        else:
            xml_error = format_ogc_exception_xml(
                exception_code=e.exception_code, exception_text=e.exception_text, locator=e.locator
            )
            return Response(content=xml_error, status_code=400, media_type="application/xml")
    except Exception as e:
        logger.error(f"Unexpected error in WMS GetCapabilities: {str(e)}")

        if accept and "application/json" in accept:
            return JSONResponse(
                status_code=500,
                content=OGCException(
                    exception_code="NoApplicableCode",
                    exception_text=f"Unexpected error: {str(e)}",
                    locator="GetCapabilities",
                ).dict(),
            )
        else:
            xml_error = format_ogc_exception_xml(
                exception_code="NoApplicableCode",
                exception_text=f"Unexpected error: {str(e)}",
                locator="GetCapabilities",
            )
            return Response(content=xml_error, status_code=500, media_type="application/xml")


@router.get("/wms/map")
async def wms_get_map(
    request: Request,
    service: str = Query("WMS", description="Service type"),
    version: str = Query("1.3.0", description="Service version"),
    request_type: str = Query("GetMap", alias="request", description="Request type"),
    layers: str = Query(..., description="Comma-separated list of layer names"),
    styles: str = Query("", description="Comma-separated list of style names"),
    crs: str = Query(..., description="Coordinate Reference System"),
    bbox: str = Query(..., description="Bounding box in format: minx,miny,maxx,maxy"),
    width: int = Query(..., description="Width of the map in pixels"),
    height: int = Query(..., description="Height of the map in pixels"),
    format: str = Query("image/png", description="Output format"),
    transparent: bool = Query(False, description="Transparency of the map"),
):
    """WMS GetMap endpoint.

    This endpoint generates a map image based on the specified parameters.
    """
    logger.info(f"WMS GetMap request received for layers: {layers}")

    try:
        if service != OGCServiceType.WMS:
            raise OGCServiceException(
                code="InvalidParameterValue", text=f"Invalid service: {service}", locator="service"
            )

        if request_type != "GetMap":
            raise OGCServiceException(
                code="InvalidParameterValue",
                text=f"Invalid request: {request_type}",
                locator="request",
            )

        # Create request model
        get_map_request = WMSGetMapRequest(
            service=service,
            version=version,
            layers=layers,
            styles=styles,
            crs=crs,
            bbox=bbox,
            width=width,
            height=height,
            format=format,
            transparent=transparent,
        )

        # Process request
        image_data = await WMSService.get_map(get_map_request)

        # Return image response
        # In a real implementation, this would return an actual image
        # For now, we'll just return a placeholder message
        content_type = format
        return StreamingResponse(io.BytesIO(image_data), media_type=content_type)

    except OGCServiceException as e:
        logger.error(f"WMS GetMap error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content=OGCException(
                exception_code=e.exception_code, exception_text=e.exception_text, locator=e.locator
            ).dict(),
        )
    except Exception as e:
        logger.error(f"Unexpected error in WMS GetMap: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=OGCException(
                exception_code="NoApplicableCode",
                exception_text=f"Unexpected error: {str(e)}",
                locator="GetMap",
            ).dict(),
        )


# WFS Endpoints


@router.get("/wfs")
async def wfs_get_capabilities(
    request: Request,
    service: str = Query("WFS", description="Service type"),
    version: str = Query("2.0.0", description="Service version"),
    request_type: str = Query("GetCapabilities", alias="request", description="Request type"),
    accept: Optional[str] = Header(None, description="Accept header for content negotiation"),
):
    """WFS GetCapabilities endpoint.

    This endpoint returns metadata about the WFS service, including available feature types,
    supported formats, and coordinate reference systems.
    """
    logger.info(f"WFS GetCapabilities request received")

    try:
        if service != OGCServiceType.WFS:
            raise OGCServiceException(
                code="InvalidParameterValue", text=f"Invalid service: {service}", locator="service"
            )

        if request_type != "GetCapabilities":
            raise OGCServiceException(
                code="InvalidParameterValue",
                text=f"Invalid request: {request_type}",
                locator="request",
            )

        capabilities = await WFSService.get_capabilities()

        # Check if XML is requested (default for OGC services)
        wants_xml = True
        if accept:
            if "application/json" in accept and "application/xml" not in accept:
                wants_xml = False

        if wants_xml:
            xml_content = format_wfs_capabilities_xml(capabilities)
            return Response(content=xml_content, media_type="application/xml")
        else:
            return JSONResponse(content=capabilities.dict())

    except OGCServiceException as e:
        logger.error(f"WFS GetCapabilities error: {str(e)}")

        if accept and "application/json" in accept:
            return JSONResponse(
                status_code=400,
                content=OGCException(
                    exception_code=e.exception_code,
                    exception_text=e.exception_text,
                    locator=e.locator,
                ).dict(),
            )
        else:
            xml_error = format_ogc_exception_xml(
                exception_code=e.exception_code, exception_text=e.exception_text, locator=e.locator
            )
            return Response(content=xml_error, status_code=400, media_type="application/xml")
    except Exception as e:
        logger.error(f"Unexpected error in WFS GetCapabilities: {str(e)}")

        if accept and "application/json" in accept:
            return JSONResponse(
                status_code=500,
                content=OGCException(
                    exception_code="NoApplicableCode",
                    exception_text=f"Unexpected error: {str(e)}",
                    locator="GetCapabilities",
                ).dict(),
            )
        else:
            xml_error = format_ogc_exception_xml(
                exception_code="NoApplicableCode",
                exception_text=f"Unexpected error: {str(e)}",
                locator="GetCapabilities",
            )
            return Response(content=xml_error, status_code=500, media_type="application/xml")


@router.get("/wfs/feature")
async def wfs_get_feature(
    request: Request,
    service: str = Query("WFS", description="Service type"),
    version: str = Query("2.0.0", description="Service version"),
    request_type: str = Query("GetFeature", alias="request", description="Request type"),
    type_names: str = Query(..., description="Comma-separated list of feature type names"),
    count: Optional[int] = Query(None, description="Maximum number of features to return"),
    bbox: Optional[str] = Query(None, description="Bounding box in format: minx,miny,maxx,maxy"),
    crs: Optional[str] = Query(None, description="Coordinate Reference System"),
    output_format: str = Query("application/json", description="Output format"),
):
    """WFS GetFeature endpoint.

    This endpoint returns features based on the specified parameters.
    """
    logger.info(f"WFS GetFeature request received for types: {type_names}")

    try:
        if service != OGCServiceType.WFS:
            raise OGCServiceException(
                code="InvalidParameterValue", text=f"Invalid service: {service}", locator="service"
            )

        if request_type != "GetFeature":
            raise OGCServiceException(
                code="InvalidParameterValue",
                text=f"Invalid request: {request_type}",
                locator="request",
            )

        # Create request model
        get_feature_request = WFSGetFeatureRequest(
            service=service,
            version=version,
            type_names=type_names,
            count=count,
            bbox=bbox,
            crs=crs,
            output_format=output_format,
        )

        # Process request
        feature_collection = await WFSService.get_feature(get_feature_request)

        # Return features
        if output_format == "application/json":
            return feature_collection.dict()
        else:
            # In a real implementation, you would convert to other formats
            # For now, we'll just return JSON
            return feature_collection.dict()

    except OGCServiceException as e:
        logger.error(f"WFS GetFeature error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content=OGCException(
                exception_code=e.exception_code, exception_text=e.exception_text, locator=e.locator
            ).dict(),
        )
    except Exception as e:
        logger.error(f"Unexpected error in WFS GetFeature: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=OGCException(
                exception_code="NoApplicableCode",
                exception_text=f"Unexpected error: {str(e)}",
                locator="GetFeature",
            ).dict(),
        )
