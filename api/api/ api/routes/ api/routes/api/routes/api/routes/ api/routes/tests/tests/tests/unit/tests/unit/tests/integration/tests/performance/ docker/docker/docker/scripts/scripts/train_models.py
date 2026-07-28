#!/usr/bin/env python
"""
Train machine learning models for artifact detection.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
from pathlib import Path
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_synthetic_data(n_samples=10000, n_features=10):
    """
    Generate synthetic training data.
    
    Args:
        n_samples: Number of samples per class
        n_features: Number of features
    
    Returns:
        Features and labels
    """
    np.random.seed(42)
    
    # Clean EEG features (class 0)
    clean = np.random.normal(0, 1, (n_samples, n_features))
    
    # Artifact features (class 1)
    artifact = np.random.normal(2, 3, (n_samples, n_features))
    
    # Combine
    X = np.vstack([clean, artifact])
    y = np.array([0]*n_samples + [1]*n_samples)
    
    # Shuffle
    indices = np.random.permutation(len(X))
    X = X[indices]
    y = y[indices]
    
    return X, y

def train_models():
    """
    Train and save multiple models.
    """
    logger.info("🧠 Generating synthetic training data...")
    X, y = generate_synthetic_data(n_samples=10000, n_features=10)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    logger.info(f"Training data: {len(X_train)} samples")
    logger.info(f"Test data: {len(X_test)} samples")
    
    # Train Random Forest
    logger.info("🌲 Training Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_accuracy = accuracy_score(y_test, rf_pred)
    logger.info(f"   RF Accuracy: {rf_accuracy:.3f}")
    
    # Train SVM
    logger.info("📐 Training SVM...")
    svm = SVC(
        kernel='rbf',
        C=1.0,
        gamma='scale',
        probability=True,
        random_state=42
    )
    svm.fit(X_train, y_train)
    svm_pred = svm.predict(X_test)
    svm_accuracy = accuracy_score(y_test, svm_pred)
    logger.info(f"   SVM Accuracy: {svm_accuracy:.3f}")
    
    # Train Lightweight model (Decision Tree)
    logger.info("🌳 Training Lightweight Model...")
    from sklearn.tree import DecisionTreeClassifier
    dt = DecisionTreeClassifier(
        max_depth=5,
        random_state=42
    )
    dt.fit(X_train, y_train)
    dt_pred = dt.predict(X_test)
    dt_accuracy = accuracy_score(y_test, dt_pred)
    logger.info(f"   DT Accuracy: {dt_accuracy:.3f}")
    
    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Save models
    joblib.dump(rf, models_dir / "artifact_model_rf.joblib")
    joblib.dump(svm, models_dir / "artifact_model_svm.joblib")
    joblib.dump(dt, models_dir / "lightweight_model.joblib")
    
    logger.info("✅ All models saved to 'models/' directory")
    
    # Generate classification reports
    logger.info("\n📊 Classification Reports:")
    logger.info("\nRandom Forest:\n" + classification_report(y_test, rf_pred))
    logger.info("\nSVM:\n" + classification_report(y_test, svm_pred))
    logger.info("\nDecision Tree:\n" + classification_report(y_test, dt_pred))
    
    return rf, svm, dt

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Train artifact detection models')
    parser.add_argument('--no-save', action='store_true', help='Don\'t save models')
    args = parser.parse_args()
    
    train_models()

if __name__ == "__main__":
    main()
