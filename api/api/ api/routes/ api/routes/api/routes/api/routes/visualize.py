"""
Visualization Routes
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from typing import Optional
import json

from ..models import EEGDataRequest
from ...src.utils import setup_logging

router = APIRouter()
logger = setup_logging()

@router.post("/spectrogram")
async def visualize_spectrogram(request: EEGDataRequest):
    """
    Generate spectrogram visualization of EEG data.
    
    Args:
        request: EEG data request
    
    Returns:
        Base64 encoded image
    """
    try:
        data = np.array(request.data)
        
        # Create spectrogram
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Use first channel for visualization
        signal = data[:, 0] if len(data.shape) > 1 else data
        
        # Compute spectrogram
        Pxx, freqs, bins, im = ax.specgram(
            signal,
            NFFT=256,
            Fs=request.sampling_rate,
            noverlap=128,
            cmap='jet'
        )
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Frequency (Hz)')
        ax.set_title('EEG Spectrogram')
        
        # Add colorbar
        plt.colorbar(im, ax=ax, label='Power (dB)')
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        return JSONResponse({
            "status": "success",
            "image": f"data:image/png;base64,{image_base64}",
            "format": "png"
        })
        
    except Exception as e:
        logger.error(f"Visualization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plot")
async def visualize_timeseries(request: EEGDataRequest):
    """
    Generate time series plot of EEG data.
    
    Args:
        request: EEG data request
    
    Returns:
        Base64 encoded image
    """
    try:
        data = np.array(request.data)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot each channel
        for i, channel in enumerate(request.channels):
            if len(data.shape) == 1:
                signal = data
            else:
                signal = data[:, i] if i < data.shape[1] else data[:, 0]
            
            # Create time axis
            time = np.arange(len(signal)) / request.sampling_rate
            
            # Plot with offset
            offset = i * 2
            ax.plot(time, signal + offset, label=channel, alpha=0.8)
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude (µV)')
        ax.set_title('EEG Time Series')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        return JSONResponse({
            "status": "success",
            "image": f"data:image/png;base64,{image_base64}",
            "format": "png"
        })
        
    except Exception as e:
        logger.error(f"Visualization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/topomap")
async def visualize_topomap(request: EEGDataRequest):
    """
    Generate topographical map of EEG data.
    
    Args:
        request: EEG data request
    
    Returns:
        Base64 encoded image
    """
    try:
        # This requires channel positions which we don't have in this example
        # Return a placeholder
        return JSONResponse({
            "status": "info",
            "message": "Topomap requires channel positions. Use /spectrogram instead.",
            "image": None
        })
        
    except Exception as e:
        logger.error(f"Visualization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
