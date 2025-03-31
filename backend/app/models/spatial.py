from datetime import datetime
from typing import Any, Dict, Optional

from geoalchemy2 import Geometry
from pydantic import BaseModel, Field, validator
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class SpatialDataBase(BaseModel):
    """Base spatial data model with common attributes."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    geometry_type: str = Field(
        ..., regex="^(Point|LineString|Polygon|MultiPoint|MultiLineString|MultiPolygon)$"
    )
    srid: int = Field(default=4326, ge=0, le=999999)


class SpatialDataCreate(SpatialDataBase):
    """Model for creating new spatial data entries."""

    geometry: str = Field(..., description="GeoJSON geometry string")

    @validator("geometry")
    def validate_geometry(cls, v):
        """Validate that the geometry string is valid GeoJSON."""
        try:
            import json

            geom = json.loads(v)
            if not isinstance(geom, dict) or "type" not in geom or "coordinates" not in geom:
                raise ValueError("Invalid GeoJSON format")
            return v
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON string")


class SpatialDataUpdate(BaseModel):
    """Model for updating spatial data entries."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = None
    geometry: Optional[str] = None

    @validator("geometry")
    def validate_geometry(cls, v):
        """Validate that the geometry string is valid GeoJSON."""
        if v is None:
            return v
        try:
            import json

            geom = json.loads(v)
            if not isinstance(geom, dict) or "type" not in geom or "coordinates" not in geom:
                raise ValueError("Invalid GeoJSON format")
            return v
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON string")


class SpatialDataInDB(SpatialDataBase):
    """Database model for spatial data."""

    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    geometry: str

    class Config:
        orm_mode = True


class SpatialData(SpatialDataInDB):
    """API model for spatial data."""

    pass


# SQLAlchemy Models
class SpatialDataDB(Base):
    """SQLAlchemy model for spatial data."""

    __tablename__ = "spatial_data"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    metadata = Column(JSON)
    geometry = Column(Geometry(geometry_type="GEOMETRY", srid=4326))
    geometry_type = Column(String(50), nullable=False)
    srid = Column(Integer, default=4326)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    creator = relationship("User", back_populates="spatial_data")

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "geometry": self.geometry.to_geojson() if self.geometry else None,
            "geometry_type": self.geometry_type,
            "srid": self.srid,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpatialDataDB":
        """Create model instance from dictionary."""
        return cls(**data)

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update model instance from dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
