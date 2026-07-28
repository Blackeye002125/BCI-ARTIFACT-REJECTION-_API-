"""
Unit tests for artifact removal module.
"""

import pytest
import numpy as np
from src.artifact_removal import ArtifactRemovalSystem

def test_extract_features():
    """Test feature extraction."""
    data = np.random.normal(0, 1, (4, 100))
    system = ArtifactRemovalSystem(None)
    features = system.extract_features(data)
    
    assert features.shape[0] == 4
    assert features.shape[1] == 7  # 7 features per channel

def test_train_classifier():
    """Test classifier training."""
    system = ArtifactRemovalSystem(None)
    data = np.random.normal(0, 1, (100, 10))
    labels = np.random.randint(0, 2, 100)
    
    classifier = system.train_ml_classifier(data, labels)
    assert classifier is not None
