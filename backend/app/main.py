from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.api.v1 import endpoints_maps
from app.utils.logging import setup_logging, get_logger
from app.utils.cache import setup_cache

# Initialize logging
logger = setup_logging()
app_logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize resources (e.g., database connections, ML models, cache)
    app_logger.info(f"Starting application in {settings.ENVIRONMENT} environment")
    
    # Setup Redis cache
    redis = await setup_cache(app)
    
    app_logger.info("Application startup complete")
    yield
    
    # Cleanup resources
    app_logger.info("Shutting down application")
    if redis:
        await redis.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for serving geospatial data and analysis results.",
    version="0.1.0",
    lifespan=lifespan,
    debug=settings.ENV_SETTINGS.get("debug", False)
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(endpoints_maps.router, prefix=f"{settings.API_V1_STR}/maps", tags=["Maps"])

@app.get("/")
async def read_root():
    return {
        "message": "Welcome to the ESDA Web Mapping API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }