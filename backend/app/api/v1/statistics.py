from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import Depends, HTTPException, status
from scipy import stats
from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.base import BaseAPIRouter
from app.core.exceptions import ValidationError
from app.core.security import get_current_active_user
from app.core.spatial_analysis import (
    analyze_spatial_patterns,
    calculate_density,
    calculate_geostatistics,
    calculate_network_analysis,
    calculate_ripleys_k,
    calculate_spatial_autocorrelation,
    perform_spatial_interpolation,
    perform_spatial_regression,
)
from app.db.session import get_db
from app.models.spatial import SpatialDataDB
from app.models.user import User

router = BaseAPIRouter(prefix="/statistics", tags=["statistics"])


@router.get("/summary/{spatial_data_id}")
async def get_summary_statistics(
    spatial_data_id: int,
    field: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get summary statistics for spatial data."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")

    # Get basic geometry statistics
    geom_stats_query = text(
        """
        SELECT 
            ST_Area(geometry) as area,
            ST_Perimeter(geometry) as perimeter,
            ST_NumPoints(geometry) as num_points,
            ST_NumGeometries(geometry) as num_geometries
        FROM spatial_data
        WHERE id = :spatial_data_id
    """
    )

    result = await db.execute(geom_stats_query, {"spatial_data_id": spatial_data_id})
    geom_stats = result.first()

    summary = {
        "geometry": {
            "area": float(geom_stats.area) if geom_stats.area else None,
            "perimeter": float(geom_stats.perimeter) if geom_stats.perimeter else None,
            "num_points": geom_stats.num_points,
            "num_geometries": geom_stats.num_geometries,
        }
    }

    # If field is specified, calculate field statistics
    if field and spatial_data.metadata and field in spatial_data.metadata:
        values = spatial_data.metadata[field]
        if isinstance(values, (list, tuple)) and all(isinstance(x, (int, float)) for x in values):
            values = np.array(values)
            summary["field"] = {
                "field_name": field,
                "count": len(values),
                "mean": float(np.mean(values)),
                "median": float(np.median(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "q1": float(np.percentile(values, 25)),
                "q3": float(np.percentile(values, 75)),
            }

    return summary


@router.get("/spatial-autocorrelation/{spatial_data_id}")
async def calculate_spatial_autocorrelation(
    spatial_data_id: int,
    field: str,
    method: str = "moran",
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Calculate spatial autocorrelation statistics."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")

    if not spatial_data.metadata or field not in spatial_data.metadata:
        raise ValidationError(f"Field {field} not found in metadata")

    values = spatial_data.metadata[field]
    if not isinstance(values, (list, tuple)) or not all(
        isinstance(x, (int, float)) for x in values
    ):
        raise ValidationError(f"Field {field} must contain numeric values")

    # Get spatial weights matrix
    weights_query = text(
        """
        WITH points AS (
            SELECT ST_Centroid(geometry) as point
            FROM spatial_data
            WHERE id = :spatial_data_id
        )
        SELECT 
            a.id as id1,
            b.id as id2,
            ST_Distance(a.point, b.point) as distance
        FROM points a, points b
        WHERE a.id < b.id
    """
    )

    result = await db.execute(weights_query, {"spatial_data_id": spatial_data_id})
    distances = result.fetchall()

    # Create spatial weights matrix
    n = len(values)
    weights = np.zeros((n, n))
    for d in distances:
        weights[d.id1, d.id2] = 1 / (d.distance**2)
        weights[d.id2, d.id1] = weights[d.id1, d.id2]

    # Calculate Moran's I
    if method == "moran":
        values = np.array(values)
        z = values - np.mean(values)
        moran_i = np.sum(weights * np.outer(z, z)) / (np.sum(weights) * np.sum(z**2))

        # Calculate expected value and variance
        expected = -1 / (n - 1)
        variance = n * (
            (n**2 - 3 * n + 3) * np.sum(weights**2)
            - n * np.sum(weights.sum(axis=1) ** 2)
            + 3 * np.sum(weights) ** 2
        ) - (
            k
            * (
                (n**2 - n) * np.sum(weights**2)
                - 2 * n * np.sum(weights.sum(axis=1) ** 2)
                + 6 * np.sum(weights) ** 2
            )
        ) / (
            (n - 1) * (n - 2) * (n - 3) * np.sum(weights) ** 2
        )

        z_score = (moran_i - expected) / np.sqrt(variance)
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))

        return {
            "method": "moran",
            "moran_i": float(moran_i),
            "expected": float(expected),
            "variance": float(variance),
            "z_score": float(z_score),
            "p_value": float(p_value),
        }

    raise ValidationError(f"Unsupported method: {method}")


