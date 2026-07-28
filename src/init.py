"""
BCI Artifact Rejection - Core Processing Module
"""

from .data_loader import EEGDataProcessor
from .artifact_removal import ArtifactRemovalSystem
from .deep_learning import EEGAutoencoder
from .adaptive_processing import AdaptiveArtifactDetector
from .feature_extraction import FeatureExtractor
from .utils import load_config, setup_logging

__all__ = [
    'EEGDataProcessor',
    'ArtifactRemovalSystem',
    'EEGAutoencoder',
    'AdaptiveArtifactDetector',
    'FeatureExtractor',
    'load_config',
    'setup_logging'
]

__version__ = '2.0.0'
