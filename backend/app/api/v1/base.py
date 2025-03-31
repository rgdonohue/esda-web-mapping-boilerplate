from typing import Any, Dict, Generic, Optional, TypeVar

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user
from app.db.session import get_db

T = TypeVar("T")


class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(10, ge=1, le=100, description="Items per page"),
        sort_by: Optional[str] = Query(None, description="Field to sort by"),
        sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    ):
        self.page = page
        self.size = size
        self.sort_by = sort_by
        self.sort_order = sort_order


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""

    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class BaseAPIRouter(APIRouter):
    """Base API router with common functionality."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dependencies = [Depends(get_current_active_user), Depends(get_db)]

    def add_paginated_endpoint(
        self,
        path: str,
        endpoint: Any,
        response_model: Any,
        summary: str = "",
        description: str = "",
        **kwargs,
    ):
        """Add a paginated endpoint with common parameters."""
        self.add_api_route(
            path,
            endpoint,
            response_model=PaginatedResponse[response_model],
            summary=summary,
            description=description,
            **kwargs,
        )

    def add_crud_endpoints(
        self,
        prefix: str,
        response_model: Any,
        create_model: Any,
        update_model: Any,
        get_all_endpoint: Any,
        get_by_id_endpoint: Any,
        create_endpoint: Any,
        update_endpoint: Any,
        delete_endpoint: Any,
        **kwargs,
    ):
        """Add standard CRUD endpoints."""
        self.add_paginated_endpoint(
            f"/{prefix}", get_all_endpoint, response_model, summary=f"Get all {prefix}", **kwargs
        )

        self.add_api_route(
            f"/{prefix}/{{item_id}}",
            get_by_id_endpoint,
            response_model=response_model,
            summary=f"Get {prefix} by ID",
            **kwargs,
        )

        self.add_api_route(
            f"/{prefix}",
            create_endpoint,
            response_model=response_model,
            summary=f"Create {prefix}",
            **kwargs,
        )

        self.add_api_route(
            f"/{prefix}/{{item_id}}",
            update_endpoint,
            response_model=response_model,
            summary=f"Update {prefix}",
            **kwargs,
        )

        self.add_api_route(
            f"/{prefix}/{{item_id}}",
            delete_endpoint,
            response_model=response_model,
            summary=f"Delete {prefix}",
            **kwargs,
        )
