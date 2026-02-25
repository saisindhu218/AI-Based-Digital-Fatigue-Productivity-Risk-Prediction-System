import joblib
import numpy as np
from pathlib import Path
from src.config import settings
from datetime import datetime
import os

class MLService:
    def __init__(self):
        self.fatigue_classifier = None
        self.fatigue_label_encoder = None
        self.productivity_model = None
        self.is_loaded = False
    
    def load_models(self):
        """Load ML models from pickle files"""
        try:
            # Get models directory from settings
            models_dir = Path(settings.ML_MODELS_DIR)
            print(f"🔍 Looking for ML models in: {models_dir}")
            
            # Check if directory exists
            if not models_dir.exists():
                print(f"⚠️ ML models directory not found at: {models_dir}")
                print(f"   Creating directory: {models_dir}")
                models_dir.mkdir(parents=True, exist_ok=True)
                self.is_loaded = False
                return
            
            # Load fatigue classifier
            classifier_path = models_dir / "fatigue_classifier.pkl"
            if classifier_path.exists():
                self.fatigue_classifier = joblib.load(classifier_path)
                print(f"✅ Loaded fatigue classifier: {type(self.fatigue_classifier).__name__}")
            else:
                print(f"⚠️ Fatigue classifier not found at: {classifier_path}")
            
            # Load label encoder
            encoder_path = models_dir / "fatigue_label_encoder.pkl"
            if encoder_path.exists():
                self.fatigue_label_encoder = joblib.load(encoder_path)
                print(f"✅ Loaded label encoder")
            else:
                print(f"⚠️ Label encoder not found at: {encoder_path}")
            
            # Load productivity model
            productivity_path = models_dir / "productivity_loss_model.pkl"
            if productivity_path.exists():
                self.productivity_model = joblib.load(productivity_path)
                print(f"✅ Loaded productivity model: {type(self.productivity_model).__name__}")
            else:
                print(f"⚠️ Productivity model not found at: {productivity_path}")
            
            self.is_loaded = (self.fatigue_classifier is not None and 
                            self.productivity_model is not None)
            
            if self.is_loaded:
                print("✅ All ML models loaded successfully")
            else:
                print("⚠️ Some ML models failed to load - using fallback predictions")
                
        except Exception as e:
            print(f"❌ Error loading ML models: {e}")
            self.is_loaded = False
    
    def predict_fatigue(self, features: dict):
        """Predict fatigue level from usage features"""
        if not self.is_loaded or not self.fatigue_classifier or not self.fatigue_label_encoder:
            # Return default prediction if models not loaded
            total_hours = features.get('screen_time', 4)
            score = min(100, total_hours * 10)
            if score > 70:
                level = "High"
            elif score > 40:
                level = "Medium"
            else:
                level = "Low"
            
            return {
                "level": level,
                "score": score,
                "confidence": 0.75,
                "features_used": ['screen_time', 'avg_session', 'breaks', 'night_ratio', 'productive_ratio']
            }
        
        try:
            # Extract features in correct order
            feature_names = ['screen_time', 'avg_session', 'breaks', 'night_ratio', 'productive_ratio']
            feature_values = [features.get(name, 0) for name in feature_names]
            
            # Convert to numpy array and reshape
            X = np.array(feature_values).reshape(1, -1)
            
            # Predict
            prediction_encoded = self.fatigue_classifier.predict(X)[0]
            prediction_label = self.fatigue_label_encoder.inverse_transform([prediction_encoded])[0]
            
            # Get probability scores
            if hasattr(self.fatigue_classifier, 'predict_proba'):
                probabilities = self.fatigue_classifier.predict_proba(X)[0]
                confidence = max(probabilities)
            else:
                confidence = 0.8  # Default confidence
            
            # Calculate score based on label
            if prediction_label == "Low":
                score = 25
            elif prediction_label == "Medium":
                score = 55
            else:  # High
                score = 85
            
            return {
                "level": prediction_label,
                "score": float(score),
                "confidence": float(confidence),
                "features_used": feature_names
            }
        except Exception as e:
            print(f"⚠️ Error in predict_fatigue: {e}")
            # Fallback
            return {
                "level": "Medium",
                "score": 50,
                "confidence": 0.7,
                "features_used": ['screen_time', 'avg_session', 'breaks', 'night_ratio', 'productive_ratio']
            }
    
    def predict_productivity_loss(self, features: dict):
        """Predict productivity loss from usage features"""
        if not self.is_loaded or not self.productivity_model:
            # Return default prediction if model not loaded
            total_hours = features.get('screen_time', 4)
            loss_hours = total_hours * 0.2
            return {
                "loss_hours": float(loss_hours),
                "features_used": ['screen_time', 'avg_session', 'breaks', 'night_ratio', 'productive_ratio', 'fatigue_score']
            }
        
        try:
            # Extract features in correct order
            feature_names = ['screen_time', 'avg_session', 'breaks', 
                            'night_ratio', 'productive_ratio', 'fatigue_score']
            feature_values = [features.get(name, 0) for name in feature_names]
            
            # Convert to numpy array and reshape
            X = np.array(feature_values).reshape(1, -1)
            
            # Predict
            prediction = self.productivity_model.predict(X)[0]
            
            return {
                "loss_hours": float(prediction),
                "features_used": feature_names
            }
        except Exception as e:
            print(f"⚠️ Error in predict_productivity_loss: {e}")
            # Fallback
            total_hours = features.get('screen_time', 4)
            return {
                "loss_hours": float(total_hours * 0.25),
                "features_used": ['screen_time', 'avg_session', 'breaks', 'night_ratio', 'productive_ratio', 'fatigue_score']
            }
    
    def extract_features_from_usage(self, usage_data: list):
        """Extract ML features from raw usage data"""
        if not usage_data:
            return {
                "screen_time": 0,
                "avg_session": 0,
                "breaks": 0,
                "night_ratio": 0,
                "productive_ratio": 0,
                "fatigue_score": 0
            }
        
        try:
            # Calculate features from usage data
            total_screen_time = sum(item.get('duration', 0) for item in usage_data)
            session_count = len(usage_data)
            avg_session = total_screen_time / max(session_count, 1)
            
            # Calculate breaks (sessions with gap > 5 minutes)
            breaks = 0
            if len(usage_data) > 1:
                # Sort by timestamp
                usage_data.sort(key=lambda x: x.get('timestamp', datetime.min))
                for i in range(1, len(usage_data)):
                    prev_end = usage_data[i-1].get('timestamp', 0)
                    if isinstance(prev_end, datetime):
                        prev_end_timestamp = prev_end.timestamp()
                    else:
                        prev_end_timestamp = 0
                        
                    current_start = usage_data[i].get('timestamp', 0)
                    if isinstance(current_start, datetime):
                        current_start_timestamp = current_start.timestamp()
                    else:
                        current_start_timestamp = 0
                    
                    if current_start_timestamp - prev_end_timestamp > 300:  # 5 minutes in seconds
                        breaks += 1
            
            # Calculate night usage ratio (10 PM to 6 AM)
            night_hours = [22, 23, 0, 1, 2, 3, 4, 5]
            night_usage = 0
            for item in usage_data:
                hour = item.get('hour', 0)
                if hour in night_hours:
                    night_usage += item.get('duration', 0)
            
            night_ratio = night_usage / max(total_screen_time, 1)
            
            # Calculate productive ratio (based on app categories)
            productive_categories = ['work', 'coding', 'learning', 'research', 
                                    'vscode', 'pycharm', 'word', 'excel', 'development']
            productive_usage = 0
            for item in usage_data:
                category = item.get('category', '').lower()
                if category in productive_categories:
                    productive_usage += item.get('duration', 0)
            
            productive_ratio = productive_usage / max(total_screen_time, 1)
            
            # Estimate fatigue score (0-100)
            fatigue_score = min(100, (
                (total_screen_time / 3600) * 10 +  # 10 points per hour
                night_ratio * 30 +                  # 30 points for night usage
                (1 - productive_ratio) * 40         # 40 points for unproductive usage
            ))
            
            return {
                "screen_time": total_screen_time / 3600,  # Convert to hours
                "avg_session": avg_session / 60,         # Convert to minutes
                "breaks": breaks,
                "night_ratio": float(night_ratio),
                "productive_ratio": float(productive_ratio),
                "fatigue_score": float(fatigue_score)
            }
        except Exception as e:
            print(f"⚠️ Error in extract_features_from_usage: {e}")
            # Return default features
            return {
                "screen_time": 4.0,
                "avg_session": 45.0,
                "breaks": 3,
                "night_ratio": 0.2,
                "productive_ratio": 0.6,
                "fatigue_score": 50.0
            }

# Create global instance
ml_service = MLService()