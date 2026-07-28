"""
Advanced Feature Extraction for EEG Signals
"""

import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
from scipy.stats import entropy
from typing import Dict, List, Tuple
import pyriemann
from sklearn.decomposition import PCA
import logging

logger = logging.getLogger(__name__)

class FeatureExtractor:
    """
    Extract features from EEG signals for artifact detection.
    """
    
    def __init__(self):
        """Initialize the feature extractor."""
        self.feature_names = []
        self.pca = None
        
    def extract_all_features(self, data: np.ndarray, 
                             sampling_rate: float) -> Dict[str, np.ndarray]:
        """
        Extract all available features.
        
        Args:
            data: EEG data (channels x samples)
            sampling_rate: Sampling rate in Hz
        
        Returns:
            Dictionary of feature names and values
        """
        features = {}
        
        # Time domain features
        features.update(self.time_domain_features(data))
        
        # Frequency domain features
        features.update(self.frequency_domain_features(data, sampling_rate))
        
        # Statistical features
        features.update(self.statistical_features(data))
        
        # Entropy features
        features.update(self.entropy_features(data))
        
        self.feature_names = list(features.keys())
        return features
    
    def time_domain_features(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Extract time domain features.
        
        Args:
            data: EEG data
        
        Returns:
            Dictionary of time domain features
        """
        features = {}
        
        # Mean absolute value
        features['mean_abs'] = np.mean(np.abs(data), axis=1)
        
        # RMS value
        features['rms'] = np.sqrt(np.mean(data**2, axis=1))
        
        # Peak-to-peak amplitude
        features['peak_peak'] = np.max(data, axis=1) - np.min(data, axis=1)
        
        # Zero crossing rate
        features['zero_crossing'] = np.sum(np.diff(np.sign(data)) != 0, axis=1)
        
        # Hjorth parameters
        features.update(self.hjorth_parameters(data))
        
        return features
    
    def hjorth_parameters(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Calculate Hjorth parameters.
        
        Args:
            data: EEG data
        
        Returns:
            Hjorth features
        """
        features = {}
        
        for i, channel in enumerate(data):
            # Activity (variance)
            activity = np.var(channel)
            
            # Mobility (sqrt of variance of derivative / variance)
            diff = np.diff(channel)
            if activity > 0:
                mobility = np.sqrt(np.var(diff) / activity)
            else:
                mobility = 0
            
            # Complexity (mobility of derivative / mobility)
            diff2 = np.diff(diff)
            if mobility > 0:
                complexity = np.sqrt(np.var(diff2) / np.var(diff)) / mobility
            else:
                complexity = 0
            
            features[f'activity_{i}'] = np.array([activity])
            features[f'mobility_{i}'] = np.array([mobility])
            features[f'complexity_{i}'] = np.array([complexity])
        
        return features
    
    def frequency_domain_features(self, 
                                  data: np.ndarray,
                                  sampling_rate: float) -> Dict[str, np.ndarray]:
        """
        Extract frequency domain features.
        
        Args:
            data: EEG data
            sampling_rate: Sampling rate in Hz
        
        Returns:
            Frequency domain features
        """
        features = {}
        
        # Define frequency bands
        bands = {
            'delta': (0.5, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 50)
        }
        
        for channel in data:
            # Compute power spectral density
            freqs, psd = signal.welch(channel, sampling_rate, nperseg=256)
            
            # Power in each frequency band
            for band_name, (low, high) in bands.items():
                idx = np.where((freqs >= low) & (freqs < high))[0]
                if len(idx) > 0:
                    power = np.trapz(psd[idx], freqs[idx])
                    features[f'{band_name}_power'] = np.array([power])
            
            # Total power
            features['total_power'] = np.array([np.trapz(psd, freqs)])
            
            # Spectral entropy
            psd_norm = psd / np.sum(psd)
            features['spectral_entropy'] = np.array([entropy(psd_norm)])
        
        return features
    
    def statistical_features(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Extract statistical features.
        
        Args:
            data: EEG data
        
        Returns:
            Statistical features
        """
        features = {}
        
        features['mean'] = np.mean(data, axis=1)
        features['std'] = np.std(data, axis=1)
        features['var'] = np.var(data, axis=1)
        features['skew'] = stats.skew(data, axis=1)
        features['kurtosis'] = stats.kurtosis(data, axis=1)
        features['median'] = np.median(data, axis=1)
        
        return features
    
    def entropy_features(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Extract entropy-based features.
        
        Args:
            data: EEG data
        
        Returns:
            Entropy features
        """
        features = {}
        
        # Approximate entropy
        features['approx_entropy'] = np.array([
            self._approx_entropy(channel) for channel in data
        ])
        
        # Sample entropy
        features['sample_entropy'] = np.array([
            self._sample_entropy(channel) for channel in data
        ])
        
        return features
    
    def _approx_entropy(self, data: np.ndarray, m: int = 2, r: float = 0.2) -> float:
        """
        Calculate approximate entropy.
        
        Args:
            data: Signal data
            m: Embedding dimension
            r: Tolerance
        
        Returns:
            Approximate entropy value
        """
        # Simplified implementation
        N = len(data)
        r *= np.std(data)
        
        # Create delay vectors
        def _create_vectors(data, m):
            vectors = []
            for i in range(N - m + 1):
                vectors.append(data[i:i+m])
            return np.array(vectors)
        
        # Calculate correlation
        def _correlation_sum(vectors, r):
            count = 0
            for i in range(len(vectors)):
                for j in range(len(vectors)):
                    if i != j:
                        if np.max(np.abs(vectors[i] - vectors[j])) <= r:
                            count += 1
            return count / (len(vectors) * (len(vectors) - 1))
        
        vectors_m = _create_vectors(data, m)
        vectors_m1 = _create_vectors(data, m + 1)
        
        C_m = _correlation_sum(vectors_m, r)
        C_m1 = _correlation_sum(vectors_m1, r)
        
        if C_m > 0 and C_m1 > 0:
            return np.log(C_m / C_m1)
        else:
            return 0
    
    def _sample_entropy(self, data: np.ndarray, m: int = 2, r: float = 0.2) -> float:
        """
        Calculate sample entropy.
        
        Args:
            data: Signal data
            m: Embedding dimension
            r: Tolerance
        
        Returns:
            Sample entropy value
        """
        # Simplified implementation
        N = len(data)
        r *= np.std(data)
        
        def _count_matches(data, m, r):
            count = 0
            for i in range(N - m):
                for j in range(i + 1, N - m):
                    if np.max(np.abs(data[i:i+m] - data[j:j+m])) <= r:
                        count += 1
            return count
        
        A = _count_matches(data, m + 1, r)
        B = _count_matches(data, m, r)
        
        if B > 0 and A > 0:
            return -np.log(A / B)
        else:
            return 0
    
    def reduce_dimensions(self, features: np.ndarray, 
                          n_components: int = 10) -> np.ndarray:
        """
        Reduce feature dimensions using PCA.
        
        Args:
            features: Feature matrix
            n_components: Number of components
        
        Returns:
            Reduced features
        """
        if self.pca is None:
            self.pca = PCA(n_components=n_components)
            reduced = self.pca.fit_transform(features)
        else:
            reduced = self.pca.transform(features)
        
        return reduced
