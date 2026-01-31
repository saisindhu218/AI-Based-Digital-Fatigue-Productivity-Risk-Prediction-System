"""
Live feature extraction service - replaces static dataset usage
Integrates with friend's ML models
"""
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
from data_science.feature_engineering import LiveFeatureExtractor

class RealTimeFeatureService:
    """
    Service to extract features from real-time data for ML predictions
    """
    
    def __init__(self):
        self.extractor = LiveFeatureExtractor()
        
    def process_live_data_for_prediction(
        self,
        user_id: str,
        laptop_usage: List[Dict],
        mobile_usage: List[Dict]
    ) -> Dict[str, Any]:
        """
        Process live usage data and extract features for ML models
        
        Args:
            user_id: User identifier
            laptop_usage: Recent laptop usage data
            mobile_usage: Recent mobile usage data
            
        Returns:
            Dictionary with extracted features and metadata
        """
        print(f"Processing live data for user {user_id}")
        print(f"Laptop records: {len(laptop_usage)}, Mobile records: {len(mobile_usage)}")
        
        # Extract features from LIVE data
        features = self.extractor.extract_features_from_live_data(
            laptop_data=laptop_usage,
            mobile_data=mobile_usage,
            user_id=user_id
        )
        
        # Calculate derived metrics
        derived_metrics = self._calculate_derived_metrics(features)
        
        # Prepare output
        result = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'features': features,
            'derived_metrics': derived_metrics,
            'ml_input': {
                'classification_features': self.extractor.prepare_for_classification(features).tolist(),
                'requires_fatigue_score': True  # Need fatigue score for regression
            },
            'data_summary': {
                'total_records': len(laptop_usage) + len(mobile_usage),
                'analysis_window': '24_hours',
                'data_quality': self._assess_data_quality(laptop_usage, mobile_usage)
            }
        }
        
        return result
    
    def _calculate_derived_metrics(self, features: Dict) -> Dict:
        """Calculate additional metrics from features"""
        screen_time = features.get('screen_time', 0)
        productive_ratio = features.get('productive_ratio', 0)
        breaks = features.get('breaks', 0)
        
        # Productivity score (0-100)
        productivity_score = min(100, 
            (productive_ratio * 50) +  # Weight for productive ratio
            (min(breaks, 4) * 5) +     # Weight for breaks (capped at 4 per hour)
            (min(screen_time, 8) * 5)  # Weight for reasonable screen time
        )
        
        # Digital wellness score
        wellness_score = min(100,
            100 - (features.get('night_ratio', 0) * 30) -  # Penalize night usage
            (max(0, screen_time - 6) * 5) +  # Penalize excessive screen time
            (breaks * 10) +  # Reward breaks
            (productive_ratio * 15)  # Reward productive usage
        )
        
        # Risk indicators
        risk_factors = []
        if features.get('night_ratio', 0) > 0.3:
            risk_factors.append('high_night_usage')
        if screen_time > 10:
            risk_factors.append('excessive_screen_time')
        if features.get('productive_ratio', 0) < 0.3:
            risk_factors.append('low_productivity')
        if breaks < 1:
            risk_factors.append('insufficient_breaks')
        
        return {
            'productivity_score': round(productivity_score, 2),
            'wellness_score': round(wellness_score, 2),
            'risk_factors': risk_factors,
            'recommended_actions': self._generate_recommendations(features, risk_factors)
        }
    
    def _generate_recommendations(self, features: Dict, risk_factors: List) -> List[str]:
        """Generate personalized recommendations based on features"""
        recommendations = []
        
        screen_time = features.get('screen_time', 0)
        productive_ratio = features.get('productive_ratio', 0)
        breaks = features.get('breaks', 0)
        night_ratio = features.get('night_ratio', 0)
        
        if screen_time > 8:
            recommendations.append(f"Consider reducing screen time. Current: {screen_time}h")
        
        if productive_ratio < 0.4:
            recommendations.append("Try using more productive apps. Current productivity ratio is low.")
        
        if breaks < 2:
            recommendations.append("Take more frequent breaks. Aim for 2-3 breaks per hour.")
        
        if night_ratio > 0.2:
            recommendations.append("Reduce late-night screen usage for better sleep quality.")
        
        if 'excessive_screen_time' in risk_factors:
            recommendations.append("Implement the 20-20-20 rule: every 20 minutes, look at something 20 feet away for 20 seconds.")
        
        if 'low_productivity' in risk_factors:
            recommendations.append("Use app blockers during focus sessions to minimize distractions.")
        
        # Always include general wellness tips
        recommendations.extend([
            "Stay hydrated - drink water regularly",
            "Practice good posture to prevent strain",
            "Take a 5-minute walk every hour"
        ])
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _assess_data_quality(self, laptop_data: List, mobile_data: List) -> Dict:
        """Assess quality of incoming data"""
        total_records = len(laptop_data) + len(mobile_data)
        
        # Check timestamps
        valid_timestamps = 0
        all_data = laptop_data + mobile_data
        
        for record in all_data:
            try:
                datetime.fromisoformat(record.get('timestamp', '').replace('Z', ''))
                valid_timestamps += 1
            except:
                pass
        
        timestamp_quality = valid_timestamps / total_records if total_records > 0 else 0
        
        # Check data completeness
        complete_records = 0
        for record in all_data:
            if 'timestamp' in record and ('usage_duration' in record or 'screen_time' in record):
                complete_records += 1
        
        completeness = complete_records / total_records if total_records > 0 else 0
        
        return {
            'total_records': total_records,
            'timestamp_quality': round(timestamp_quality, 2),
            'completeness': round(completeness, 2),
            'quality_level': 'good' if completeness > 0.7 else 'fair' if completeness > 0.4 else 'poor'
        }
    
    def get_feature_explanations(self) -> Dict:
        """Return explanations for each feature (useful for UI)"""
        return {
            'screen_time': 'Total daily screen time in hours. High values (>8h) increase fatigue risk.',
            'avg_session': 'Average length of continuous usage sessions in hours. Longer sessions reduce recovery.',
            'breaks': 'Frequency of breaks per hour of usage. More frequent breaks reduce fatigue.',
            'night_ratio': 'Percentage of usage during night hours (10PM-6AM). Disrupts circadian rhythm.',
            'productive_ratio': 'Percentage of time spent on productive/work-related applications.',
            'social_ratio': 'Percentage of time spent on social media applications.',
            'entertainment_ratio': 'Percentage of time spent on entertainment applications.',
            'focus_score': 'Score based on uninterrupted productive work sessions.'
        }


# Singleton instance
feature_service = RealTimeFeatureService()