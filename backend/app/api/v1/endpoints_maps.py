from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any

from app.utils.cache import cached
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/basemap", response_model=Dict[str, Any])
@cached(namespace="maps")
async def get_basemap_config(request: Request):
    """Return basemap configuration for the frontend."""
    logger.info("Fetching basemap configuration")
    try:
        config = {
            "type": "mapbox",
            "style": "mapbox://styles/mapbox/light-v10",
            "center": [-73.935242, 40.730610],  # Default: New York City
            "zoom": 12
        }
        logger.debug(f"Basemap config retrieved: {config}")
        return config
    except Exception as e:
        logger.error(f"Error retrieving basemap config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))