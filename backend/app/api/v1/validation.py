import json
from typing import Any, Dict, List

from fastapi import Depends, HTTPException, status
from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.base import BaseAPIRouter
from app.core.exceptions import ValidationError
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.spatial import SpatialDataDB
from app.models.user import User

router = BaseAPIRouter(prefix="/validation", tags=["validation"])


@router.get("/geometry/{spatial_data_id}")
async def validate_geometry(
    spatial_data_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Validate geometry of spatial data."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")

    # Check geometry validity
    validity_query = text(
        """
        SELECT 
            ST_IsValid(geometry) as is_valid,
            ST_IsValidReason(geometry) as validity_reason,
            ST_IsSimple(geometry) as is_simple,
            ST_IsRing(geometry) as is_ring,
            ST_IsClosed(geometry) as is_closed
        FROM spatial_data
        WHERE id = :spatial_data_id
    """
    )

    result = await db.execute(validity_query, {"spatial_data_id": spatial_data_id})
    validity = result.first()

    # Get geometry type and dimension
    type_query = text(
        """
        SELECT 
            GeometryType(geometry) as geom_type,
            ST_Dimension(geometry) as dimension,
            ST_CoordDim(geometry) as coord_dim
        FROM spatial_data
        WHERE id = :spatial_data_id
    """
    )

    result = await db.execute(type_query, {"spatial_data_id": spatial_data_id})
    geom_type = result.first()

    return {
        "validity": {
            "is_valid": validity.is_valid,
            "validity_reason": validity.validity_reason,
            "is_simple": validity.is_simple,
            "is_ring": validity.is_ring,
            "is_closed": validity.is_closed,
        },
        "geometry_type": {
            "type": geom_type.geom_type,
            "dimension": geom_type.dimension,
            "coordinate_dimension": geom_type.coord_dim,
        },
    }


@router.get("/topology/{spatial_data_id}")
async def check_topology(
    spatial_data_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Check topology of spatial data."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")

    # Check for self-intersections
    self_intersect_query = text(
        """
        SELECT 
            ST_IsSimple(geometry) as is_simple,
            ST_IsValid(geometry) as is_valid
        FROM spatial_data
        WHERE id = :spatial_data_id
    """
    )

    result = await db.execute(self_intersect_query, {"spatial_data_id": spatial_data_id})
    topology = result.first()

    # Check for gaps and overlaps in polygons
    if spatial_data.geometry_type in ["Polygon", "MultiPolygon"]:
        gaps_query = text(
            """
            WITH polygons AS (
                SELECT geometry
                FROM spatial_data
                WHERE id = :spatial_data_id
            )
            SELECT 
                ST_Area(ST_Difference(
                    ST_Envelope(geometry),
                    ST_Union(geometry)
                )) as gap_area
            FROM polygons
        """
        )

        result = await db.execute(gaps_query, {"spatial_data_id": spatial_data_id})
        gaps = result.first()

        overlaps_query = text(
            """
            WITH polygons AS (
                SELECT geometry
                FROM spatial_data
                WHERE id = :spatial_data_id
            )
            SELECT 
                ST_Area(ST_Union(geometry)) - ST_Area(ST_Collect(geometry)) as overlap_area
            FROM polygons
        """
        )

        result = await db.execute(overlaps_query, {"spatial_data_id": spatial_data_id})
        overlaps = result.first()

        return {
            "topology": {
                "is_simple": topology.is_simple,
                "is_valid": topology.is_valid,
                "has_gaps": gaps.gap_area > 0 if gaps.gap_area else False,
                "gap_area": float(gaps.gap_area) if gaps.gap_area else 0,
                "has_overlaps": overlaps.overlap_area > 0 if overlaps.overlap_area else False,
                "overlap_area": float(overlaps.overlap_area) if overlaps.overlap_area else 0,
            }
        }

    return {"topology": {"is_simple": topology.is_simple, "is_valid": topology.is_valid}}


