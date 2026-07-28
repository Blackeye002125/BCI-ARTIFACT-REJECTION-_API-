"""
Health and Monitoring Routes
"""

from fastapi import APIRouter
import time
import psutil
import os
from datetime import datetime
from typing import Dict, Any

from ..models import HealthResponse
from ...src.utils import load_config

router = APIRouter()

# API start time
START_TIME = time.time()

@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        HealthResponse with system status
    """
    # Get system metrics
    uptime = time.time() - START_TIME
    
    # Memory usage
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    # CPU usage
    cpu_percent = psutil.cpu_percent(interval=0.1)
    
    # Check if model is loaded
    model_loaded = True  # Placeholder
    
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        active_connections=0,  # Will be updated by WebSocket handler
        model_loaded=model_loaded,
        cache_size=0,
        uptime_seconds=uptime,
        timestamp=datetime.now().isoformat()
    )

@router.get("/metrics")
async def get_metrics():
    """
    Get Prometheus metrics.
    
    Returns:
        Metrics dictionary
    """
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        "status": "success",
        "metrics": {
            "uptime_seconds": time.time() - START_TIME,
            "memory_usage_mb": memory_info.rss / 1024 / 1024,
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "active_connections": 0,  # Will be updated
            "model_loaded": True,
            "cache_size": 0
        },
        "timestamp": datetime.now().isoformat()
    }

@router.get("/detailed")
async def detailed_health():
    """
    Detailed health check with system information.
    
    Returns:
        Detailed health information
    """
    process = psutil.Process(os.getpid())
    
    return {
        "status": "healthy",
        "system": {
            "cpu": {
                "percent": psutil.cpu_percent(interval=0.1),
                "cores": psutil.cpu_count(),
                "load_avg": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            },
            "memory": {
                "total_mb": psutil.virtual_memory().total / 1024 / 1024,
                "available_mb": psutil.virtual_memory().available / 1024 / 1024,
                "used_mb": psutil.virtual_memory().used / 1024 / 1024,
                "percent": psutil.virtual_memory().percent
            },
            "process": {
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "cpu_percent": process.cpu_percent(interval=0.1),
                "threads": process.num_threads()
            }
        },
        "api": {
            "uptime_seconds": time.time() - START_TIME,
            "uptime_hours": (time.time() - START_TIME) / 3600,
            "start_time": datetime.fromtimestamp(START_TIME).isoformat(),
            "version": "2.0.0"
        },
        "timestamp": datetime.now().isoformat()
    }
