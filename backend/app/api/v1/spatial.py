from typing import Any, List

from fastapi import Depends, HTTPException, status
from geoalchemy2 import Geometry
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.base import BaseAPIRouter, PaginationParams
from app.core.exceptions import NotFoundError, ValidationError
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.spatial import SpatialData, SpatialDataCreate, SpatialDataUpdate
from app.models.user import User

router = BaseAPIRouter(prefix="/spatial", tags=["spatial"])


@router.post("/", response_model=SpatialData)
async def create_spatial_data(
    data_in: SpatialDataCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create new spatial data entry."""
    spatial_data = SpatialData(**data_in.dict(), created_by=current_user.id)
    db.add(spatial_data)
    await db.commit()
    await db.refresh(spatial_data)
    return spatial_data


@router.get("/", response_model=List[SpatialData])
async def get_spatial_data(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get paginated spatial data entries."""
    query = db.query(SpatialData)

    # Apply filters if provided
    if pagination.filters:
        for field, value in pagination.filters.items():
            if hasattr(SpatialData, field):
                query = query.filter(getattr(SpatialData, field) == value)

    # Apply sorting
    if pagination.sort_by:
        sort_column = getattr(SpatialData, pagination.sort_by, None)
        if sort_column:
            query = query.order_by(
                sort_column.desc() if pagination.sort_order == "desc" else sort_column.asc()
            )

    # Apply pagination
    total = await db.scalar(func.count(query.subquery().c.id))
    query = query.offset(pagination.offset).limit(pagination.size)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{spatial_data_id}", response_model=SpatialData)
async def get_spatial_data_by_id(
    spatial_data_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get spatial data by ID."""
    spatial_data = await db.query(SpatialData).filter(SpatialData.id == spatial_data_id).first()
    if not spatial_data:
        raise NotFoundError(f"Spatial data with ID {spatial_data_id} not found")
    return spatial_data


@router.put("/{spatial_data_id}", response_model=SpatialData)
async def update_spatial_data(
    spatial_data_id: int,
    data_in: SpatialDataUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update spatial data entry."""
    spatial_data = await db.query(SpatialData).filter(SpatialData.id == spatial_data_id).first()
    if not spatial_data:
        raise NotFoundError(f"Spatial data with ID {spatial_data_id} not found")

    # Update fields
    for field, value in data_in.dict(exclude_unset=True).items():
        setattr(spatial_data, field, value)

    await db.commit()
    await db.refresh(spatial_data)
    return spatial_data


@router.delete("/{spatial_data_id}")
async def delete_spatial_data(
    spatial_data_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Delete spatial data entry."""
    spatial_data = await db.query(SpatialData).filter(SpatialData.id == spatial_data_id).first()
    if not spatial_data:
        raise NotFoundError(f"Spatial data with ID {spatial_data_id} not found")

    await db.delete(spatial_data)
    await db.commit()
    return {"message": "Spatial data deleted successfully"}


@router.post("/{spatial_data_id}/analyze")
async def analyze_spatial_data(
    spatial_data_id: int,
    analysis_type: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Perform spatial analysis on the data."""
    spatial_data = await db.query(SpatialData).filter(SpatialData.id == spatial_data_id).first()
    if not spatial_data:
        raise NotFoundError(f"Spatial data with ID {spatial_data_id} not found")

    # Perform different types of spatial analysis based on analysis_type
    if analysis_type == "centroid":
        result = await db.scalar(func.ST_Centroid(spatial_data.geometry))
    elif analysis_type == "area":
        result = await db.scalar(func.ST_Area(spatial_data.geometry))
    elif analysis_type == "buffer":
        result = await db.scalar(func.ST_Buffer(spatial_data.geometry, 1000))  # 1000 meters buffer
    else:
        raise ValidationError(f"Unsupported analysis type: {analysis_type}")

    return {"result": result}


@router.get("/{spatial_data_id}/intersects")
async def find_intersecting_data(
    spatial_data_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Find all spatial data that intersects with the given data."""
    spatial_data = await db.query(SpatialData).filter(SpatialData.id == spatial_data_id).first()
    if not spatial_data:
        raise NotFoundError(f"Spatial data with ID {spatial_data_id} not found")

    intersecting_data = (
        await db.query(SpatialData)
        .filter(func.ST_Intersects(SpatialData.geometry, spatial_data.geometry))
        .all()
    )

    return intersecting_data