@router.get("/coordinate-system/{spatial_data_id}")
async def check_coordinate_system(
    spatial_data_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Check coordinate system of spatial data."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")

    # Get coordinate system information
    crs_query = text(
        """
        SELECT 
            ST_SRID(geometry) as srid,
            ST_IsEmpty(geometry) as is_empty,
            ST_Is3D(geometry) as is_3d,
            ST_IsMeasured(geometry) as is_measured
        FROM spatial_data
        WHERE id = :spatial_data_id
    """
    )

    result = await db.execute(crs_query, {"spatial_data_id": spatial_data_id})
    crs_info = result.first()

    # Get spatial extent
    extent_query = text(
        """
        SELECT 
            ST_XMin(ST_Extent(geometry)) as x_min,
            ST_YMin(ST_Extent(geometry)) as y_min,
            ST_XMax(ST_Extent(geometry)) as x_max,
            ST_YMax(ST_Extent(geometry)) as y_max
        FROM spatial_data
        WHERE id = :spatial_data_id
        GROUP BY id
    """
    )

    result = await db.execute(extent_query, {"spatial_data_id": spatial_data_id})
    extent = result.first()

    return {
        "coordinate_system": {
            "srid": crs_info.srid,
            "is_empty": crs_info.is_empty,
            "is_3d": crs_info.is_3d,
            "is_measured": crs_info.is_measured,
        },
        "spatial_extent": {
            "x_min": float(extent.x_min) if extent.x_min else None,
            "y_min": float(extent.y_min) if extent.y_min else None,
            "x_max": float(extent.x_max) if extent.x_max else None,
            "y_max": float(extent.y_max) if extent.y_max else None,
        },
    }


@router.get("/data-quality/{spatial_data_id}")
async def check_data_quality(
    spatial_data_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Check data quality of spatial data."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")

    # Get basic statistics
    stats_query = text(
        """
        SELECT 
            COUNT(*) as feature_count,
            COUNT(DISTINCT geometry) as unique_geometries,
            COUNT(*) - COUNT(geometry) as null_geometries,
            COUNT(*) - COUNT(name) as null_names,
            COUNT(*) - COUNT(description) as null_descriptions
        FROM spatial_data
        WHERE id = :spatial_data_id
    """
    )

    result = await db.execute(stats_query, {"spatial_data_id": spatial_data_id})
    stats = result.first()

    # Check for duplicate geometries
    duplicate_query = text(
        """
        WITH duplicates AS (
            SELECT geometry, COUNT(*) as count
            FROM spatial_data
            WHERE id = :spatial_data_id
            GROUP BY geometry
            HAVING COUNT(*) > 1
        )
        SELECT COUNT(*) as duplicate_count
        FROM duplicates
    """
    )

    result = await db.execute(duplicate_query, {"spatial_data_id": spatial_data_id})
    duplicates = result.first()

    # Check metadata completeness
    metadata = spatial_data.metadata or {}
    required_fields = ["created_date", "source", "accuracy"]
    missing_fields = [field for field in required_fields if field not in metadata]

    return {
        "completeness": {
            "feature_count": stats.feature_count,
            "unique_geometries": stats.unique_geometries,
            "null_geometries": stats.null_geometries,
            "null_names": stats.null_names,
            "null_descriptions": stats.null_descriptions,
            "duplicate_geometries": duplicates.duplicate_count,
        },
        "metadata": {
            "missing_fields": missing_fields,
            "completeness_score": (len(required_fields) - len(missing_fields))
            / len(required_fields),
        },
    }


@router.post("/fix/{spatial_data_id}")
async def fix_geometry(
    spatial_data_id: int,
    fix_type: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Fix common geometry issues."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")

    if fix_type == "self_intersection":
        # Fix self-intersections
        fix_query = text(
            """
            UPDATE spatial_data
            SET geometry = ST_MakeValid(geometry)
            WHERE id = :spatial_data_id
        """
        )
    elif fix_type == "orientation":
        # Fix polygon orientation
        fix_query = text(
            """
            UPDATE spatial_data
            SET geometry = ST_Force2D(ST_ForcePolygonCW(geometry))
            WHERE id = :spatial_data_id
        """
        )
    elif fix_type == "snap":
        # Snap vertices to grid
        fix_query = text(
            """
            UPDATE spatial_data
            SET geometry = ST_SnapToGrid(geometry, 0.0001)
            WHERE id = :spatial_data_id
        """
        )
    else:
        raise ValidationError(f"Unsupported fix type: {fix_type}")

    await db.execute(fix_query, {"spatial_data_id": spatial_data_id})
    await db.commit()

    return {"message": f"Applied {fix_type} fix successfully"}
