"""
Utility Functions for the BCI Artifact Rejection System
"""

import os
import yaml
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import numpy as np
from pathlib import Path

def setup_logging(log_file: str = 'logs/api.log', 
                  level: str = 'INFO') -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        log_file: Path to log file
        level: Logging level
    
    Returns:
        Configured logger
    """
    # Create logs directory if it doesn't exist
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: {log_file}")
    return logger

def load_config(config_path: str = 'config/development.yaml') -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
    
    Returns:
        Configuration dictionary
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        # Use default configuration
        return {
            'api': {
                'host': '0.0.0.0',
                'port': 8000,
                'workers': 4,
                'debug': True
            },
            'model': {
                'ica_method': 'fastica',
                'n_components': 20,
                'threshold': 0.7
            },
            'data': {
                'sampling_rate': 250.0,
                'band_pass_low': 1.0,
                'band_pass_high': 40.0,
                'notch_filter': 50.0
            }
        }
    
    with open(config_path, 'r') as f:
        if config_path.suffix == '.yaml' or config_path.suffix == '.yml':
            config = yaml.safe_load(f)
        elif config_path.suffix == '.json':
            config = json.load(f)
        else:
            raise ValueError(f"Unsupported config format: {config_path.suffix}")
    
    return config

def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Save configuration to file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to save config
    """
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        if config_path.suffix == '.yaml' or config_path.suffix == '.yml':
            yaml.dump(config, f, default_flow_style=False)
        elif config_path.suffix == '.json':
            json.dump(config, f, indent=2)
        else:
            raise ValueError(f"Unsupported config format: {config_path.suffix}")
    
    logger.info(f"Configuration saved to {config_path}")

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to readable string.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"

def validate_data_shape(data: np.ndarray, 
                       expected_shape: tuple) -> bool:
    """
    Validate data shape.
    
    Args:
        data: Data array
        expected_shape: Expected shape
    
    Returns:
        True if shape matches
    """
    if len(data.shape) != len(expected_shape):
        return False
    
    for i, dim in enumerate(expected_shape):
        if dim is not None and data.shape[i] != dim:
            return False
    
    return True

def generate_timestamp() -> str:
    """
    Generate current timestamp string.
    
    Returns:
        ISO format timestamp
    """
    return datetime.now().isoformat()

def parse_timestamp(timestamp_str: str) -> datetime:
    """
    Parse timestamp string to datetime.
    
    Args:
        timestamp_str: ISO format timestamp
    
    Returns:
        Datetime object
    """
    return datetime.fromisoformat(timestamp_str)

def find_nearest(array: np.ndarray, value: float) -> int:
    """
    Find index of nearest value in array.
    
    Args:
        array: Array to search
        value: Target value
    
    Returns:
        Index of nearest value
    """
    idx = np.abs(array - value).argmin()
    return idx

class Timer:
    """
    Simple timer for performance measurement.
    """
    
    def __init__(self):
        """Initialize timer."""
        self.start_time = None
        self.end_time = None
    
    def start(self) -> None:
        """Start the timer."""
        self.start_time = time.perf_counter()
        self.end_time = None
    
    def stop(self) -> float:
        """
        Stop the timer.
        
        Returns:
            Elapsed time in milliseconds
        """
        self.end_time = time.perf_counter()
        return self.get_elapsed()
    
    def get_elapsed(self) -> float:
        """
        Get elapsed time.
        
        Returns:
            Elapsed time in milliseconds
        """
        if self.start_time is None:
            return 0.0
        
        end = self.end_time or time.perf_counter()
        return (end - self.start_time) * 1000
    
    def reset(self) -> None:
        """Reset the timer."""
        self.start_time = None
        self.end_time = None

import time  # Import for Timer class
