from typing import Any, Dict, List

from fastapi import Depends, HTTPException, status
from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.base import BaseAPIRouter, PaginationParams
from app.core.exceptions import ValidationError
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.spatial import SpatialDataDB
from app.models.user import User

router = BaseAPIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/buffer")
async def create_buffer(
    spatial_data_id: int,
    distance: float,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create a buffer around spatial data."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")

    buffer_query = text(
        """
        SELECT ST_Buffer(geometry, :distance) as buffer_geom
        FROM spatial_data
        WHERE id = :spatial_data_id
    """
    )

    result = await db.execute(
        buffer_query, {"distance": distance, "spatial_data_id": spatial_data_id}
    )
    buffer_geom = result.scalar()

    return {"buffer_geometry": buffer_geom.to_geojson() if buffer_geom else None}


@router.post("/intersection")
async def calculate_intersection(
    spatial_data_id1: int,
    spatial_data_id2: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Calculate intersection between two spatial data entries."""
    query = text(
        """
        SELECT ST_Intersection(a.geometry, b.geometry) as intersection_geom
        FROM spatial_data a, spatial_data b
        WHERE a.id = :id1 AND b.id = :id2
    """
    )

    result = await db.execute(query, {"id1": spatial_data_id1, "id2": spatial_data_id2})
    intersection_geom = result.scalar()

    return {"intersection_geometry": intersection_geom.to_geojson() if intersection_geom else None}


@router.post("/union")
async def calculate_union(
    spatial_data_ids: List[int],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Calculate union of multiple spatial data entries."""
    if len(spatial_data_ids) < 2:
        raise ValidationError("At least two spatial data IDs are required")

    # Create a dynamic query based on the number of IDs
    placeholders = ", ".join([f":id{i}" for i in range(len(spatial_data_ids))])
    query = text(
        f"""
        SELECT ST_Union(geometry) as union_geom
        FROM spatial_data
        WHERE id IN ({placeholders})
    """
    )

    params = {f"id{i}": id for i, id in enumerate(spatial_data_ids)}
    result = await db.execute(query, params)
    union_geom = result.scalar()

    return {"union_geometry": union_geom.to_geojson() if union_geom else None}


@router.get("/nearest")
async def find_nearest(
    spatial_data_id: int,
    limit: int = 5,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Find nearest spatial data entries to a given entry."""
    query = text(
        """
        WITH target AS (
            SELECT geometry
            FROM spatial_data
            WHERE id = :spatial_data_id
        )
        SELECT 
            sd.id,
            sd.name,
            sd.geometry,
            ST_Distance(sd.geometry, target.geometry) as distance
        FROM spatial_data sd, target
        WHERE sd.id != :spatial_data_id
        ORDER BY distance
        LIMIT :limit
    """
    )

    result = await db.execute(query, {"spatial_data_id": spatial_data_id, "limit": limit})

    nearest = []
    for row in result:
        nearest.append(
            {
                "id": row.id,
                "name": row.name,
                "geometry": row.geometry.to_geojson(),
                "distance": row.distance,
            }
        )

    return {"nearest": nearest}


@router.get("/density")
async def calculate_density(
    bbox: str,  # Format: "minx,miny,maxx,maxy"
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Calculate spatial density within a bounding box."""
    try:
        minx, miny, maxx, maxy = map(float, bbox.split(","))
    except ValueError:
        raise ValidationError("Invalid bounding box format. Use: minx,miny,maxx,maxy")

    query = text(
        """
        WITH bbox AS (
            SELECT ST_MakeEnvelope(:minx, :miny, :maxx, :maxy, 4326) as box
        )
        SELECT 
            COUNT(*) as count,
            ST_Area(bbox.box) as area,
            COUNT(*) / ST_Area(bbox.box) as density
        FROM spatial_data, bbox
        WHERE ST_Intersects(geometry, bbox.box)
    """
    )

    result = await db.execute(query, {"minx": minx, "miny": miny, "maxx": maxx, "maxy": maxy})

    density_data = result.first()
    return {"count": density_data.count, "area": density_data.area, "density": density_data.density}


@router.get("/clustering")
async def analyze_clustering(
    method: str = "kmeans",
    n_clusters: int = 5,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Perform spatial clustering analysis."""
    if method not in ["kmeans", "dbscan"]:
        raise ValidationError("Unsupported clustering method. Use 'kmeans' or 'dbscan'")

    if method == "kmeans":
        query = text(
            """
            WITH points AS (
                SELECT ST_Centroid(geometry) as point
                FROM spatial_data
                WHERE geometry IS NOT NULL
            ),
            clusters AS (
                SELECT 
                    ST_ClusterKMeans(point, :n_clusters) OVER () as cluster_id,
                    point
                FROM points
            )
            SELECT 
                cluster_id,
                ST_Collect(point) as cluster_points,
                COUNT(*) as point_count
            FROM clusters
            GROUP BY cluster_id
        """
        )
    else:  # DBSCAN
        query = text(
            """
            WITH points AS (
                SELECT ST_Centroid(geometry) as point
                FROM spatial_data
                WHERE geometry IS NOT NULL
            ),
            clusters AS (
                SELECT 
                    ST_ClusterDBSCAN(point, eps := 0.1, minpoints := 2) OVER () as cluster_id,
                    point
                FROM points
            )
            SELECT 
                cluster_id,
                ST_Collect(point) as cluster_points,
                COUNT(*) as point_count
            FROM clusters
            WHERE cluster_id IS NOT NULL
            GROUP BY cluster_id
        """
        )

    result = await db.execute(query, {"n_clusters": n_clusters})

    clusters = []
    for row in result:
        clusters.append(
            {
                "cluster_id": row.cluster_id,
                "points": row.cluster_points.to_geojson(),
                "point_count": row.point_count,
            }
        )

    return {"clusters": clusters}
