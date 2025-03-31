from typing import Any, List, Dict, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.api.v1.base import BaseAPIRouter
from app.models.spatial import SpatialDataDB
from app.core.exceptions import ValidationError
import json

router = BaseAPIRouter(prefix="/visualization", tags=["visualization"])

@router.post("/style/{spatial_data_id}")
async def update_style(
    spatial_data_id: int,
    style: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update visualization style for spatial data."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")
    
    # Validate style properties
    valid_properties = {
        "fillColor", "fillOpacity", "color", "weight", "opacity",
        "dashArray", "lineCap", "lineJoin", "radius", "fill"
    }
    
    for prop in style:
        if prop not in valid_properties:
            raise ValidationError(f"Invalid style property: {prop}")
    
    # Update metadata with style
    metadata = spatial_data.metadata or {}
    metadata["style"] = style
    spatial_data.metadata = metadata
    
    await db.commit()
    return {"message": "Style updated successfully", "style": style}

@router.get("/style/{spatial_data_id}")
async def get_style(
    spatial_data_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get visualization style for spatial data."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")
    
    return spatial_data.metadata.get("style", {})

@router.post("/choropleth")
async def create_choropleth(
    spatial_data_id: int,
    field: str,
    method: str = "quantile",
    n_classes: int = 5,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create choropleth style based on field values."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")
    
    # Get field values from metadata
    metadata = spatial_data.metadata or {}
    if field not in metadata:
        raise ValidationError(f"Field {field} not found in metadata")
    
    values = metadata[field]
    if not isinstance(values, (list, tuple)):
        raise ValidationError(f"Field {field} must contain numeric values")
    
    # Calculate breaks based on method
    if method == "quantile":
        breaks = sorted(values)
        n = len(breaks)
        breaks = [breaks[i * n // n_classes] for i in range(n_classes + 1)]
    elif method == "equal_interval":
        min_val, max_val = min(values), max(values)
        interval = (max_val - min_val) / n_classes
        breaks = [min_val + i * interval for i in range(n_classes + 1)]
    else:
        raise ValidationError(f"Unsupported classification method: {method}")
    
    # Generate color scheme
    colors = ["#ffffcc", "#c7e9b4", "#7fcdbb", "#41b6c4", "#1d91c0"]
    
    # Create style rules
    style_rules = []
    for i in range(n_classes):
        style_rules.append({
            "min": breaks[i],
            "max": breaks[i + 1],
            "color": colors[i],
            "fillOpacity": 0.7
        })
    
    # Update style in metadata
    metadata["style"] = {
        "type": "choropleth",
        "field": field,
        "rules": style_rules
    }
    spatial_data.metadata = metadata
    
    await db.commit()
    return {
        "message": "Choropleth style created successfully",
        "style": metadata["style"]
    }

@router.post("/heatmap")
async def create_heatmap(
    spatial_data_ids: List[int],
    weight_field: Optional[str] = None,
    radius: int = 25,
    blur: int = 15,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create heatmap visualization from point data."""
    query = db.query(SpatialDataDB).filter(SpatialDataDB.id.in_(spatial_data_ids))
    spatial_data = await query.all()
    
    if not spatial_data:
        raise ValidationError("No spatial data found")
    
    # Collect point coordinates and weights
    points = []
    for data in spatial_data:
        if data.geometry_type != "Point":
            continue
        
        point = json.loads(data.geometry.to_geojson())
        weight = 1.0
        if weight_field and data.metadata and weight_field in data.metadata:
            weight = float(data.metadata[weight_field])
        
        points.append({
            "coordinates": point["coordinates"],
            "weight": weight
        })
    
    if not points:
        raise ValidationError("No point features found in selected data")
    
    # Create heatmap configuration
    heatmap_config = {
        "type": "heatmap",
        "points": points,
        "options": {
            "radius": radius,
            "blur": blur
        }
    }
    
    return {
        "message": "Heatmap configuration created successfully",
        "configuration": heatmap_config
    }

@router.get("/clustering/{spatial_data_id}")
async def get_clustering_options(
    spatial_data_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get clustering visualization options for spatial data."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")
    
    # Get feature count
    count_query = text("""
        SELECT COUNT(*) as count
        FROM spatial_data
        WHERE id = :spatial_data_id
    """)
    result = await db.execute(count_query, {"spatial_data_id": spatial_data_id})
    feature_count = result.scalar()
    
    # Generate clustering options based on feature count
    options = {
        "feature_count": feature_count,
        "recommended_options": {
            "min_zoom": 0,
            "max_zoom": 18,
            "radius": min(80, max(20, feature_count // 100)),
            "extent": 512,
            "min_points": 2
        }
    }
    
    return options

@router.post("/animation")
async def create_animation(
    spatial_data_id: int,
    time_field: str,
    interval: int = 1000,  # milliseconds
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create time-based animation configuration."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")
    
    # Get time values from metadata
    metadata = spatial_data.metadata or {}
    if time_field not in metadata:
        raise ValidationError(f"Time field {time_field} not found in metadata")
    
    time_values = metadata[time_field]
    if not isinstance(time_values, (list, tuple)):
        raise ValidationError(f"Time field {time_field} must contain time values")
    
    # Create animation configuration
    animation_config = {
        "type": "time",
        "field": time_field,
        "interval": interval,
        "frames": sorted(set(time_values))
    }
    
    # Update metadata with animation configuration
    metadata["animation"] = animation_config
    spatial_data.metadata = metadata
    
    await db.commit()
    return {
        "message": "Animation configuration created successfully",
        "configuration": animation_config
    } 