from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging.config
from app.core.config import settings
from app.core.middleware import (
    ErrorHandlingMiddleware,
    RequestValidationMiddleware,
    RateLimitMiddleware,
    LoggingMiddleware
)

# Configure logging
logging.config.dictConfig(settings.get_logging_config())
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting up application...")
    # Initialize resources (e.g., database connections, ML models)
    yield
    logger.info("Shutting down application...")
    # Cleanup resources

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for serving geospatial data and analysis results.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestValidationMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT
    }

# Include routers
# app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
# app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
# app.include_router(maps_router, prefix=f"{settings.API_V1_STR}/maps", tags=["maps"])
# app.include_router(data_router, prefix=f"{settings.API_V1_STR}/data", tags=["data"])