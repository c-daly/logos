"""
Standalone FastAPI application for media ingestion service.

This can be run with:
    uvicorn logos_perception.app:app --host 0.0.0.0 --port 8002
"""

import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .media_api import create_media_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="LOGOS Media Ingestion Service",
    description="Media upload and streaming service for perception workflows",
    version="0.2.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup."""
    logger.info("Starting Media Ingestion Service")

    # Get configuration from environment
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "logosdev")
    storage_path = os.getenv("MEDIA_STORAGE_PATH", "/tmp/logos_media")

    logger.info(f"Connecting to Neo4j at {neo4j_uri}")

    # Create Neo4j driver
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    # Test connection
    try:
        with driver.session() as session:
            session.run("RETURN 1")
        logger.info("Neo4j connection successful")
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {e}")
        # Continue anyway for Talos-free scenarios

    # Store driver in app state
    app.state.neo4j_driver = driver
    app.state.storage_path = Path(storage_path)

    # Mount media API routes
    media_router = create_media_api(driver, Path(storage_path))
    app.include_router(media_router)

    logger.info("Media Ingestion Service started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections on shutdown."""
    logger.info("Shutting down Media Ingestion Service")

    if hasattr(app.state, "neo4j_driver"):
        app.state.neo4j_driver.close()
        logger.info("Neo4j connection closed")


@app.get("/")
def root():
    """Root endpoint with service information."""
    return {
        "service": "LOGOS Media Ingestion Service",
        "version": "0.2.0",
        "endpoints": {
            "health": "/media/health",
            "upload": "/media/upload (POST)",
            "stream_start": "/media/stream/start (POST)",
            "stream_stop": "/media/stream/{stream_id}/stop (POST)",
            "frame_metadata": "/media/frames/{frame_id} (GET)",
            "docs": "/docs",
        },
    }


@app.get("/health")
def health():
    """Simple health check."""
    return {"status": "healthy", "service": "media-ingest"}
