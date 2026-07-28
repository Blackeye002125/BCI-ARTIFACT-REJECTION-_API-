"""
Pytest Configuration and Fixtures
"""

import pytest
import numpy as np
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.main import app
from src.data_loader import EEGDataProcessor
from src.artifact_removal import ArtifactRemovalSystem

@pytest.fixture
def client():
    """
    Test client for API testing.
    """
    return TestClient(app)

@pytest.fixture
def sample_eeg_data():
    """
    Generate sample EEG data for testing.
    """
    np.random.seed(42)
    n_samples = 1000
    n_channels = 4
    
    # Generate clean signal
    t = np.linspace(0, 4, n_samples)
    clean = np.sin(2 * np.pi * 10 * t).reshape(-1, 1)
    clean = np.tile(clean, (1, n_channels))
    
    # Add noise
    noise = np.random.normal(0, 0.1, (n_samples, n_channels))
    
    # Add artifact (eye blink simulation)
    artifact = np.zeros((n_samples, n_channels))
    blink_pos = 200
    artifact[blink_pos:blink_pos+50, :] = np.random.normal(2, 0.5, (50, n_channels))
    
    data = clean + noise + artifact
    
    return data

@pytest.fixture
def sample_channels():
    """
    Sample channel names.
    """
    return ['Fz', 'Cz', 'Pz', 'Oz']

@pytest.fixture
def sample_request_data(sample_eeg_data, sample_channels):
    """
    Sample request data for API tests.
    """
    return {
        "channels": sample_channels,
        "data": sample_eeg_data.tolist(),
        "sampling_rate": 250.0,
        "timestamp": "2024-01-01T12:00:00Z"
    }
