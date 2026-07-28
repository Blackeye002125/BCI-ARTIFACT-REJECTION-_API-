"""
Performance Optimization for EEG Processing
"""

import numpy as np
from functools import lru_cache
import hashlib
import time
from typing import Any, Dict, Optional, Tuple
import threading
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """
    Optimizes performance through caching, batching, and quantization.
    """
    
    def __init__(self, max_cache_size: int = 100):
        """
        Initialize the optimizer.
        
        Args:
            max_cache_size: Maximum number of items in cache
        """
        self.cache = OrderedDict()
        self.max_cache_size = max_cache_size
        self.cache_lock = threading.Lock()
        self.batch_size = 32
        
    @lru_cache(maxsize=128)
    def cached_processing(self, data_hash: str) -> Optional[np.ndarray]:
        """
        Check if processed data exists in cache.
        
        Args:
            data_hash: Hash of input data
        
        Returns:
            Cached result or None
        """
        with self.cache_lock:
            if data_hash in self.cache:
                return self.cache[data_hash]
        return None
    
    def cache_result(self, data_hash: str, result: np.ndarray) -> None:
        """
        Cache processed result.
        
        Args:
            data_hash: Hash of input data
            result: Processed result
        """
        with self.cache_lock:
            self.cache[data_hash] = result
            if len(self.cache) > self.max_cache_size:
                # Remove oldest item
                self.cache.popitem(last=False)
    
    def compute_data_hash(self, data: np.ndarray) -> str:
        """
        Compute hash of input data for caching.
        
        Args:
            data: Input data array
        
        Returns:
            Hash string
        """
        # Convert to bytes and hash
        data_bytes = data.tobytes()
        return hashlib.md5(data_bytes).hexdigest()
    
    def dynamic_batching(self, 
                        data: np.ndarray,
                        min_batch: int = 16,
                        max_batch: int = 256) -> int:
        """
        Determine optimal batch size based on data length.
        
        Args:
            data: Input data
            min_batch: Minimum batch size
            max_batch: Maximum batch size
        
        Returns:
            Optimal batch size
        """
        data_length = len(data)
        
        if data_length < 100:
            batch_size = min_batch
        elif data_length < 1000:
            batch_size = 64
        elif data_length < 10000:
            batch_size = 128
        else:
            batch_size = max_batch
        
        self.batch_size = batch_size
        return batch_size
    
    def process_in_batches(self, 
                          data: np.ndarray,
                          process_func: callable,
                          batch_size: Optional[int] = None) -> np.ndarray:
        """
        Process data in batches to manage memory.
        
        Args:
            data: Input data
            process_func: Function to process each batch
            batch_size: Optional custom batch size
        
        Returns:
            Processed results
        """
        if batch_size is None:
            batch_size = self.batch_size
        
        results = []
        n_batches = int(np.ceil(len(data) / batch_size))
        
        logger.info(f"Processing {len(data)} items in {n_batches} batches")
        
        for i in range(n_batches):
            start = i * batch_size
            end = min((i + 1) * batch_size, len(data))
            batch = data[start:end]
            
            # Process batch
            start_time = time.perf_counter()
            result = process_func(batch)
            process_time = (time.perf_counter() - start_time) * 1000
            
            results.append(result)
            
            if i % 10 == 0:
                logger.debug(f"Batch {i+1}/{n_batches} completed in {process_time:.2f}ms")
        
        return np.vstack(results) if results else np.array([])
    
    def quantize_model(self, model, bits: int = 8) -> Any:
        """
        Quantize model for faster inference.
        
        Args:
            model: Trained model
            bits: Quantization bits (8 or 16)
        
        Returns:
            Quantized model
        """
        # Placeholder - actual implementation depends on the model type
        logger.info(f"Quantizing model to {bits}-bit")
        return model
    
    def profile_performance(self, 
                           func: callable,
                           *args, 
                           **kwargs) -> Tuple[Any, float]:
        """
        Profile function performance.
        
        Args:
            func: Function to profile
            *args: Function arguments
            **kwargs: Function keyword arguments
        
        Returns:
            (Result, execution_time_in_ms)
        """
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        execution_time = (time.perf_counter() - start_time) * 1000
        
        return result, execution_time
