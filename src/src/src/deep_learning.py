"""
Deep Learning Autoencoder for Artifact Removal
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class EEGAutoencoder:
    """
    Deep learning autoencoder for artifact removal.
    """
    
    def __init__(self, input_dim: int, latent_dim: int = 16):
        """
        Initialize the autoencoder.
        
        Args:
            input_dim: Input dimension (number of features)
            latent_dim: Latent space dimension
        """
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.model = None
        self.encoder = None
        self.decoder = None
        
    def build_model(self) -> keras.Model:
        """
        Build the autoencoder architecture.
        
        Returns:
            Compiled Keras model
        """
        # Encoder
        encoder_input = keras.Input(shape=(self.input_dim,))
        x = keras.layers.Dense(128, activation='relu')(encoder_input)
        x = keras.layers.Dropout(0.2)(x)
        x = keras.layers.Dense(64, activation='relu')(x)
        x = keras.layers.Dense(32, activation='relu')(x)
        encoded = keras.layers.Dense(self.latent_dim, activation='relu')(x)
        
        # Decoder
        x = keras.layers.Dense(32, activation='relu')(encoded)
        x = keras.layers.Dense(64, activation='relu')(x)
        x = keras.layers.Dense(128, activation='relu')(x)
        decoded = keras.layers.Dense(self.input_dim, activation='linear')(x)
        
        # Full model
        autoencoder = keras.Model(encoder_input, decoded)
        autoencoder.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        # Separate encoder and decoder
        self.encoder = keras.Model(encoder_input, encoded)
        
        encoded_input = keras.Input(shape=(self.latent_dim,))
        decoder_layer = autoencoder.layers[-1]
        self.decoder = keras.Model(encoded_input, decoder_layer(encoded_input))
        
        self.model = autoencoder
        logger.info(f"Built autoencoder with latent_dim={self.latent_dim}")
        
        return self.model
    
    def train(self,
             clean_data: np.ndarray,
             epochs: int = 50,
             batch_size: int = 32,
             validation_split: float = 0.2,
             add_noise: bool = True) -> keras.callbacks.History:
        """
        Train the autoencoder on clean data with added noise.
        
        Args:
            clean_data: Clean EEG data
            epochs: Number of training epochs
            batch_size: Batch size
            validation_split: Fraction for validation
            add_noise: Whether to add synthetic noise
        
        Returns:
            Training history
        """
        if self.model is None:
            self.build_model()
        
        # Add noise for self-supervised learning
        if add_noise:
            noise = np.random.normal(0, 0.1, clean_data.shape)
            noisy_data = clean_data + noise
        else:
            noisy_data = clean_data
        
        # Train the model
        history = self.model.fit(
            noisy_data,
            clean_data,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=1,
            callbacks=[
                keras.callbacks.EarlyStopping(
                    patience=10,
                    restore_best_weights=True
                ),
                keras.callbacks.ReduceLROnPlateau(
                    factor=0.5,
                    patience=5
                )
            ]
        )
        
        logger.info(f"Training completed: {len(history.history['loss'])} epochs")
        return history
    
    def remove_artifacts(self, noisy_data: np.ndarray) -> np.ndarray:
        """
        Remove artifacts using the trained autoencoder.
        
        Args:
            noisy_data: EEG data with artifacts
        
        Returns:
            Cleaned EEG data
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        cleaned = self.model.predict(noisy_data, verbose=0)
        logger.info(f"Cleaned {len(noisy_data)} samples")
        
        return cleaned
    
    def save_model(self, path: str = 'models/autoencoder.h5') -> None:
        """
        Save the trained model.
        
        Args:
            path: Path to save the model
        """
        if self.model is None:
            raise ValueError("No model to save")
        
        self.model.save(path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str = 'models/autoencoder.h5') -> None:
        """
        Load a trained model.
        
        Args:
            path: Path to the saved model
        """
        self.model = keras.models.load_model(path)
        
        # Rebuild encoder and decoder
        self.encoder = keras.Model(
            self.model.input,
            self.model.layers[-3].output
        )
        self.decoder = keras.Model(
            keras.Input(shape=(self.latent_dim,)),
            self.model.layers[-1].output
        )
        
        logger.info(f"Model loaded from {path}")