@router.get("/density-analysis/{spatial_data_id}")
async def analyze_density(
    spatial_data_id: int,
    method: str = "kernel",
    bandwidth: Optional[float] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Perform density analysis on spatial data."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")

    # Get point coordinates
    points_query = text(
        """
        SELECT ST_X(ST_Centroid(geometry)) as x, ST_Y(ST_Centroid(geometry)) as y
        FROM spatial_data
        WHERE id = :spatial_data_id
    """
    )

    result = await db.execute(points_query, {"spatial_data_id": spatial_data_id})
    points = result.fetchall()

    if not points:
        raise ValidationError("No point features found")

    # Convert to numpy arrays
    x = np.array([p.x for p in points])
    y = np.array([p.y for p in points])

    if method == "kernel":
        # Perform kernel density estimation
        if bandwidth is None:
            # Calculate optimal bandwidth using Scott's rule
            bandwidth = np.std([x, y]) * (len(x) ** (-1 / 6))

        # Create grid for density estimation
        x_min, x_max = x.min(), x.max()
        y_min, y_max = y.min(), y.max()
        x_grid = np.linspace(x_min, x_max, 100)
        y_grid = np.linspace(y_min, y_max, 100)
        X, Y = np.meshgrid(x_grid, y_grid)

        # Calculate kernel density
        positions = np.vstack([X.ravel(), Y.ravel()])
        values = np.vstack([x, y])
        kernel = stats.gaussian_kde(values, bw_method=bandwidth)
        Z = np.reshape(kernel(positions), X.shape)

        return {
            "method": "kernel",
            "bandwidth": float(bandwidth),
            "x_grid": x_grid.tolist(),
            "y_grid": y_grid.tolist(),
            "density": Z.tolist(),
        }

    raise ValidationError(f"Unsupported method: {method}")


@router.get("/spatial-pattern/{spatial_data_id}")
async def analyze_spatial_pattern(
    spatial_data_id: int,
    method: str = "ripley",
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Analyze spatial pattern of point data."""
    spatial_data = await db.query(SpatialDataDB).filter(SpatialDataDB.id == spatial_data_id).first()
    if not spatial_data:
        raise ValidationError(f"Spatial data with ID {spatial_data_id} not found")

    # Get point coordinates
    points_query = text(
        """
        SELECT ST_X(ST_Centroid(geometry)) as x, ST_Y(ST_Centroid(geometry)) as y
        FROM spatial_data
        WHERE id = :spatial_data_id
    """
    )

    result = await db.execute(points_query, {"spatial_data_id": spatial_data_id})
    points = result.fetchall()

    if not points:
        raise ValidationError("No point features found")

    # Convert to numpy arrays
    x = np.array([p.x for p in points])
    y = np.array([p.y for p in points])

    if method == "ripley":
        # Calculate Ripley's K function
        r = np.linspace(0, np.max([x.max() - x.min(), y.max() - y.min()]), 100)
        k_values = []

        for r_val in r:
            # Count pairs within distance r
            distances = np.sqrt((x[:, np.newaxis] - x) ** 2 + (y[:, np.newaxis] - y) ** 2)
            pairs = np.sum(distances <= r_val)
            k = pairs / (len(x) * (len(x) - 1))
            k_values.append(float(k))

        return {"method": "ripley", "r": r.tolist(), "k": k_values}

    raise ValidationError(f"Unsupported method: {method}")


@router.get("/network-analysis/{spatial_data_id}")
async def network_analysis(spatial_data_id: int, db: AsyncSession = Depends(get_db)):
    """Perform network analysis on spatial data."""
    try:
        # Get spatial data
        spatial_data = await db.get(SpatialDataDB, spatial_data_id)
        if not spatial_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Spatial data not found"
            )

        # Perform network analysis
        result = await calculate_network_analysis(spatial_data)

        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/spatial-interpolation/{spatial_data_id}")
async def spatial_interpolation(
    spatial_data_id: int,
    method: str = "idw",  # idw, kriging, spline
    field: str = None,
    resolution: float = 0.1,
    db: AsyncSession = Depends(get_db),
):
    """Perform spatial interpolation on point data."""
    try:
        # Get spatial data
        spatial_data = await db.get(SpatialDataDB, spatial_data_id)
        if not spatial_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Spatial data not found"
            )

        # Perform spatial interpolation
        result = await perform_spatial_interpolation(
            spatial_data, method=method, field=field, resolution=resolution
        )

        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/pattern-analysis/{spatial_data_id}")
async def pattern_analysis(
    spatial_data_id: int,
    method: str = "quadrat",  # quadrat, nearest_neighbor, ripleys_k
    db: AsyncSession = Depends(get_db),
):
    """Analyze spatial patterns in the data."""
    try:
        # Get spatial data
        spatial_data = await db.get(SpatialDataDB, spatial_data_id)
        if not spatial_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Spatial data not found"
            )

        # Analyze spatial patterns
        result = await analyze_spatial_patterns(spatial_data, method=method)

        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/geostatistics/{spatial_data_id}")
async def geostatistics(spatial_data_id: int, field: str, db: AsyncSession = Depends(get_db)):
    """Calculate geostatistical measures."""
    try:
        # Get spatial data
        spatial_data = await db.get(SpatialDataDB, spatial_data_id)
        if not spatial_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Spatial data not found"
            )

        # Calculate geostatistics
        result = await calculate_geostatistics(spatial_data, field)

        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/spatial-regression/{spatial_data_id}")
async def spatial_regression(
    spatial_data_id: int,
    dependent_field: str,
    independent_fields: List[str],
    method: str = "ols",  # ols, gwr, spatial_lag, spatial_error
    db: AsyncSession = Depends(get_db),
):
    """Perform spatial regression analysis."""
    try:
        # Get spatial data
        spatial_data = await db.get(SpatialDataDB, spatial_data_id)
        if not spatial_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Spatial data not found"
            )

        # Perform spatial regression
        result = await perform_spatial_regression(
            spatial_data,
            dependent_field=dependent_field,
            independent_fields=independent_fields,
            method=method,
        )

        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
