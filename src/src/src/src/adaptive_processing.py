"""
Adaptive Processing for Artifact Detection
"""

import numpy as np
from scipy import stats
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class AdaptiveArtifactDetector:
    """
    Adaptive artifact detection based on signal statistics.
    """
    
    def __init__(self):
        """Initialize the adaptive detector."""
        self.threshold = None
        self.baseline_stats = None
        self.adaptation_rate = 0.1
        self.window_size = 100
        
    def update_baseline(self, clean_segment: np.ndarray) -> None:
        """
        Update baseline statistics from clean signal.
        
        Args:
            clean_segment: Clean EEG segment
        """
        self.baseline_stats = {
            'mean': np.mean(clean_segment),
            'std': np.std(clean_segment),
            'skew': stats.skew(clean_segment),
            'kurtosis': stats.kurtosis(clean_segment),
            'median': np.median(clean_segment),
            'iqr': stats.iqr(clean_segment)
        }
        
        # Adaptive threshold based on baseline
        self.threshold = self.baseline_stats['mean'] + 3.5 * self.baseline_stats['std']
        
        logger.info("Updated baseline statistics")
        
    def detect_artifacts(self, 
                        new_data: np.ndarray,
                        method: str = 'z_score') -> np.ndarray:
        """
        Detect artifacts in new data.
        
        Args:
            new_data: New EEG data to check
            method: Detection method ('z_score', 'iqr', 'mahalanobis')
        
        Returns:
            Boolean array of artifact detections
        """
        if self.baseline_stats is None:
            logger.warning("No baseline set. Using data statistics.")
            self.update_baseline(new_data[:min(100, len(new_data))])
        
        if method == 'z_score':
            return self._detect_z_score(new_data)
        elif method == 'iqr':
            return self._detect_iqr(new_data)
        elif method == 'mahalanobis':
            return self._detect_mahalanobis(new_data)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _detect_z_score(self, data: np.ndarray) -> np.ndarray:
        """Detect using z-score."""
        z_scores = np.abs((data - self.baseline_stats['mean']) / 
                         self.baseline_stats['std'])
        return z_scores > 3.5
    
    def _detect_iqr(self, data: np.ndarray) -> np.ndarray:
        """Detect using IQR method."""
        lower = self.baseline_stats['median'] - 1.5 * self.baseline_stats['iqr']
        upper = self.baseline_stats['median'] + 1.5 * self.baseline_stats['iqr']
        return (data < lower) | (data > upper)
    
    def _detect_mahalanobis(self, data: np.ndarray) -> np.ndarray:
        """Detect using Mahalanobis distance."""
        # Simplified version
        mean = self.baseline_stats['mean']
        std = self.baseline_stats['std']
        distances = np.abs((data - mean) / std)
        return distances > 4.0
    
    def adapt_threshold(self, 
                        detection_results: np.ndarray,
                        performance_metric: float) -> None:
        """
        Adapt threshold based on detection performance.
        
        Args:
            detection_results: Boolean array of detections
            performance_metric: Detection performance metric (0-1)
        """
        if performance_metric < 0.7:
            # Increase threshold to reduce false positives
            self.threshold *= (1 + self.adaptation_rate)
            logger.debug(f"Increased threshold to {self.threshold:.3f}")
        elif performance_metric > 0.95:
            # Decrease threshold to catch more artifacts
            self.threshold *= (1 - self.adaptation_rate)
            logger.debug(f"Decreased threshold to {self.threshold:.3f}")
