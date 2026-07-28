"""
Unit tests for data loader module.
"""

import pytest
import numpy as np
from pathlib import Path
from src.data_loader import EEGDataProcessor

def test_initialization():
    """Test processor initialization."""
    processor = EEGDataProcessor("test.edf")
    assert processor.file_path == Path("test.edf")
    assert processor.raw is None

def test_load_data_unsupported_format():
    """Test loading unsupported format."""
    processor = EEGDataProcessor("test.txt")
    with pytest.raises(ValueError):
        processor.load_data()

def test_filter_without_data():
    """Test applying filters without data loaded."""
    processor = EEGDataProcessor("test.edf")
    with pytest.raises(ValueError):
        processor.apply_filters()

# Additional tests would require actual EEG data files
# These are placeholders for the structure
