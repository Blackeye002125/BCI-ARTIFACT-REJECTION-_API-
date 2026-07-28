"""
Export Routes for Processed Data
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
import numpy as np
import json
import io
import csv
from typing import Optional
from datetime import datetime

from ..models import EEGDataRequest
from ...src.utils import setup_logging

router = APIRouter()
logger = setup_logging()

@router.post("/csv")
async def export_to_csv(request: EEGDataRequest):
    """
    Export cleaned data as CSV.
    
    Args:
        request: EEG data request
    
    Returns:
        CSV file download
    """
    try:
        # Process data
        data = np.array(request.data)
        cleaned_data = data * 0.85  # Simulate cleaning
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        header = ['time'] + request.channels
        writer.writerow(header)
        
        # Write data
        for i, row in enumerate(cleaned_data):
            time_val = i / request.sampling_rate
            writer.writerow([time_val] + row.tolist())
        
        # Create response
        response = StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv"
        )
        response.headers["Content-Disposition"] = f"attachment; filename=eeg_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return response
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/json")
async def export_to_json(request: EEGDataRequest):
    """
    Export cleaned data as JSON.
    
    Args:
        request: EEG data request
    
    Returns:
        JSON file download
    """
    try:
        # Process data
        data = np.array(request.data)
        cleaned_data = data * 0.85  # Simulate cleaning
        
        # Create JSON structure
        result = {
            "metadata": {
                "channels": request.channels,
                "sampling_rate": request.sampling_rate,
                "timestamp": request.timestamp,
                "export_date": datetime.now().isoformat()
            },
            "data": cleaned_data.tolist(),
            "channels": request.channels
        }
        
        # Create response
        json_str = json.dumps(result, indent=2)
        response = StreamingResponse(
            io.BytesIO(json_str.encode('utf-8')),
            media_type="application/json"
        )
        response.headers["Content-Disposition"] = f"attachment; filename=eeg_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return response
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/matlab")
async def export_to_matlab(request: EEGDataRequest):
    """
    Export cleaned data as MATLAB .mat file.
    
    Args:
        request: EEG data request
    
    Returns:
        .mat file download
    """
    try:
        import scipy.io as sio
        
        # Process data
        data = np.array(request.data)
        cleaned_data = data * 0.85  # Simulate cleaning
        
        # Create MATLAB structure
        mat_dict = {
            'data': cleaned_data,
            'channels': request.channels,
            'sampling_rate': request.sampling_rate,
            'timestamp': request.timestamp or datetime.now().isoformat()
        }
        
        # Save to memory
        mat_buffer = io.BytesIO()
        sio.savemat(mat_buffer, mat_dict)
        mat_buffer.seek(0)
        
        # Create response
        response = StreamingResponse(
            mat_buffer,
            media_type="application/octet-stream"
        )
        response.headers["Content-Disposition"] = f"attachment; filename=eeg_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mat"
        
        return response
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
