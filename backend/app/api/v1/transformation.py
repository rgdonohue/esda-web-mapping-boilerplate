from typing import Any, List, Dict
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

router = BaseAPIRouter(prefix="/transformation", tags=["transformation"])

@router.post("/project/{spatial_data_id}")
async def project_data(
    spatial_data_id: int,
    target_srid: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Project spatial data to a different coordinate system."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")
    
    # Get current SRID
    current_srid_query = text("""
        SELECT ST_SRID(geometry) as srid
        FROM spatial_data
        WHERE id = :spatial_data_id
    """)
    
    result = await db.execute(current_srid_query, {"spatial_data_id": spatial_data_id})
    current_srid = result.first().srid
    
    if current_srid == target_srid:
        return {"message": "Data already in target coordinate system"}
    
    # Project geometry
    project_query = text("""
        UPDATE spatial_data
        SET 
            geometry = ST_Transform(geometry, :target_srid),
            srid = :target_srid
        WHERE id = :spatial_data_id
    """)
    
    await db.execute(project_query, {
        "spatial_data_id": spatial_data_id,
        "target_srid": target_srid
    })
    await db.commit()
    
    return {
        "message": "Data projected successfully",
        "from_srid": current_srid,
        "to_srid": target_srid
    }

@router.post("/simplify/{spatial_data_id}")
async def simplify_geometry(
    spatial_data_id: int,
    tolerance: float,
    preserve_topology: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Simplify geometry while preserving topology."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")
    
    # Get original geometry stats
    original_stats_query = text("""
        SELECT 
            ST_NumPoints(geometry) as num_points,
            ST_Area(geometry) as area
        FROM spatial_data
        WHERE id = :spatial_data_id
    """)
    
    result = await db.execute(original_stats_query, {"spatial_data_id": spatial_data_id})
    original_stats = result.first()
    
    # Simplify geometry
    simplify_query = text("""
        UPDATE spatial_data
        SET geometry = ST_SimplifyPreserveTopology(geometry, :tolerance)
        WHERE id = :spatial_data_id
    """)
    
    await db.execute(simplify_query, {
        "spatial_data_id": spatial_data_id,
        "tolerance": tolerance
    })
    await db.commit()
    
    # Get simplified geometry stats
    result = await db.execute(original_stats_query, {"spatial_data_id": spatial_data_id})
    simplified_stats = result.first()
    
    return {
        "message": "Geometry simplified successfully",
        "original": {
            "num_points": original_stats.num_points,
            "area": float(original_stats.area) if original_stats.area else None
        },
        "simplified": {
            "num_points": simplified_stats.num_points,
            "area": float(simplified_stats.area) if simplified_stats.area else None
        },
        "reduction": {
            "points": (original_stats.num_points - simplified_stats.num_points) / original_stats.num_points,
            "area": abs(float(original_stats.area) - float(simplified_stats.area)) / float(original_stats.area) if original_stats.area and simplified_stats.area else None
        }
    }

@router.post("/buffer/{spatial_data_id}")
async def create_buffer(
    spatial_data_id: int,
    distance: float,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create buffer around geometry."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")
    
    # Create buffered geometry
    buffer_query = text("""
        UPDATE spatial_data
        SET geometry = ST_Buffer(geometry, :distance)
        WHERE id = :spatial_data_id
    """)
    
    await db.execute(buffer_query, {
        "spatial_data_id": spatial_data_id,
        "distance": distance
    })
    await db.commit()
    
    return {
        "message": "Buffer created successfully",
        "distance": distance
    }

@router.post("/smooth/{spatial_data_id}")
async def smooth_geometry(
    spatial_data_id: int,
    iterations: int = 1,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Smooth geometry using Chaikin's algorithm."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")
    
    # Get original geometry stats
    original_stats_query = text("""
        SELECT 
            ST_NumPoints(geometry) as num_points,
            ST_Area(geometry) as area
        FROM spatial_data
        WHERE id = :spatial_data_id
    """)
    
    result = await db.execute(original_stats_query, {"spatial_data_id": spatial_data_id})
    original_stats = result.first()
    
    # Apply Chaikin's algorithm
    for _ in range(iterations):
        smooth_query = text("""
            WITH RECURSIVE chaikin AS (
                SELECT 
                    id,
                    ST_Chaikin(geometry) as geometry
                FROM spatial_data
                WHERE id = :spatial_data_id
            )
            UPDATE spatial_data
            SET geometry = chaikin.geometry
            FROM chaikin
            WHERE spatial_data.id = chaikin.id
        """)
        
        await db.execute(smooth_query, {"spatial_data_id": spatial_data_id})
    
    await db.commit()
    
    # Get smoothed geometry stats
    result = await db.execute(original_stats_query, {"spatial_data_id": spatial_data_id})
    smoothed_stats = result.first()
    
    return {
        "message": "Geometry smoothed successfully",
        "iterations": iterations,
        "original": {
            "num_points": original_stats.num_points,
            "area": float(original_stats.area) if original_stats.area else None
        },
        "smoothed": {
            "num_points": smoothed_stats.num_points,
            "area": float(smoothed_stats.area) if smoothed_stats.area else None
        }
    }

@router.post("/generalize/{spatial_data_id}")
async def generalize_geometry(
    spatial_data_id: int,
    method: str,
    tolerance: float,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Generalize geometry using various methods."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")
    
    # Get original geometry stats
    original_stats_query = text("""
        SELECT 
            ST_NumPoints(geometry) as num_points,
            ST_Area(geometry) as area
        FROM spatial_data
        WHERE id = :spatial_data_id
    """)
    
    result = await db.execute(original_stats_query, {"spatial_data_id": spatial_data_id})
    original_stats = result.first()
    
    # Apply generalization based on method
    if method == "douglas_peucker":
        generalize_query = text("""
            UPDATE spatial_data
            SET geometry = ST_Simplify(geometry, :tolerance)
            WHERE id = :spatial_data_id
        """)
    elif method == "visvalingam":
        generalize_query = text("""
            UPDATE spatial_data
            SET geometry = ST_SimplifyVW(geometry, :tolerance)
            WHERE id = :spatial_data_id
        """)
    else:
        raise ValidationError(f"Unsupported generalization method: {method}")
    
    await db.execute(generalize_query, {
        "spatial_data_id": spatial_data_id,
        "tolerance": tolerance
    })
    await db.commit()
    
    # Get generalized geometry stats
    result = await db.execute(original_stats_query, {"spatial_data_id": spatial_data_id})
    generalized_stats = result.first()
    
    return {
        "message": "Geometry generalized successfully",
        "method": method,
        "tolerance": tolerance,
        "original": {
            "num_points": original_stats.num_points,
            "area": float(original_stats.area) if original_stats.area else None
        },
        "generalized": {
            "num_points": generalized_stats.num_points,
            "area": float(generalized_stats.area) if generalized_stats.area else None
        },
        "reduction": {
            "points": (original_stats.num_points - generalized_stats.num_points) / original_stats.num_points,
            "area": abs(float(original_stats.area) - float(generalized_stats.area)) / float(original_stats.area) if original_stats.area and generalized_stats.area else None
        }
    } 