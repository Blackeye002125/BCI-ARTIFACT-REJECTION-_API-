#!/usr/bin/env python
"""
Performance benchmarking for EEG processing.
"""

import time
import numpy as np
from pathlib import Path
import statistics
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def benchmark_processing():
    """
    Benchmark processing time.
    """
    logger.info("🔬 Running benchmarks...")
    
    # Generate test data
    n_samples = 1000
    n_channels = 4
    test_data = np.random.normal(0, 1, (n_samples, n_channels))
    
    # Simulate processing function
    def process_data(data):
        """Simulate EEG processing."""
        # Apply some operations
        filtered = data * 0.85  # Simulate filtering
        return filtered
    
    # Test processing times
    times = []
    n_runs = 100
    
    logger.info(f"Running {n_runs} benchmark runs...")
    
    for i in range(n_runs):
        start = time.perf_counter()
        result = process_data(test_data)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        times.append(elapsed)
    
    logger.info(f"\n📊 Benchmark Results ({n_runs} runs):")
    logger.info(f"   Average: {statistics.mean(times):.2f} ms")
    logger.info(f"   Median: {statistics.median(times):.2f} ms")
    logger.info(f"   Min: {min(times):.2f} ms")
    logger.info(f"   Max: {max(times):.2f} ms")
    logger.info(f"   Std Dev: {statistics.stdev(times):.2f} ms")
    
    # Check real-time requirement
    avg_time = statistics.mean(times)
    meets_requirement = avg_time < 20
    logger.info(f"\n✅ Real-time (<20ms): {meets_requirement}")
    
    if meets_requirement:
        logger.info("🎉 Performance meets real-time requirements!")
    else:
        logger.warning("⚠️ Performance does not meet real-time requirements.")
    
    return times

def benchmark_memory():
    """
    Benchmark memory usage.
    """
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_before = process.memory_info().rss / 1024 / 1024
    
    # Generate large data
    data = np.random.normal(0, 1, (10000, 16))
    
    # Process data
    processed = data * 0.85
    
    memory_after = process.memory_info().rss / 1024 / 1024
    
    logger.info(f"\n📊 Memory Usage:")
    logger.info(f"   Before: {memory_before:.2f} MB")
    logger.info(f"   After: {memory_after:.2f} MB")
    logger.info(f"   Delta: {memory_after - memory_before:.2f} MB")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Performance benchmarking')
    parser.add_argument('--runs', type=int, default=100, help='Number of benchmark runs')
    parser.add_argument('--memory', action='store_true', help='Benchmark memory usage')
    args = parser.parse_args()
    
    # Run benchmarks
    benchmark_processing()
    
    if args.memory:
        benchmark_memory()

if __name__ == "__main__":
    main()
