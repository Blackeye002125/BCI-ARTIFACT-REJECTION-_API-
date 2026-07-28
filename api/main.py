"""
Main FastAPI Application
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import asyncio
from contextlib import asynccontextmanager
import time
import logging

from .routes import process, model, health, visualize, export
from .websocket_handler import WebSocketHandler
from ..src.utils import setup_logging, load_config

# Setup logging
logger = setup_logging()

# Load configuration
config = load_config()

# Global state
app_start_time = time.time()
websocket_handler = WebSocketHandler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting BCI Artifact Rejection API...")
    logger.info(f"Configuration: {config}")
    
    # Initialize WebSocket handler
    await websocket_handler.start()
    
    yield
    
    # Shutdown
    logger.info("Shutting down BCI Artifact Rejection API...")
    await websocket_handler.stop()

# Create FastAPI application
app = FastAPI(
    title="BCI Artifact Rejection API",
    description="AI-powered EEG artifact rejection for BCI applications",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get('api', {}).get('allowed_origins', ['*']),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=config.get('api', {}).get('allowed_hosts', ['*'])
)

# Include routers
app.include_router(process.router, prefix="/process", tags=["Processing"])
app.include_router(model.router, prefix="/model", tags=["Models"])
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(visualize.router, prefix="/visualize", tags=["Visualization"])
app.include_router(export.router, prefix="/export", tags=["Export"])

# WebSocket endpoint
@app.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time EEG processing.
    """
    await websocket_handler.handle_connection(websocket)

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {
        "message": "BCI Artifact Rejection API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Handle HTTP exceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status": "error",
            "timestamp": time.time()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Handle general exceptions.
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status": "error",
            "timestamp": time.time()
        }
    )
