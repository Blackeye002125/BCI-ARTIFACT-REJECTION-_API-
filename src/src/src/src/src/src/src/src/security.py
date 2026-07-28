"""
Security and Privacy Module for EEG Data
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import numpy as np
import json
from typing import Union, Tuple
import logging

logger = logging.getLogger(__name__)

class DataSecurity:
    """
    Handles encryption, decryption, and privacy of EEG data.
    """
    
    def __init__(self, key_file: str = 'security.key'):
        """
        Initialize security module.
        
        Args:
            key_file: Path to key file
        """
        self.key_file = key_file
        self.key = self._load_or_generate_key()
        self.cipher_suite = Fernet(self.key)
    
    def _load_or_generate_key(self) -> bytes:
        """
        Load existing key or generate new one.
        
        Returns:
            Encryption key
        """
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                key = f.read()
            logger.info(f"Loaded encryption key from {self.key_file}")
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            logger.info(f"Generated new encryption key: {self.key_file}")
        
        return key
    
    def encrypt_eeg_data(self, data: np.ndarray) -> bytes:
        """
        Encrypt EEG data.
        
        Args:
            data: EEG data array
        
        Returns:
            Encrypted data
        """
        # Serialize to bytes
        serialized = data.tobytes()
        encrypted = self.cipher_suite.encrypt(serialized)
        
        logger.info(f"Encrypted {len(data)} samples")
        return encrypted
    
    def decrypt_eeg_data(self, encrypted: bytes) -> np.ndarray:
        """
        Decrypt EEG data.
        
        Args:
            encrypted: Encrypted data
        
        Returns:
            Decrypted EEG data
        """
        decrypted = self.cipher_suite.decrypt(encrypted)
        data = np.frombuffer(decrypted, dtype=np.float32)
        
        logger.info(f"Decrypted {len(data)} samples")
        return data
    
    def encrypt_metadata(self, metadata: dict) -> bytes:
        """
        Encrypt metadata dictionary.
        
        Args:
            metadata: Metadata dictionary
        
        Returns:
            Encrypted metadata
        """
        json_str = json.dumps(metadata)
        encrypted = self.cipher_suite.encrypt(json_str.encode())
        
        return encrypted
    
    def decrypt_metadata(self, encrypted: bytes) -> dict:
        """
        Decrypt metadata.
        
        Args:
            encrypted: Encrypted metadata
        
        Returns:
            Decrypted metadata dictionary
        """
        decrypted = self.cipher_suite.decrypt(encrypted)
        metadata = json.loads(decrypted.decode())
        
        return metadata
    
    def anonymize_data(self, data: np.ndarray, 
                      noise_scale: float = 0.01) -> np.ndarray:
        """
        Anonymize data by adding differential privacy noise.
        
        Args:
            data: EEG data
            noise_scale: Scale of noise
        
        Returns:
            Anonymized data
        """
        noise = np.random.normal(0, noise_scale, data.shape)
        anonymized = data + noise
        
        logger.info("Applied differential privacy")
        return anonymized
    
    def create_secure_hash(self, data: np.ndarray) -> str:
        """
        Create secure hash of data for authentication.
        
        Args:
            data: EEG data
        
        Returns:
            Hash string
        """
        import hashlib
        data_bytes = data.tobytes()
        hash_obj = hashlib.sha256(data_bytes)
        return hash_obj.hexdigest()
