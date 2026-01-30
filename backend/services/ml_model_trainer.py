"""
ML Model Trainer for Issue Prediction
Trains scikit-learn models using collected ML training data.
Provides both offline training and real-time prediction capabilities.
"""
import asyncio
import logging
import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import pickle
import hashlib

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, f1_score
import joblib

from utils.database import db

logger = logging.getLogger(__name__)

# Model storage path
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'ml_models')
os.makedirs(MODEL_DIR, exist_ok=True)


@dataclass
class ModelMetrics:
    accuracy: float
    f1_score: float
    training_samples: int
    feature_count: int
    trained_at: str
    model_version: str


class IssuePredictor:
    """
    Machine Learning model for predicting system issues.
    Uses Random Forest and Gradient Boosting ensemble.
    """
    
    MODEL_VERSION = "1.0.0"
    
    def __init__(self):
        self.rf_model: Optional[RandomForestClassifier] = None
        self.gb_model: Optional[GradientBoostingClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.label_encoder: Optional[LabelEncoder] = None
        self.feature_columns: List[str] = []
        self.metrics: Optional[ModelMetrics] = None
        self.is_trained = False
        
        # Try to load existing model
        self._load_model()
    
    def _get_model_path(self, name: str) -> str:
        return os.path.join(MODEL_DIR, f"{name}.joblib")
    
    def _load_model(self) -> bool:
        """Load trained model from disk"""
        try:
            rf_path = self._get_model_path("rf_model")
            gb_path = self._get_model_path("gb_model")
            scaler_path = self._get_model_path("scaler")
            le_path = self._get_model_path("label_encoder")
            meta_path = self._get_model_path("metadata")
            
            if all(os.path.exists(p) for p in [rf_path, gb_path, scaler_path, le_path, meta_path]):
                self.rf_model = joblib.load(rf_path)
                self.gb_model = joblib.load(gb_path)
                self.scaler = joblib.load(scaler_path)
                self.label_encoder = joblib.load(le_path)
                
                with open(meta_path, 'r') as f:
                    meta = json.load(f)
                    self.feature_columns = meta.get("feature_columns", [])
                    self.metrics = ModelMetrics(**meta.get("metrics", {}))
                
                self.is_trained = True
                logger.info(f"Loaded ML model v{self.MODEL_VERSION}")
                return True
        except Exception as e:
            logger.warning(f"Could not load ML model: {e}")
        
        return False
    
    def _save_model(self):
        """Save trained model to disk"""
        try:
            joblib.dump(self.rf_model, self._get_model_path("rf_model"))
            joblib.dump(self.gb_model, self._get_model_path("gb_model"))
            joblib.dump(self.scaler, self._get_model_path("scaler"))
            joblib.dump(self.label_encoder, self._get_model_path("label_encoder"))
            
            meta = {
                "feature_columns": self.feature_columns,
                "metrics": {
                    "accuracy": self.metrics.accuracy,
                    "f1_score": self.metrics.f1_score,
                    "training_samples": self.metrics.training_samples,
                    "feature_count": self.metrics.feature_count,
                    "trained_at": self.metrics.trained_at,
                    "model_version": self.metrics.model_version
                }
            }
            
            with open(self._get_model_path("metadata"), 'w') as f:
                json.dump(meta, f, indent=2)
            
            logger.info("ML model saved to disk")
        except Exception as e:
            logger.error(f"Failed to save ML model: {e}")
    
    async def prepare_training_data(self, days: int = 30) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare training data from ML training collection.
        Features are extracted from system metrics and event patterns.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Fetch training data
        cursor = db.ml_training_data.find(
            {"timestamp": {"$gte": cutoff}},
            {"_id": 0}
        )
        events = await cursor.to_list(length=50000)
        
        if len(events) < 100:
            raise ValueError(f"Insufficient training data: {len(events)} events (need 100+)")
        
        # Convert to DataFrame
        df = pd.DataFrame(events)
        
        # Feature engineering
        features = []
        labels = []
        
        # Group by time windows (5-minute buckets)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['time_bucket'] = df['timestamp'].dt.floor('5T')
        
        for bucket, group in df.groupby('time_bucket'):
            feature_row = self._extract_features(group)
            label = self._determine_label(group)
            
            features.append(feature_row)
            labels.append(label)
        
        X = pd.DataFrame(features)
        y = pd.Series(labels)
        
        # Store feature columns for prediction
        self.feature_columns = X.columns.tolist()
        
        return X, y
    
    def _extract_features(self, group: pd.DataFrame) -> Dict[str, float]:
        """Extract features from a time window of events"""
        features = {}
        
        # Event count features
        features['total_events'] = len(group)
        features['error_count'] = len(group[group['severity'].isin(['error', 'critical'])])
        features['warning_count'] = len(group[group['severity'] == 'warning'])
        
        # Error rate
        api_calls = group[group['event_type'] == 'api_call']
        if len(api_calls) > 0:
            error_calls = api_calls[api_calls['data'].apply(
                lambda x: x.get('status_code', 200) >= 400 if isinstance(x, dict) else False
            )]
            features['error_rate'] = len(error_calls) / len(api_calls)
        else:
            features['error_rate'] = 0
        
        # Response time features
        response_times = group['response_time_ms'].dropna()
        if len(response_times) > 0:
            features['avg_response_time'] = response_times.mean()
            features['max_response_time'] = response_times.max()
            features['response_time_std'] = response_times.std() if len(response_times) > 1 else 0
        else:
            features['avg_response_time'] = 0
            features['max_response_time'] = 0
            features['response_time_std'] = 0
        
        # System metrics
        sys_metrics = group['system_metrics'].apply(
            lambda x: x if isinstance(x, dict) else {}
        )
        
        cpu_values = [m.get('cpu_percent', 0) for m in sys_metrics if m.get('cpu_percent')]
        memory_values = [m.get('memory_percent', 0) for m in sys_metrics if m.get('memory_percent')]
        disk_values = [m.get('disk_percent', 0) for m in sys_metrics if m.get('disk_percent')]
        
        features['avg_cpu'] = np.mean(cpu_values) if cpu_values else 0
        features['max_cpu'] = np.max(cpu_values) if cpu_values else 0
        features['avg_memory'] = np.mean(memory_values) if memory_values else 0
        features['max_memory'] = np.max(memory_values) if memory_values else 0
        features['avg_disk'] = np.mean(disk_values) if disk_values else 0
        
        # Event type diversity
        features['unique_event_types'] = group['event_type'].nunique()
        features['unique_users'] = group['user_id'].nunique()
        
        # Time-based features
        if len(group) > 0:
            first_ts = group['timestamp'].min()
            features['hour_of_day'] = first_ts.hour
            features['day_of_week'] = first_ts.dayofweek
            features['is_weekend'] = 1 if first_ts.dayofweek >= 5 else 0
        else:
            features['hour_of_day'] = 0
            features['day_of_week'] = 0
            features['is_weekend'] = 0
        
        return features
    
    def _determine_label(self, group: pd.DataFrame) -> str:
        """
        Determine the issue label for a time window.
        Labels: 'healthy', 'degraded', 'critical'
        """
        error_count = len(group[group['severity'].isin(['error', 'critical'])])
        total = len(group)
        
        if total == 0:
            return 'healthy'
        
        error_rate = error_count / total
        
        # Check system metrics
        sys_metrics = group['system_metrics'].apply(
            lambda x: x if isinstance(x, dict) else {}
        )
        
        cpu_values = [m.get('cpu_percent', 0) for m in sys_metrics if m.get('cpu_percent')]
        memory_values = [m.get('memory_percent', 0) for m in sys_metrics if m.get('memory_percent')]
        
        max_cpu = np.max(cpu_values) if cpu_values else 0
        max_memory = np.max(memory_values) if memory_values else 0
        
        # Critical conditions
        if error_rate > 0.15 or max_cpu > 90 or max_memory > 90:
            return 'critical'
        
        # Degraded conditions
        if error_rate > 0.05 or max_cpu > 70 or max_memory > 75:
            return 'degraded'
        
        return 'healthy'
    
    async def train(self, days: int = 30) -> Dict[str, Any]:
        """
        Train the ML models on collected data.
        Returns training metrics and model info.
        """
        logger.info(f"Starting ML model training with {days} days of data...")
        
        try:
            # Prepare data
            X, y = await self.prepare_training_data(days)
            
            if len(X) < 50:
                return {
                    "success": False,
                    "error": f"Insufficient training samples: {len(X)} (need 50+)"
                }
            
            # Encode labels
            self.label_encoder = LabelEncoder()
            y_encoded = self.label_encoder.fit_transform(y)
            
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
            )
            
            # Train Random Forest
            self.rf_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
            self.rf_model.fit(X_train, y_train)
            
            # Train Gradient Boosting
            self.gb_model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
            self.gb_model.fit(X_train, y_train)
            
            # Evaluate
            rf_pred = self.rf_model.predict(X_test)
            gb_pred = self.gb_model.predict(X_test)
            
            # Ensemble prediction (average)
            ensemble_pred = np.round((rf_pred + gb_pred) / 2).astype(int)
            
            accuracy = accuracy_score(y_test, ensemble_pred)
            f1 = f1_score(y_test, ensemble_pred, average='weighted')
            
            # Store metrics
            self.metrics = ModelMetrics(
                accuracy=round(accuracy, 4),
                f1_score=round(f1, 4),
                training_samples=len(X),
                feature_count=len(self.feature_columns),
                trained_at=datetime.now(timezone.utc).isoformat(),
                model_version=self.MODEL_VERSION
            )
            
            self.is_trained = True
            
            # Save model
            self._save_model()
            
            # Feature importance
            feature_importance = dict(zip(
                self.feature_columns,
                self.rf_model.feature_importances_.tolist()
            ))
            top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
            
            logger.info(f"ML model training complete. Accuracy: {accuracy:.2%}")
            
            return {
                "success": True,
                "metrics": {
                    "accuracy": self.metrics.accuracy,
                    "f1_score": self.metrics.f1_score,
                    "training_samples": self.metrics.training_samples,
                    "feature_count": self.metrics.feature_count
                },
                "model_version": self.MODEL_VERSION,
                "trained_at": self.metrics.trained_at,
                "top_features": top_features,
                "class_distribution": dict(zip(
                    self.label_encoder.classes_.tolist(),
                    [int((y == c).sum()) for c in self.label_encoder.classes_]
                ))
            }
            
        except Exception as e:
            logger.error(f"ML training failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def predict(self, window_minutes: int = 5) -> Dict[str, Any]:
        """
        Predict system health for the current time window.
        Returns prediction with confidence scores.
        """
        if not self.is_trained:
            return {
                "success": False,
                "error": "Model not trained. Run training first."
            }
        
        try:
            # Get recent events
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
            cursor = db.ml_training_data.find(
                {"timestamp": {"$gte": cutoff}},
                {"_id": 0}
            )
            events = await cursor.to_list(length=1000)
            
            if len(events) < 5:
                return {
                    "success": True,
                    "prediction": "healthy",
                    "confidence": 0.5,
                    "note": "Insufficient recent data for accurate prediction"
                }
            
            # Extract features
            df = pd.DataFrame(events)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            features = self._extract_features(df)
            
            # Ensure all feature columns exist
            feature_vector = [features.get(col, 0) for col in self.feature_columns]
            X = np.array([feature_vector])
            
            # Scale
            X_scaled = self.scaler.transform(X)
            
            # Predict with both models
            rf_proba = self.rf_model.predict_proba(X_scaled)[0]
            gb_proba = self.gb_model.predict_proba(X_scaled)[0]
            
            # Ensemble
            ensemble_proba = (rf_proba + gb_proba) / 2
            prediction_idx = np.argmax(ensemble_proba)
            prediction = self.label_encoder.inverse_transform([prediction_idx])[0]
            confidence = ensemble_proba[prediction_idx]
            
            # Get class probabilities
            class_probabilities = dict(zip(
                self.label_encoder.classes_.tolist(),
                ensemble_proba.tolist()
            ))
            
            return {
                "success": True,
                "prediction": prediction,
                "confidence": round(confidence, 4),
                "probabilities": class_probabilities,
                "events_analyzed": len(events),
                "window_minutes": window_minutes,
                "features": {k: round(v, 2) if isinstance(v, float) else v 
                           for k, v in features.items()}
            }
            
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        if not self.is_trained:
            return {
                "trained": False,
                "message": "No model trained yet"
            }
        
        return {
            "trained": True,
            "version": self.MODEL_VERSION,
            "metrics": {
                "accuracy": self.metrics.accuracy,
                "f1_score": self.metrics.f1_score,
                "training_samples": self.metrics.training_samples,
                "feature_count": self.metrics.feature_count
            },
            "trained_at": self.metrics.trained_at,
            "feature_columns": self.feature_columns,
            "classes": self.label_encoder.classes_.tolist() if self.label_encoder else []
        }


# Global instance
ml_issue_predictor = IssuePredictor()


# Export
__all__ = ['IssuePredictor', 'ml_issue_predictor', 'ModelMetrics']
