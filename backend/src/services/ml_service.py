import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Tuple
import os
from config import settings

class MLService:
    def __init__(self):
        self.fatigue_model = None
        self.label_encoder = None
        self.productivity_model = None
        self.is_loaded = False
        
    def load_models(self):
        """Load pre-trained models from ml_models directory"""
        try:
            models_dir = settings.ML_MODELS_DIR
            
            self.fatigue_model = joblib.load(
                os.path.join(models_dir, "fatigue_classifier.pkl")
            )
            
            self.label_encoder = joblib.load(
                os.path.join(models_dir, "fatigue_label_encoder.pkl")
            )
            
            self.productivity_model = joblib.load(
                os.path.join(models_dir, "productivity_loss_model.pkl")
            )
            
            self.is_loaded = True
            print("ML models loaded successfully")
            
        except Exception as e:
            print(f"Error loading models: {e}")
            self.is_loaded = False
    
    def extract_features_from_live_data(
        self, 
        laptop_data: Dict[str, Any],
        mobile_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Extract features from real-time laptop and mobile usage data
        NO STATIC DATASETS - only live data processing
        """
        features = {}
        
        # Laptop features from live data
        features['total_laptop_minutes'] = laptop_data.get('usage_duration', 0)
        features['avg_session_length'] = laptop_data.get('session_length', 0)
        features['idle_ratio'] = (
            laptop_data.get('idle_time', 0) / 
            max(laptop_data.get('usage_duration', 1), 1)
        )
        features['keystroke_rate'] = laptop_data.get('keystrokes', 0) / 60
        features['mouse_activity'] = laptop_data.get('mouse_clicks', 0) / 60
        
        # Mobile features from live data
        features['total_mobile_minutes'] = mobile_data.get('screen_time', 0)
        features['mobile_notifications'] = mobile_data.get('notifications_received', 0)
        
        # Time-based features
        hour = datetime.now().hour
        features['is_evening'] = 1 if 18 <= hour < 24 else 0
        features['is_night'] = 1 if 0 <= hour < 6 else 0
        features['is_weekend'] = 1 if datetime.now().weekday() >= 5 else 0
        
        # Combined metrics
        features['total_screen_time'] = (
            features['total_laptop_minutes'] + features['total_mobile_minutes']
        )
        features['device_switch_rate'] = (
            features['total_laptop_minutes'] / 
            max(features['total_mobile_minutes'], 1)
        )
        
        return features
    
    def predict_fatigue(self, features: Dict[str, float]) -> Tuple[float, str]:
        """Predict fatigue score and level using pre-trained model"""
        if not self.is_loaded:
            self.load_models()
        
        # Convert features to array
        feature_names = [
            'total_screen_time', 'avg_session_length', 'idle_ratio',
            'keystroke_rate', 'mouse_activity', 'is_evening',
            'is_night', 'is_weekend', 'device_switch_rate'
        ]
        
        X = np.array([[features.get(f, 0) for f in feature_names]])
        
        # Predict
        fatigue_score = self.fatigue_model.predict_proba(X)[0][1] * 100
        prediction = self.fatigue_model.predict(X)[0]
        fatigue_level = self.label_encoder.inverse_transform([prediction])[0]
        
        return float(fatigue_score), fatigue_level
    
    def predict_productivity_loss(self, features: Dict[str, float]) -> float:
        """Predict productivity loss in hours/week"""
        if not self.is_loaded:
            self.load_models()
        
        feature_names = [
            'total_screen_time', 'avg_session_length', 'idle_ratio',
            'keystroke_rate', 'mobile_notifications', 'is_evening'
        ]
        
        X = np.array([[features.get(f, 0) for f in feature_names]])
        productivity_loss = self.productivity_model.predict(X)[0]
        
        return float(productivity_loss)
    
    def detect_productivity_zones(
        self, 
        usage_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Identify peak productivity hours and fatigue-prone windows"""
        # Analyze recent usage data to find patterns
        peak_hours = []
        fatigue_windows = []
        
        # This would typically analyze historical data from database
        # For demo, returning sample patterns
        current_hour = datetime.now().hour
        
        if 9 <= current_hour <= 12:
            peak_hours = ["09:00-12:00"]
            fatigue_windows = ["14:00-16:00"]
        elif 14 <= current_hour <= 16:
            peak_hours = ["09:00-12:00"]
            fatigue_windows = ["14:00-16:00", "current"]
        else:
            peak_hours = ["09:00-12:00", "19:00-21:00"]
            fatigue_windows = ["14:00-16:00"]
        
        return {
            "peak_hours": peak_hours,
            "fatigue_prone_windows": fatigue_windows
        }
    
    def generate_recommendations(
        self, 
        fatigue_score: float,
        fatigue_level: str,
        productivity_loss: float
    ) -> List[str]:
        """Generate personalized recommendations based on predictions"""
        recommendations = []
        
        if fatigue_score > 70:
            recommendations.extend([
                "Take a 15-minute break away from screens",
                "Practice 5-10 minutes of deep breathing",
                "Hydrate with water - dehydration increases fatigue"
            ])
        
        if fatigue_level == "High":
            recommendations.extend([
                "Consider a 20-minute power nap if possible",
                "Engage in light physical activity (stretching, walking)",
                "Reduce screen brightness and enable blue light filter"
            ])
        
        if productivity_loss > 15:
            recommendations.extend([
                "Schedule focused work sessions using Pomodoro technique",
                "Prioritize tasks using Eisenhower Matrix",
                "Limit multitasking - focus on one task at a time"
            ])
        
        # Always include general recommendations
        recommendations.extend([
            "Ensure 7-8 hours of quality sleep",
            "Take regular micro-breaks every 45-50 minutes",
            "Practice the 20-20-20 rule for eye strain"
        ])
        
        return recommendations[:5]  # Return top 5 recommendations

ml_service = MLService()