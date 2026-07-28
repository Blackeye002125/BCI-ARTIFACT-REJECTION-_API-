"""
Artifact Removal System using ICA and Machine Learning
"""

import mne
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib
from typing import Optional, List, Tuple
import logging
from mne_icalabel import label_components

logger = logging.getLogger(__name__)

class ArtifactRemovalSystem:
    """
    Removes artifacts from EEG data using ICA and ML classification.
    """
    
    def __init__(self, raw_data: mne.io.Raw):
        """
        Initialize the artifact removal system.
        
        Args:
            raw_data: MNE Raw object with EEG data
        """
        self.raw = raw_data
        self.ica = None
        self.classifier = None
        self.scaler = StandardScaler()
        self.cleaned_data = None
    
    def apply_ica(self, 
                 n_components: int = 20,
                 method: str = 'fastica',
                 random_state: int = 42) -> mne.preprocessing.ICA:
        """
        Apply Independent Component Analysis to separate sources.
        
        Args:
            n_components: Number of ICA components
            method: ICA method ('fastica', 'infomax', 'picard')
            random_state: Random seed for reproducibility
        
        Returns:
            Fitted ICA object
        """
        self.ica = mne.preprocessing.ICA(
            n_components=n_components,
            method=method,
            random_state=random_state,
            max_iter=500
        )
        
        self.ica.fit(self.raw)
        logger.info(f"Applied ICA with {n_components} components")
        
        # Visualize components
        self.ica.plot_components(picks=range(min(10, n_components)))
        
        return self.ica
    
    def auto_detect_artifacts(self) -> List[int]:
        """
        Automatically detect artifact components using AI.
        
        Returns:
            List of component indices that are artifacts
        """
        if self.ica is None:
            raise ValueError("ICA not applied. Call apply_ica() first.")
        
        # Use mne-icalabel for automatic labeling
        ic_labels = label_components(self.raw, self.ica, method='iclabel')
        
        artifact_components = []
        for idx, label in enumerate(ic_labels['labels']):
            if label in ['eye blink', 'muscle artifact', 'heart beat']:
                artifact_components.append(idx)
                logger.info(f"Component {idx}: {label} - Artifact detected")
            else:
                logger.debug(f"Component {idx}: {label} - Clean signal")
        
        return artifact_components
    
    def train_ml_classifier(self, 
                           data: np.ndarray, 
                           labels: np.ndarray) -> Pipeline:
        """
        Train a machine learning classifier for artifact detection.
        
        Args:
            data: Feature matrix
            labels: Target labels (0=clean, 1=artifact)
        
        Returns:
            Trained pipeline
        """
        features = self.extract_features(data)
        
        self.classifier = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ))
        ])
        
        self.classifier.fit(features, labels)
        logger.info(f"Trained classifier with {len(features)} samples")
        
        return self.classifier
    
    def extract_features(self, data: np.ndarray) -> np.ndarray:
        """
        Extract statistical features from EEG data.
        
        Args:
            data: EEG data array
        
        Returns:
            Feature matrix
        """
        features = []
        
        for channel in data:
            # Statistical features
            mean = np.mean(channel)
            std = np.std(channel)
            rms = np.sqrt(np.mean(channel**2))
            
            # Frequency features
            fft = np.fft.fft(channel)
            power = np.abs(fft)**2
            
            # Peak features
            peaks = len(mne.preprocessing.find_peaks(
                channel, 
                threshold=3*std
            )[0])
            
            features.append([
                mean,
                std,
                rms,
                np.max(power),
                np.min(power),
                np.mean(power),
                peaks
            ])
        
        return np.array(features)
    
    def remove_artifacts(self, 
                        artifact_indices: Optional[List[int]] = None) -> mne.io.Raw:
        """
        Remove artifact components and reconstruct clean signal.
        
        Args:
            artifact_indices: List of component indices to remove
        
        Returns:
            Cleaned MNE Raw object
        """
        if self.ica is None:
            raise ValueError("ICA not applied. Call apply_ica() first.")
        
        if artifact_indices is None:
            artifact_indices = self.auto_detect_artifacts()
        
        # Apply ICA to remove artifacts
        self.cleaned_data = self.ica.apply(
            self.raw.copy(), 
            exclude=artifact_indices
        )
        
        # Calculate SNR improvement
        original_power = np.mean(self.raw.get_data()**2)
        cleaned_power = np.mean(self.cleaned_data.get_data()**2)
        snr_improvement = 10 * np.log10(cleaned_power / original_power)
        
        logger.info(f"Removed {len(artifact_indices)} artifact components")
        logger.info(f"SNR improvement: {snr_improvement:.2f} dB")
        
        return self.cleaned_data
    
    def save_model(self, path: str = 'models/artifact_model.joblib') -> None:
        """
        Save the trained model to disk.
        
        Args:
            path: Path to save the model
        """
        if self.classifier:
            joblib.dump(self.classifier, path)
            logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str = 'models/artifact_model.joblib') -> None:
        """
        Load a trained model from disk.
        
        Args:
            path: Path to the saved model
        """
        self.classifier = joblib.load(path)
        logger.info(f"Model loaded from {path}")
