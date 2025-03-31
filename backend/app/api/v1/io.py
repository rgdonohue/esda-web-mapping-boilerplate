import io
import json
from typing import Any, List

import geopandas as gpd
from fastapi import Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.base import BaseAPIRouter
from app.core.exceptions import ValidationError
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.spatial import SpatialDataDB
from app.models.user import User

router = BaseAPIRouter(prefix="/io", tags=["io"])


@router.post("/import/geojson")
async def import_geojson(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Import spatial data from GeoJSON file."""
    if not file.filename.endswith(".geojson"):
        raise ValidationError("File must be a GeoJSON file")

    try:
        content = await file.read()
        geojson_data = json.loads(content)

        if not isinstance(geojson_data, dict) or "features" not in geojson_data:
            raise ValidationError("Invalid GeoJSON format")

        imported_features = []
        for feature in geojson_data["features"]:
            if "geometry" not in feature or "properties" not in feature:
                continue

            # Extract properties
            props = feature["properties"]
            name = props.get("name", "Unnamed Feature")
            description = props.get("description", "")
            metadata = {k: v for k, v in props.items() if k not in ["name", "description"]}

            # Create spatial data entry
            spatial_data = SpatialDataDB(
                name=name,
                description=description,
                metadata=metadata,
                geometry=feature["geometry"],
                geometry_type=feature["geometry"]["type"],
                created_by=current_user.id,
            )

            db.add(spatial_data)
            imported_features.append(name)

        await db.commit()
        return {
            "message": f"Successfully imported {len(imported_features)} features",
            "imported_features": imported_features,
        }

    except json.JSONDecodeError:
        raise ValidationError("Invalid JSON format")
    except Exception as e:
        raise ValidationError(f"Error importing GeoJSON: {str(e)}")


@router.post("/import/shapefile")
async def import_shapefile(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Import spatial data from Shapefile."""
    if not file.filename.endswith(".shp"):
        raise ValidationError("File must be a Shapefile (.shp)")

    try:
        # Save uploaded file temporarily
        content = await file.read()
        with open(f"temp_{file.filename}", "wb") as f:
            f.write(content)

        # Read Shapefile using geopandas
        gdf = gpd.read_file(f"temp_{file.filename}")

        imported_features = []
        for _, row in gdf.iterrows():
            # Convert to GeoJSON
            geojson = json.loads(row.geometry.to_json())

            # Create spatial data entry
            spatial_data = SpatialDataDB(
                name=str(row.get("name", "Unnamed Feature")),
                description=str(row.get("description", "")),
                metadata=row.drop(["geometry", "name", "description"]).to_dict(),
                geometry=geojson,
                geometry_type=geojson["type"],
                created_by=current_user.id,
            )

            db.add(spatial_data)
            imported_features.append(spatial_data.name)

        await db.commit()
        return {
            "message": f"Successfully imported {len(imported_features)} features",
            "imported_features": imported_features,
        }

    except Exception as e:
        raise ValidationError(f"Error importing Shapefile: {str(e)}")


@router.get("/export/geojson")
async def export_geojson(
    spatial_data_ids: List[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Export spatial data to GeoJSON format."""
    query = db.query(SpatialDataDB)

    if spatial_data_ids:
        query = query.filter(SpatialDataDB.id.in_(spatial_data_ids))

    spatial_data = await query.all()

    features = []
    for data in spatial_data:
        feature = {
            "type": "Feature",
            "geometry": json.loads(data.geometry.to_geojson()),
            "properties": {
                "id": data.id,
                "name": data.name,
                "description": data.description,
                **data.metadata,
            },
        }
        features.append(feature)

    geojson = {"type": "FeatureCollection", "features": features}

    return StreamingResponse(
        io.StringIO(json.dumps(geojson)),
        media_type="application/geo+json",
        headers={"Content-Disposition": f"attachment; filename=spatial_data.geojson"},
    )


@router.get("/export/shapefile")
async def export_shapefile(
    spatial_data_ids: List[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Export spatial data to Shapefile format."""
    query = db.query(SpatialDataDB)

    if spatial_data_ids:
        query = query.filter(SpatialDataDB.id.in_(spatial_data_ids))

    spatial_data = await query.all()

    # Create GeoDataFrame
    features = []
    for data in spatial_data:
        feature = {
            "geometry": data.geometry,
            "id": data.id,
            "name": data.name,
            "description": data.description,
            **data.metadata,
        }
        features.append(feature)

    gdf = gpd.GeoDataFrame(features)

    # Save to temporary file
    output_path = "temp_export.shp"
    gdf.to_file(output_path)

    return StreamingResponse(
        open(output_path, "rb"),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=spatial_data.shp"},
    )


@router.get("/export/csv")
async def export_csv(
    spatial_data_ids: List[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Export spatial data to CSV format with WKT geometry."""
    query = db.query(SpatialDataDB)

    if spatial_data_ids:
        query = query.filter(SpatialDataDB.id.in_(spatial_data_ids))

    spatial_data = await query.all()

    # Create CSV content
    csv_content = "id,name,description,geometry\n"
    for data in spatial_data:
        row = [str(data.id), data.name, data.description or "", data.geometry.to_wkt()]
        csv_content += ",".join(f'"{str(cell)}"' for cell in row) + "\n"

    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=spatial_data.csv"},
    )
