"""
Pydantic Models for API Requests and Responses
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import numpy as np

class EEGDataRequest(BaseModel):
    """
    Request model for EEG data processing.
    """
    channels: List[str] = Field(..., description="Channel names")
    data: List[List[float]] = Field(..., description="EEG data [samples x channels]")
    sampling_rate: float = Field(250.0, description="Sampling rate in Hz")
    timestamp: Optional[str] = Field(None, description="Timestamp of data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('data')
    def validate_data_shape(cls, v):
        """Validate data shape."""
        if len(v) == 0:
            raise ValueError("Data cannot be empty")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "channels": ["Fz", "Cz", "Pz", "Oz"],
                "data": [[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]],
                "sampling_rate": 250.0,
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }

class ArtifactResponse(BaseModel):
    """
    Response model for artifact removal.
    """
    cleaned_data: List[List[float]] = Field(..., description="Cleaned EEG data")
    artifacts_removed: int = Field(..., description="Number of artifacts removed")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    snr_improvement: float = Field(..., description="SNR improvement in dB")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score")
    status: str = Field("success", description="Processing status")
    timestamp: str = Field(..., description="Response timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "cleaned_data": [[0.09, 0.19, 0.29, 0.39], [0.49, 0.59, 0.69, 0.79]],
                "artifacts_removed": 2,
                "processing_time_ms": 15.3,
                "snr_improvement": 5.7,
                "confidence_score": 0.92,
                "status": "success",
                "timestamp": "2024-01-01T12:00:00.123Z"
            }
        }

class HealthResponse(BaseModel):
    """
    Health check response model.
    """
    status: str = Field("healthy", description
