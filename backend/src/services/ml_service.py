import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
import os
from config import settings
from .feature_extractor import feature_service  # ← NEW: Use live feature extractor
from typing import Dict, Any, Tuple, List

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
            print("✅ ML models loaded successfully")
            print(f"   - Fatigue classifier: {type(self.fatigue_model).__name__}")
            print(f"   - Productivity regressor: {type(self.productivity_model).__name__}")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            self.is_loaded = False
    
    def predict_from_live_data(
        self,
        user_id: str,
        laptop_usage: list,
        mobile_usage: list
    ) -> Dict[str, Any]:
        """
        Predict fatigue and productivity loss from LIVE data
        
        Args:
            user_id: User identifier
            laptop_usage: Recent laptop usage data
            mobile_usage: Recent mobile usage data
            
        Returns:
            Complete prediction results
        """
        if not self.is_loaded:
            self.load_models()
        
        # Extract features from LIVE data (NO STATIC DATASETS)
        feature_result = feature_service.process_live_data_for_prediction(
            user_id=user_id,
            laptop_usage=laptop_usage,
            mobile_usage=mobile_usage
        )
        
        features = feature_result['features']
        
        # Get ML-ready features
        X_classification = feature_service.extractor.prepare_for_classification(features)
        
        # Predict fatigue level and score
        fatigue_prediction = self.fatigue_model.predict(X_classification)[0]
        fatigue_probabilities = self.fatigue_model.predict_proba(X_classification)[0]
        fatigue_level = self.label_encoder.inverse_transform([fatigue_prediction])[0]
        
        # Fatigue score is probability of "High" fatigue class
        fatigue_score = float(fatigue_probabilities[list(self.label_encoder.classes_).index('High')] * 100)
        
        # Now predict productivity loss (requires fatigue_score as feature)
        X_regression = feature_service.extractor.prepare_for_regression(features, fatigue_score)
        productivity_loss = float(self.productivity_model.predict(X_regression)[0])
        
        # Generate insights
        insights = self._generate_insights(features, fatigue_score, fatigue_level, productivity_loss)
        
        return {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'predictions': {
                'fatigue_score': fatigue_score,
                'fatigue_level': fatigue_level,
                'productivity_loss': productivity_loss,
                'confidence': float(max(fatigue_probabilities))
            },
            'features': features,
            'feature_explanations': feature_service.get_feature_explanations(),
            'insights': insights,
            'derived_metrics': feature_result['derived_metrics'],
            'data_quality': feature_result['data_summary']['data_quality']
        }
    
    def _generate_insights(
        self,
        features: Dict,
        fatigue_score: float,
        fatigue_level: str,
        productivity_loss: float
    ) -> Dict:
        """Generate human-readable insights from predictions"""
        insights = []
        
        # Screen time insights
        screen_time = features.get('screen_time', 0)
        if screen_time > 10:
            insights.append(f"High screen time detected: {screen_time}h (recommended: <8h)")
        elif screen_time > 8:
            insights.append(f"Moderate screen time: {screen_time}h")
        else:
            insights.append(f"Healthy screen time: {screen_time}h")
        
        # Break frequency insights
        breaks = features.get('breaks', 0)
        if breaks < 1:
            insights.append("Very few breaks taken. Aim for 2-3 breaks per hour.")
        elif breaks < 2:
            insights.append("Could take more frequent breaks for better focus.")
        else:
            insights.append("Good break frequency maintained.")
        
        # Night usage insights
        night_ratio = features.get('night_ratio', 0)
        if night_ratio > 0.3:
            insights.append(f"High night usage ({night_ratio*100:.0f}%). Affects sleep quality.")
        elif night_ratio > 0.1:
            insights.append(f"Moderate night usage ({night_ratio*100:.0f}%).")
        
        # Productivity insights
        productive_ratio = features.get('productive_ratio', 0)
        if productive_ratio < 0.3:
            insights.append(f"Low productive app usage ({productive_ratio*100:.0f}%). Consider focus sessions.")
        elif productive_ratio > 0.7:
            insights.append(f"High productive usage ({productive_ratio*100:.0f}%). Good focus!")
        
        # Fatigue insights
        if fatigue_level == "High":
            insights.append(f"High fatigue risk ({fatigue_score:.0f}%). Consider taking a break.")
        elif fatigue_level == "Medium":
            insights.append(f"Moderate fatigue ({fatigue_score:.0f}%). Monitor your energy levels.")
        else:
            insights.append(f"Low fatigue ({fatigue_score:.0f}%). Good energy management!")
        
        # Productivity loss insights
        if productivity_loss > 15:
            insights.append(f"High productivity loss: {productivity_loss:.1f} hours/week")
        elif productivity_loss > 10:
            insights.append(f"Moderate productivity loss: {productivity_loss:.1f} hours/week")
        else:
            insights.append(f"Minimal productivity loss: {productivity_loss:.1f} hours/week")
        
        return {
            'summary': insights[:5],  # Top 5 insights
            'primary_concern': self._identify_primary_concern(features, fatigue_score, productivity_loss),
            'improvement_areas': self._identify_improvement_areas(features)
        }
    
    def _identify_primary_concern(
        self,
        features: Dict,
        fatigue_score: float,
        productivity_loss: float
    ) -> str:
        """Identify the most pressing concern"""
        concerns = []
        
        if fatigue_score > 70:
            concerns.append(("High fatigue level", 3))
        if productivity_loss > 15:
            concerns.append(("Significant productivity loss", 3))
        if features.get('screen_time', 0) > 10:
            concerns.append(("Excessive screen time", 2))
        if features.get('night_ratio', 0) > 0.3:
            concerns.append(("Late-night usage", 2))
        if features.get('breaks', 0) < 1:
            concerns.append(("Insufficient breaks", 1))
        
        if not concerns:
            return "All metrics within healthy ranges"
        
        # Return highest priority concern
        concerns.sort(key=lambda x: x[1], reverse=True)
        return concerns[0][0]
    
    def _identify_improvement_areas(self, features: Dict) -> List[str]:
        """Identify areas for improvement"""
        areas = []
        
        if features.get('productive_ratio', 0) < 0.4:
            areas.append("Increase productive app usage")
        if features.get('breaks', 0) < 2:
            areas.append("Take more frequent breaks")
        if features.get('night_ratio', 0) > 0.2:
            areas.append("Reduce late-night screen time")
        if features.get('screen_time', 0) > 8:
            areas.append("Reduce total screen time")
        
        return areas
    
    def batch_predict(self, users_data: Dict) -> Dict:
        """
        Batch prediction for multiple users
        Useful for admin dashboards or analytics
        """
        results = {}
        
        for user_id, data in users_data.items():
            try:
                prediction = self.predict_from_live_data(
                    user_id=user_id,
                    laptop_usage=data.get('laptop_usage', []),
                    mobile_usage=data.get('mobile_usage', [])
                )
                results[user_id] = prediction
            except Exception as e:
                results[user_id] = {
                    'error': str(e),
                    'user_id': user_id
                }
        
        # Calculate aggregate statistics
        if results:
            fatigue_scores = [r.get('predictions', {}).get('fatigue_score', 0) 
                            for r in results.values() if 'predictions' in r]
            productivity_losses = [r.get('predictions', {}).get('productivity_loss', 0) 
                                 for r in results.values() if 'predictions' in r]
            
            aggregate_stats = {
                'avg_fatigue_score': np.mean(fatigue_scores) if fatigue_scores else 0,
                'avg_productivity_loss': np.mean(productivity_losses) if productivity_losses else 0,
                'high_risk_users': len([s for s in fatigue_scores if s > 70]),
                'total_users': len(results)
            }
        else:
            aggregate_stats = {}
        
        return {
            'individual_results': results,
            'aggregate_statistics': aggregate_stats,
            'timestamp': datetime.now().isoformat()
        }


# Global instance
ml_service = MLService()