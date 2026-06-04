"""
PlutoClips Worker - Main Application Entry Point

A production-ready backend service for video processing, transcription,
AI-driven clip detection, automatic cutting, and caption generation.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api import routes
from app.core.config import settings
from app.core.logger import setup_logger
from app.storage.local import LocalStorage
from app.database.sqlite import init_database

# Setup logging
setup_logger()
logger = logging.getLogger(__name__)

# Initialize storage directories
def _init_storage() -> None:
    """Create necessary storage directories if they don't exist."""
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    logger.info(f"Storage directories initialized: {settings.UPLOAD_DIR}, {settings.OUTPUT_DIR}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager for startup/shutdown events.
    
    Startup:
    - Initialize storage directories
    - Initialize database
    - Verify API keys are configured
    
    Shutdown:
    - Clean up resources
    """
    # Startup
    logger.info("=== PlutoClips Worker Starting ===")
    _init_storage()
    init_database()
    
    # Verify critical configuration
    if not settings.OPENAI_API_KEY:
        logger.warning("⚠️  OPENAI_API_KEY not configured")
    if not settings.ANTHROPIC_API_KEY:
        logger.warning("⚠️  ANTHROPIC_API_KEY not configured")
    
    logger.info("✓ PlutoClips Worker initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("=== PlutoClips Worker Shutting Down ===")
    logger.info("Cleanup completed")


# Create FastAPI application
app = FastAPI(
    title="PlutoClips Worker",
    description="Backend service for AI-driven video clip generation",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
origins = settings.ALLOWED_ORIGINS.split(",") if isinstance(settings.ALLOWED_ORIGINS, str) else settings.ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add compression middleware for responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routes
app.include_router(routes.router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint.
    
    Returns:
        dict: Status indicator
    """
    return {"status": "ok"}


@app.get("/")
async def root() -> dict:
    """Root endpoint with service information."""
    return {
        "service": "PlutoClips Worker",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "api": "/api/v1",
            "docs": "/docs",
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=not settings.ENVIRONMENT == "production",
        log_level=settings.LOG_LEVEL.lower(),
    )
