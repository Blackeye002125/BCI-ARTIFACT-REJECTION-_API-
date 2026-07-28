"""
Model Management Routes
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
import os
import joblib
import json
from datetime import datetime

from ..models import ModelInfoResponse
from ...src.artifact_removal import ArtifactRemovalSystem
from ...src.deep_learning import EEGAutoencoder
from ...src.utils import load_config, setup_logging

router = APIRouter()
logger = setup_logging()

# Global model instances
_current_model = None
_model_type = None

@router.get("/status", response_model=ModelInfoResponse)
async def get_model_status():
    """
    Get current model status.
    
    Returns:
        ModelInfoResponse with model details
    """
    return ModelInfoResponse(
        model_type=_model_type or "none",
        model_path="models/artifact_model_rf.joblib",
        loaded=_current_model is not None,
        training_date=None,
        accuracy=None
    )

@router.post("/switch")
async def switch_model(model_type: str):
    """
    Switch to a different model.
    
    Args:
        model_type: Type of model to load
    
    Returns:
        Status message
    """
    global _current_model, _model_type
    
    try:
        # Validate model type
        valid_models = ['random_forest', 'svm', 'autoencoder', 'lightweight']
        if model_type not in valid_models:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model type. Must be one of: {valid_models}"
            )
        
        # Load model based on type
        if model_type == 'random_forest':
            _current_model = joblib.load('models/artifact_model_rf.joblib')
        elif model_type == 'svm':
            _current_model = joblib.load('models/artifact_model_svm.joblib')
        elif model_type == 'autoencoder':
            from tensorflow import keras
            _current_model = keras.models.load_model('models/autoencoder.h5')
        elif model_type == 'lightweight':
            # Placeholder for lightweight model
            _current_model = joblib.load('models/lightweight_model.joblib')
        
        _model_type = model_type
        logger.info(f"Switched to model: {model_type}")
        
        return {
            "status": "success",
            "model_type": model_type,
            "message": f"Model switched to {model_type}"
        }
        
    except Exception as e:
        logger.error(f"Model switch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reload")
async def reload_model():
    """
    Reload the current model from disk.
    
    Returns:
        Status message
    """
    global _current_model
    
    if _model_type is None:
        raise HTTPException(status_code=400, detail="No model currently loaded")
    
    try:
        # Reload model
        if _model_type == 'random_forest':
            _current_model = joblib.load('models/artifact_model_rf.joblib')
        elif _model_type == 'svm':
            _current_model = joblib.load('models/artifact_model_svm.joblib')
        elif _model_type == 'autoencoder':
            from tensorflow import keras
            _current_model = keras.models.load_model('models/autoencoder.h5')
        
        logger.info(f"Reloaded model: {_model_type}")
        
        return {
            "status": "success",
            "message": f"Model reloaded successfully"
        }
        
    except Exception as e:
        logger.error(f"Model reload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_models():
    """
    List available models.
    
    Returns:
        List of available models
    """
    models_dir = 'models'
    available_models = []
    
    if os.path.exists(models_dir):
        for file in os.listdir(models_dir):
            if file.endswith(('.joblib', '.h5', '.pkl', '.pt')):
                available_models.append({
                    'name': file,
                    'path': os.path.join(models_dir, file),
                    'size_mb': os.path.getsize(os.path.join(models_dir, file)) / 1024 / 1024,
                    'modified': datetime.fromtimestamp(
                        os.path.getmtime(os.path.join(models_dir, file))
                    ).isoformat()
                })
    
    return {
        "status": "success",
        "models": available_models,
        "current_model": _model_type
    }
