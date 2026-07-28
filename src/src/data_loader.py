"""
EEG Data Loading and Preprocessing Module
"""

import mne
import numpy as np
from pathlib import Path
from typing import Optional, Union, List
import logging

logger = logging.getLogger(__name__)

class EEGDataProcessor:
    """
    Handles loading, filtering, and preprocessing of EEG data.
    """
    
    def __init__(self, file_path: Union[str, Path]):
        """
        Initialize the EEG data processor.
        
        Args:
            file_path: Path to the EEG data file
        """
        self.file_path = Path(file_path)
        self.raw = None
        self.cleaned = None
        self.info = {}
    
    def load_data(self) -> mne.io.Raw:
        """
        Load EEG data from various file formats.
        
        Returns:
            MNE Raw object with loaded data
        """
        if self.file_path.suffix in ['.edf', '.bdf']:
            self.raw = mne.io.read_raw_edf(self.file_path, preload=True)
        elif self.file_path.suffix == '.fif':
            self.raw = mne.io.read_raw_fif(self.file_path, preload=True)
        elif self.file_path.suffix in ['.gdf', '.gdf2']:
            self.raw = mne.io.read_raw_gdf(self.file_path, preload=True)
        else:
            raise ValueError(f"Unsupported file format: {self.file_path.suffix}")
        
        # Set channel types if not present
        if not self.raw.ch_names:
            self.raw.set_channel_types({
                'EEG': 'eeg',
                'EOG': 'eog',
                'EMG': 'emg',
                'ECG': 'ecg'
            })
        
        logger.info(f"Loaded EEG data: {len(self.raw.ch_names)} channels, "
                   f"{self.raw.n_times / self.raw.info['sfreq']:.1f} seconds")
        
        self.info = {
            'channels': len(self.raw.ch_names),
            'duration': self.raw.n_times / self.raw.info['sfreq'],
            'sampling_rate': self.raw.info['sfreq']
        }
        
        return self.raw
    
    def apply_filters(self, 
                     l_freq: float = 1.0,
                     h_freq: float = 40.0,
                     notch_freq: Optional[float] = 50.0) -> mne.io.Raw:
        """
        Apply band-pass and notch filters to remove noise.
        
        Args:
            l_freq: Low cutoff frequency (Hz)
            h_freq: High cutoff frequency (Hz)
            notch_freq: Notch filter frequency (Hz) for power line noise
        
        Returns:
            Filtered MNE Raw object
        """
        if self.raw is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        # Band-pass filter
        self.raw.filter(l_freq, h_freq, fir_design='firwin')
        logger.info(f"Applied band-pass filter: {l_freq}-{h_freq} Hz")
        
        # Notch filter
        if notch_freq:
            self.raw.notch_filter(notch_freq, fir_design='firwin', picks='eeg')
            logger.info(f"Applied notch filter: {notch_freq} Hz")
        
        # Remove DC offset
        self.raw.apply_function(
            lambda x: x - np.mean(x, axis=1, keepdims=True),
            picks='eeg',
            channel_wise=True
        )
        
        return self.raw
    
    def detect_bad_channels(self, threshold: float = 0.85) -> List[str]:
        """
        Detect channels with poor signal quality using correlation.
        
        Args:
            threshold: Correlation threshold for detecting bad channels
        
        Returns:
            List of bad channel names
        """
        if self.raw is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        data = self.raw.get_data(picks='eeg')
        corr_matrix = np.corrcoef(data)
        mean_corr = np.mean(corr_matrix, axis=0)
        
        bad_channels = []
        for i, ch_name in enumerate(self.raw.ch_names):
            if mean_corr[i] < threshold:
                bad_channels.append(ch_name)
                logger.warning(f"Channel '{ch_name}' may be bad "
                             f"(correlation: {mean_corr[i]:.3f})")
        
        if bad_channels:
            self.raw.info['bads'] = bad_channels
            self.raw.interpolate_bads(reset_bads=True)
        
        return bad_channels
    
    def visualize(self, duration: int = 10, start: int = 0) -> None:
        """
        Visualize the EEG data.
        
        Args:
            duration: Duration to display (seconds)
            start: Start time (seconds)
        """
        if self.raw is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.raw.plot(n_channels=20, duration=duration, start=start,
                     scalings='auto', title='EEG Data')
        
        # Plot power spectral density
        self.raw.plot_psd(fmax=50, average=True)
