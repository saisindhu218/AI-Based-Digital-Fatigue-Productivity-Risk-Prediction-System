"""
Feature engineering for LIVE data
Converts real-time usage data into features for ML models
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

class LiveFeatureExtractor:
    """
    Extract features from LIVE laptop and mobile usage data
    NO STATIC DATASETS - processes real-time data only
    """
    
    def __init__(self):
        # Feature names expected by pre-trained models (from friend's notebooks)
        self.classification_features = [
            'screen_time', 
            'avg_session', 
            'breaks', 
            'night_ratio', 
            'productive_ratio'
        ]
        
        self.regression_features = [
            'screen_time', 
            'avg_session', 
            'breaks', 
            'night_ratio', 
            'productive_ratio',
            'fatigue_score'
        ]
        
        # App categories for productive ratio calculation
        self.productive_apps = [
            'vs code', 'pycharm', 'intellij', 'eclipse', 'sublime',
            'chrome', 'firefox', 'edge', 'safari',
            'slack', 'teams', 'zoom', 'outlook', 'gmail',
            'jupyter', 'rstudio', 'terminal', 'cmd',
            'excel', 'word', 'powerpoint', 'google docs', 'sheets'
        ]
        
        self.social_apps = [
            'facebook', 'instagram', 'twitter', 'whatsapp', 
            'telegram', 'messenger', 'snapchat', 'tiktok'
        ]
        
        self.entertainment_apps = [
            'youtube', 'netflix', 'spotify', 'prime video',
            'disney+', 'hulu', 'twitch', 'games'
        ]
    
    def extract_features_from_live_data(
        self,
        laptop_data: List[Dict],
        mobile_data: List[Dict],
        user_id: str = None
    ) -> Dict[str, float]:
        """
        Extract ML features from LIVE laptop and mobile usage data
        
        Args:
            laptop_data: List of laptop usage records (last 24 hours)
            mobile_data: List of mobile usage records (last 24 hours)
            user_id: Optional user ID for personalized features
            
        Returns:
            Dictionary of feature values for ML prediction
        """
        print(f"Extracting features from {len(laptop_data)} laptop records and {len(mobile_data)} mobile records")
        
        # Combine and process data
        all_data = self._combine_and_preprocess(laptop_data, mobile_data)
        
        if len(all_data) == 0:
            print("Warning: No usage data available for feature extraction")
            return self._get_default_features()
        
        # Calculate features
        features = {}
        
        # 1. screen_time (total hours)
        features['screen_time'] = self._calculate_screen_time(all_data)
        
        # 2. avg_session (average session length in hours)
        features['avg_session'] = self._calculate_avg_session_length(all_data)
        
        # 3. breaks (break frequency per hour)
        features['breaks'] = self._calculate_break_frequency(all_data)
        
        # 4. night_ratio (percentage of usage during night hours)
        features['night_ratio'] = self._calculate_night_usage_ratio(all_data)
        
        # 5. productive_ratio (percentage of productive app usage)
        features['productive_ratio'] = self._calculate_productive_ratio(all_data)
        
        # 6. Additional features for insights (not used in ML models)
        features['social_ratio'] = self._calculate_social_ratio(all_data)
        features['entertainment_ratio'] = self._calculate_entertainment_ratio(all_data)
        features['focus_score'] = self._calculate_focus_score(all_data)
        
        print(f"Extracted features: {features}")
        return features
    
    def _combine_and_preprocess(
        self, 
        laptop_data: List[Dict], 
        mobile_data: List[Dict]
    ) -> pd.DataFrame:
        """Combine and preprocess laptop and mobile data"""
        records = []
        
        # Process laptop data
        for record in laptop_data:
            records.append({
                'timestamp': pd.to_datetime(record.get('timestamp')),
                'device_type': 'laptop',
                'app_name': record.get('active_app', 'unknown').lower(),
                'duration_minutes': record.get('usage_duration', 0),
                'session_length': record.get('session_length', 0),
                'category': self._categorize_app(record.get('active_app', 'unknown')),
                'is_idle': record.get('idle_time', 0) > 5,  # >5 minutes idle
                'time_of_day': record.get('time_of_day', 'unknown')
            })
        
        # Process mobile data
        for record in mobile_data:
            records.append({
                'timestamp': pd.to_datetime(record.get('timestamp')),
                'device_type': 'mobile',
                'app_name': record.get('app_name', 'unknown').lower(),
                'duration_minutes': record.get('screen_time', 0),
                'session_length': record.get('screen_time', 0),  # Approximate
                'category': record.get('category', 'unknown').lower(),
                'is_idle': False,  # Mobile doesn't track idle
                'time_of_day': self._get_time_of_day(pd.to_datetime(record.get('timestamp')))
            })
        
        if not records:
            return pd.DataFrame()
        
        df = pd.DataFrame(records)
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Filter last 24 hours
        cutoff = datetime.now() - timedelta(hours=24)
        df = df[df['timestamp'] >= cutoff]
        
        return df
    
    def _calculate_screen_time(self, df: pd.DataFrame) -> float:
        """Calculate total screen time in hours (feature 1)"""
        if len(df) == 0:
            return 0.0
        
        total_minutes = df['duration_minutes'].sum()
        return round(total_minutes / 60, 2)  # Convert to hours
    
    def _calculate_avg_session_length(self, df: pd.DataFrame) -> float:
        """Calculate average session length in hours (feature 2)"""
        if len(df) == 0:
            return 0.0
        
        # Group by approximate sessions (gaps > 5 minutes)
        df = df.sort_values('timestamp')
        df['time_diff'] = df['timestamp'].diff().dt.total_seconds() / 60
        
        # New session if gap > 5 minutes
        df['session_id'] = (df['time_diff'] > 5).cumsum()
        
        # Calculate session lengths
        session_lengths = df.groupby('session_id')['duration_minutes'].sum()
        
        if len(session_lengths) == 0:
            return 0.0
        
        avg_session_minutes = session_lengths.mean()
        return round(avg_session_minutes / 60, 2)  # Convert to hours
    
    def _calculate_break_frequency(self, df: pd.DataFrame) -> float:
        """Calculate break frequency per hour (feature 3)"""
        if len(df) < 2:
            return 0.0
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Calculate time gaps between usage
        df['time_diff'] = df['timestamp'].diff().dt.total_seconds() / 60
        
        # Count breaks (gaps > 5 minutes)
        breaks = (df['time_diff'] > 5).sum()
        
        # Calculate breaks per hour of usage
        total_hours = self._calculate_screen_time(df)
        if total_hours == 0:
            return 0.0
        
        return round(breaks / total_hours, 2)
    
    def _calculate_night_usage_ratio(self, df: pd.DataFrame) -> float:
        """Calculate percentage of usage during night hours (10 PM - 6 AM) (feature 4)"""
        if len(df) == 0:
            return 0.0
        
        # Extract hour from timestamp
        df['hour'] = df['timestamp'].dt.hour
        
        # Night hours: 22 (10 PM) to 6 (6 AM)
        night_usage = df[
            (df['hour'] >= 22) | (df['hour'] < 6)
        ]['duration_minutes'].sum()
        
        total_usage = df['duration_minutes'].sum()
        
        if total_usage == 0:
            return 0.0
        
        return round(night_usage / total_usage, 2)
    
    def _calculate_productive_ratio(self, df: pd.DataFrame) -> float:
        """Calculate percentage of productive app usage (feature 5)"""
        if len(df) == 0:
            return 0.0
        
        # Categorize apps if not already categorized
        if 'category' not in df.columns:
            df['category'] = df['app_name'].apply(self._categorize_app)
        
        # Calculate productive usage
        productive_mask = df['category'].isin(['productive', 'development', 'work'])
        productive_minutes = df[productive_mask]['duration_minutes'].sum()
        
        total_minutes = df['duration_minutes'].sum()
        
        if total_minutes == 0:
            return 0.0
        
        return round(productive_minutes / total_minutes, 2)
    
    def _calculate_social_ratio(self, df: pd.DataFrame) -> float:
        """Calculate percentage of social app usage"""
        if len(df) == 0:
            return 0.0
        
        if 'category' not in df.columns:
            df['category'] = df['app_name'].apply(self._categorize_app)
        
        social_mask = df['category'] == 'social'
        social_minutes = df[social_mask]['duration_minutes'].sum()
        
        total_minutes = df['duration_minutes'].sum()
        
        if total_minutes == 0:
            return 0.0
        
        return round(social_minutes / total_minutes, 2)
    
    def _calculate_entertainment_ratio(self, df: pd.DataFrame) -> float:
        """Calculate percentage of entertainment app usage"""
        if len(df) == 0:
            return 0.0
        
        if 'category' not in df.columns:
            df['category'] = df['app_name'].apply(self._categorize_app)
        
        entertainment_mask = df['category'] == 'entertainment'
        entertainment_minutes = df[entertainment_mask]['duration_minutes'].sum()
        
        total_minutes = df['duration_minutes'].sum()
        
        if total_minutes == 0:
            return 0.0
        
        return round(entertainment_minutes / total_minutes, 2)
    
    def _calculate_focus_score(self, df: pd.DataFrame) -> float:
        """Calculate focus score based on session continuity"""
        if len(df) == 0:
            return 0.0
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Calculate uninterrupted work sessions (>30 minutes of productive apps)
        df['is_productive'] = df['category'].isin(['productive', 'development', 'work'])
        df['session_change'] = (~df['is_productive']).astype(int).cumsum()
        
        productive_sessions = []
        for _, session_df in df.groupby('session_change'):
            if session_df['is_productive'].any():
                session_duration = session_df['duration_minutes'].sum()
                if session_duration >= 30:  # Minimum 30 minutes for focus session
                    productive_sessions.append(session_duration)
        
        if not productive_sessions:
            return 0.0
        
        # Score based on number and length of focus sessions
        total_focus_time = sum(productive_sessions)
        avg_focus_session = total_focus_time / len(productive_sessions)
        
        # Normalize to 0-100 scale
        score = min(100, (len(productive_sessions) * 10) + (avg_focus_session / 60 * 5))
        return round(score, 2)
    
    def _categorize_app(self, app_name: str) -> str:
        """Categorize app based on name"""
        app_lower = str(app_name).lower()
        
        if any(prod in app_lower for prod in self.productive_apps):
            return 'productive'
        elif any(social in app_lower for social in self.social_apps):
            return 'social'
        elif any(ent in app_lower for ent in self.entertainment_apps):
            return 'entertainment'
        elif 'browser' in app_lower or 'chrome' in app_lower or 'firefox' in app_lower:
            return 'browser'
        elif 'code' in app_lower or 'pycharm' in app_lower or 'ide' in app_lower:
            return 'development'
        elif 'slack' in app_lower or 'teams' in app_lower or 'zoom' in app_lower:
            return 'communication'
        else:
            return 'other'
    
    def _get_time_of_day(self, timestamp: datetime) -> str:
        """Get time of day category"""
        hour = timestamp.hour
        
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 22:
            return 'evening'
        else:
            return 'night'
    
    def _get_default_features(self) -> Dict[str, float]:
        """Return default feature values when no data is available"""
        return {
            'screen_time': 0.0,
            'avg_session': 0.0,
            'breaks': 0.0,
            'night_ratio': 0.0,
            'productive_ratio': 0.0,
            'social_ratio': 0.0,
            'entertainment_ratio': 0.0,
            'focus_score': 0.0
        }
    
    def prepare_for_classification(self, features: Dict) -> np.ndarray:
        """Prepare features for fatigue classification model"""
        # Extract only the features used in classification
        X = np.array([[
            features.get('screen_time', 0),
            features.get('avg_session', 0),
            features.get('breaks', 0),
            features.get('night_ratio', 0),
            features.get('productive_ratio', 0)
        ]])
        return X
    
    def prepare_for_regression(self, features: Dict, fatigue_score: float) -> np.ndarray:
        """Prepare features for productivity loss regression model"""
        # Extract features used in regression (includes fatigue_score)
        X = np.array([[
            features.get('screen_time', 0),
            features.get('avg_session', 0),
            features.get('breaks', 0),
            features.get('night_ratio', 0),
            features.get('productive_ratio', 0),
            fatigue_score  # This comes from classification prediction
        ]])
        return X


# Example usage for testing
if __name__ == "__main__":
    print("Testing Live Feature Extractor...")
    
    # Create mock live data
    mock_laptop_data = [
        {
            'timestamp': '2024-01-01T09:00:00',
            'active_app': 'VS Code',
            'usage_duration': 120,
            'session_length': 120,
            'idle_time': 0,
            'time_of_day': 'morning'
        },
        {
            'timestamp': '2024-01-01T11:00:00',
            'active_app': 'Chrome',
            'usage_duration': 60,
            'session_length': 60,
            'idle_time': 5,
            'time_of_day': 'morning'
        }
    ]
    
    mock_mobile_data = [
        {
            'timestamp': '2024-01-01T12:00:00',
            'app_name': 'WhatsApp',
            'screen_time': 30,
            'category': 'Social'
        }
    ]
    
    extractor = LiveFeatureExtractor()
    features = extractor.extract_features_from_live_data(mock_laptop_data, mock_mobile_data)
    
    print("\nExtracted Features:")
    for key, value in features.items():
        print(f"  {key}: {value}")
    
    # Prepare for ML models
    X_class = extractor.prepare_for_classification(features)
    print(f"\nFeatures for classification: {X_class}")