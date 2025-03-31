import logging
import time
from typing import Callable, Optional

from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint

from app.core.config import settings
from app.core.exceptions import AppException, ErrorResponse

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except AppException as e:
            return JSONResponse(
                status_code=e.status_code,
                content=ErrorResponse(code=e.code, message=e.message, details=e.details).dict(),
            )
        except Exception as e:
            logger.exception("Unhandled exception occurred")
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    code="INTERNAL_SERVER_ERROR",
                    message="An unexpected error occurred",
                    details={"error": str(e)} if settings.ENVIRONMENT == "development" else None,
                ).dict(),
            )


class RequestValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Add request validation logic here
        # For example, validate content type, required headers, etc.
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("application/json"):
                return JSONResponse(
                    status_code=415,
                    content=ErrorResponse(
                        code="UNSUPPORTED_MEDIA_TYPE",
                        message="Content-Type must be application/json",
                    ).dict(),
                )
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        requests_per_minute: int = settings.RATE_LIMIT_REQUESTS,
        window_seconds: int = settings.RATE_LIMIT_PERIOD,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = request.client.host
        current_time = time.time()

        # Clean up old requests
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time
                for req_time in self.requests[client_ip]
                if current_time - req_time < self.window_seconds
            ]
        else:
            self.requests[client_ip] = []

        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content=ErrorResponse(
                    code="RATE_LIMIT_EXCEEDED", message="Too many requests"
                ).dict(),
            )

        # Add current request
        self.requests[client_ip].append(current_time)

        return await call_next(request)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()

        # Log request
        logger.info(
            "Request started",
            extra={
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host,
                "user_agent": request.headers.get("user-agent"),
            },
        )

        try:
            response = await call_next(request)

            # Log response
            process_time = time.time() - start_time
            logger.info(
                "Request completed",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "process_time": f"{process_time:.3f}s",
                },
            )

            return response
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                "Request failed",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "error": str(e),
                    "process_time": f"{process_time:.3f}s",
                },
            )
            raise
