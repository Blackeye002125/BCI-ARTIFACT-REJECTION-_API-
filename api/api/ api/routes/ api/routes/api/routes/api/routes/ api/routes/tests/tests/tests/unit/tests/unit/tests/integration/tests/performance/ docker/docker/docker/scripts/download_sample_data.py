#!/usr/bin/env python
"""
Download sample EEG data from PhysioNet.
"""

import os
import requests
from pathlib import Path
import mne
import argparse
from tqdm import tqdm

def download_sample_data():
    """Download sample EEG data from PhysioNet."""
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Download sample file
    url = "https://www.physionet.org/files/eegmmidb/1.0.0/S001/S001R01.edf"
    file_path = data_dir / "sample.edf"
    
    if file_path.exists():
        print("✅ Data already exists!")
        return load_data(file_path)
    
    print("📥 Downloading sample EEG data...")
    
    # Download with progress bar
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(file_path, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                pbar.update(len(chunk))
    
    print("✅ Download complete!")
    return load_data(file_path)

def load_data(file_path):
    """Load and display EEG data info."""
    raw = mne.io.read_raw_edf(file_path, preload=True)
    
    print(f"\n📊 EEG Data Info:")
    print(f"   Channels: {len(raw.ch_names)}")
    print(f"   Duration: {raw.n_times / raw.info['sfreq']:.1f} seconds")
    print(f"   Sampling Rate: {raw.info['sfreq']} Hz")
    print(f"   Channel Names: {', '.join(raw.ch_names[:10])}{'...' if len(raw.ch_names) > 10 else ''}")
    
    return raw

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download sample EEG data')
    parser.add_argument('--force', action='store_true', help='Force re-download')
    args = parser.parse_args()
    
    download_sample_data()
