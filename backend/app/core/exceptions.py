from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class AppException(HTTPException):
    def __init__(
        self, status_code: int, code: str, message: str, details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code)
        self.code = code
        self.message = message
        self.details = details


class ValidationError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            message=message,
            details=details,
        )


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, code="AUTHENTICATION_ERROR", message=message
        )


class AuthorizationError(AppException):
    def __init__(self, message: str = "Not authorized"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, code="AUTHORIZATION_ERROR", message=message
        )


class NotFoundError(AppException):
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=f"{resource} with identifier {identifier} not found",
        )


class DatabaseError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="DATABASE_ERROR",
            message=message,
            details=details,
        )


class GeospatialError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="GEOSPATIAL_ERROR",
            message=message,
            details=details,
        )


class RateLimitError(AppException):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, code="RATE_LIMIT_ERROR", message=message
        )


class ExternalServiceError(AppException):
    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="EXTERNAL_SERVICE_ERROR",
            message=f"Error from {service}: {message}",
            details=details,
        )
