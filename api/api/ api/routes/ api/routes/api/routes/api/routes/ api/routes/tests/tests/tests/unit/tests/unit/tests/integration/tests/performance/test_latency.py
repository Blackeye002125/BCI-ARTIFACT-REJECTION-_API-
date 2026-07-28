"""
Performance tests for latency.
"""

import pytest
import time
import numpy as np
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

@pytest.mark.performance
def test_processing_latency(sample_request_data):
    """
    Test that processing latency is under 20
