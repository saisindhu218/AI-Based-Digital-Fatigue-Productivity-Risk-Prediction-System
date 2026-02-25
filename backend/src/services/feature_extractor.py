"""
Feature extraction for ML models
"""
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class LiveFeatureExtractor:
    """Extract features from live usage data"""
    
    def __init__(self):
        pass
    
    def extract_features_from_live_data(
        self,
        laptop_data: List[Dict],
        mobile_data: List[Dict],
        user_id: Optional[str] = None
    ) -> Dict[str, float]:
        """Extract features from live usage data"""
        
        # Combine all data
        all_data = laptop_data + mobile_data
        
        if not all_data:
            return self._get_default_features()
        
        try:
            # Calculate features
            total_screen_time = sum(self._get_duration(item) for item in all_data) / 3600  # hours
            
            # Average session length
            session_count = len(all_data)
            avg_session = total_screen_time / max(session_count, 1)
            
            # Breaks (gaps > 5 minutes)
            breaks = self._calculate_breaks(all_data)
            
            # Night usage ratio (10PM-6AM)
            night_ratio = self._calculate_night_ratio(all_data)
            
            # Productive ratio
            productive_ratio = self._calculate_productive_ratio(all_data)
            
            # Social media ratio
            social_ratio = self._calculate_social_ratio(all_data)
            
            # Entertainment ratio
            entertainment_ratio = self._calculate_entertainment_ratio(all_data)
            
            # Focus score
            focus_score = self._calculate_focus_score(all_data)
            
            return {
                'screen_time': round(total_screen_time, 2),
                'avg_session': round(avg_session, 2),
                'breaks': breaks,
                'night_ratio': round(night_ratio, 2),
                'productive_ratio': round(productive_ratio, 2),
                'social_ratio': round(social_ratio, 2),
                'entertainment_ratio': round(entertainment_ratio, 2),
                'focus_score': round(focus_score, 2)
            }
            
        except Exception as e:
            print(f"⚠️ Error extracting features: {e}")
            return self._get_default_features()
    
    def prepare_for_classification(self, features: Dict) -> np.ndarray:
        """Prepare features for fatigue classification"""
        # Order matters - must match training
        feature_order = [
            'screen_time', 'avg_session', 'breaks', 
            'night_ratio', 'productive_ratio'
        ]
        
        values = [features.get(f, 0) for f in feature_order]
        return np.array(values).reshape(1, -1)
    
    def prepare_for_regression(self, features: Dict) -> np.ndarray:
        """Prepare features for productivity loss regression"""
        # Order matters - must match training
        feature_order = [
            'screen_time', 'avg_session', 'breaks',
            'night_ratio', 'productive_ratio', 'focus_score'
        ]
        
        values = [features.get(f, 0) for f in feature_order]
        return np.array(values).reshape(1, -1)
    
    def _get_duration(self, item: Dict) -> float:
        """Extract duration in seconds"""
        if 'duration' in item:
            return float(item['duration'])
        elif 'usage_duration' in item:
            return float(item['usage_duration'])
        elif 'screen_time' in item:
            return float(item['screen_time'])
        return 0
    
    def _calculate_breaks(self, data: List[Dict]) -> int:
        """Calculate number of breaks (>5 min gaps)"""
        if len(data) < 2:
            return 0
        
        breaks = 0
        # Sort by timestamp
        sorted_data = sorted(data, key=lambda x: self._get_timestamp(x))
        
        for i in range(1, len(sorted_data)):
            prev_time = self._get_timestamp(sorted_data[i-1])
            curr_time = self._get_timestamp(sorted_data[i])
            
            if prev_time and curr_time:
                gap = (curr_time - prev_time).total_seconds()
                if gap > 300:  # 5 minutes
                    breaks += 1
        
        return breaks
    
    def _get_timestamp(self, item: Dict) -> Optional[datetime]:
        """Extract timestamp from item"""
        if 'timestamp' in item:
            ts = item['timestamp']
            if isinstance(ts, datetime):
                return ts
            elif isinstance(ts, str):
                try:
                    return datetime.fromisoformat(ts.replace('Z', '+00:00'))
                except:
                    pass
        return None
    
    def _calculate_night_ratio(self, data: List[Dict]) -> float:
        """Calculate ratio of usage during night hours (10PM-6AM)"""
        night_hours = [22, 23, 0, 1, 2, 3, 4, 5]
        night_duration = 0
        total_duration = 0
        
        for item in data:
            duration = self._get_duration(item)
            total_duration += duration
            
            ts = self._get_timestamp(item)
            if ts and ts.hour in night_hours:
                night_duration += duration
        
        if total_duration == 0:
            return 0
            
        return night_duration / total_duration
    
    def _calculate_productive_ratio(self, data: List[Dict]) -> float:
        """Calculate ratio of productive app usage"""
        productive_categories = [
            'work', 'coding', 'development', 'vscode', 'pycharm',
            'word', 'excel', 'powerpoint', 'outlook', 'slack',
            'teams', 'zoom', 'meet', 'research', 'learning',
            'documentation', 'terminal', 'cmd', 'powershell'
        ]
        
        productive_duration = 0
        total_duration = 0
        
        for item in data:
            duration = self._get_duration(item)
            total_duration += duration
            
            category = str(item.get('category', '')).lower()
            app_name = str(item.get('app_name', '')).lower()
            
            if any(cat in category or cat in app_name for cat in productive_categories):
                productive_duration += duration
        
        if total_duration == 0:
            return 0.5  # Default
            
        return productive_duration / total_duration
    
    def _calculate_social_ratio(self, data: List[Dict]) -> float:
        """Calculate ratio of social media usage"""
        social_categories = [
            'social', 'facebook', 'instagram', 'twitter', 'whatsapp',
            'telegram', 'discord', 'reddit', 'tiktok', 'snapchat',
            'messenger', 'linkedin', 'social_media'
        ]
        
        social_duration = 0
        total_duration = 0
        
        for item in data:
            duration = self._get_duration(item)
            total_duration += duration
            
            category = str(item.get('category', '')).lower()
            app_name = str(item.get('app_name', '')).lower()
            
            if any(cat in category or cat in app_name for cat in social_categories):
                social_duration += duration
        
        if total_duration == 0:
            return 0.1  # Default
            
        return social_duration / total_duration
    
    def _calculate_entertainment_ratio(self, data: List[Dict]) -> float:
        """Calculate ratio of entertainment usage"""
        entertainment_categories = [
            'entertainment', 'youtube', 'netflix', 'prime', 'hotstar',
            'music', 'spotify', 'game', 'gaming', 'video', 'movie',
            'tv', 'streaming', 'hulu', 'disney'
        ]
        
        entertainment_duration = 0
        total_duration = 0
        
        for item in data:
            duration = self._get_duration(item)
            total_duration += duration
            
            category = str(item.get('category', '')).lower()
            app_name = str(item.get('app_name', '')).lower()
            
            if any(cat in category or cat in app_name for cat in entertainment_categories):
                entertainment_duration += duration
        
        if total_duration == 0:
            return 0.2  # Default
            
        return entertainment_duration / total_duration
    
    def _calculate_focus_score(self, data: List[Dict]) -> float:
        """Calculate focus score (0-100)"""
        if not data:
            return 70  # Default
        
        productive_ratio = self._calculate_productive_ratio(data)
        social_ratio = self._calculate_social_ratio(data)
        entertainment_ratio = self._calculate_entertainment_ratio(data)
        
        # Focus = high productive, low social, low entertainment
        focus_score = (
            productive_ratio * 70 -  # Positive for productive
            social_ratio * 20 -      # Negative for social
            entertainment_ratio * 10  # Negative for entertainment
        ) * 100
        
        # Clamp to 0-100
        return max(0, min(100, focus_score))
    
    def _get_default_features(self) -> Dict[str, float]:
        """Return default features when no data"""
        return {
            'screen_time': 4.0,
            'avg_session': 1.5,
            'breaks': 2,
            'night_ratio': 0.2,
            'productive_ratio': 0.6,
            'social_ratio': 0.15,
            'entertainment_ratio': 0.15,
            'focus_score': 70.0
        }