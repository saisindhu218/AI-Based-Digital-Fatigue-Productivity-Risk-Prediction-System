from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from src.models.usage import PredictionRequest, PredictionResponse
from src.services.ml_service import ml_service
from src.database import db

router = APIRouter(prefix="/prediction", tags=["predictions"])

@router.post("/predict", response_model=PredictionResponse)
async def predict_fatigue(request: PredictionRequest):
    """Generate predictions based on recent usage data"""
    
    if not db.db:
        raise HTTPException(
            status_code=503,
            detail="Database not available"
        )
    
    try:
        # Get recent usage data (last 4 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=4)
        
        # Get laptop usage data
        laptop_data_cursor = db.db.usage_data.find({
            "user_id": request.user_id,
            "data_type": "laptop",
            "timestamp": {"$gte": cutoff_time}
        }).sort("timestamp", -1).limit(50)
        
        laptop_data = await laptop_data_cursor.to_list(length=50)
        
        # Get mobile usage data
        mobile_data_cursor = db.db.usage_data.find({
            "user_id": request.user_id,
            "data_type": "mobile",
            "timestamp": {"$gte": cutoff_time}
        }).sort("timestamp", -1).limit(50)
        
        mobile_data = await mobile_data_cursor.to_list(length=50)
        
        if not laptop_data and not mobile_data:
            # Return default prediction if no data
            return PredictionResponse(
                fatigue_score=50.0,
                fatigue_level="Medium",
                productivity_loss=5.0,
                confidence=0.7,
                peak_hours=["09:00-12:00", "15:00-17:00"],
                fatigue_prone_windows=["13:00-15:00", "23:00-01:00"],
                recommendations=[
                    "Start tracking your device usage",
                    "Take regular breaks",
                    "Maintain consistent sleep schedule"
                ]
            )
        
        # Combine all usage data for feature extraction
        all_usage_data = []
        
        # Convert laptop data to format expected by ml_service
        for item in laptop_data:
            all_usage_data.append({
                "duration": item.get("usage_duration", 0) * 60,  # Convert to seconds
                "timestamp": item.get("timestamp", datetime.utcnow()),
                "hour": item.get("timestamp", datetime.utcnow()).hour if item.get("timestamp") else 0,
                "category": "work" if item.get("active_app") in ["vscode", "pycharm", "word", "excel", "code"] else "other"
            })
        
        # Convert mobile data
        for item in mobile_data:
            all_usage_data.append({
                "duration": item.get("screen_time", 0) * 60,  # Convert to seconds
                "timestamp": item.get("timestamp", datetime.utcnow()),
                "hour": item.get("timestamp", datetime.utcnow()).hour if item.get("timestamp") else 0,
                "category": item.get("category", "other")
            })
        
        # Extract features from the usage data
        features = ml_service.extract_features_from_usage(all_usage_data)
        
        # Get predictions
        fatigue_prediction = ml_service.predict_fatigue(features)
        fatigue_score = fatigue_prediction.get("score", 50)
        fatigue_level = fatigue_prediction.get("level", "Medium")
        confidence = fatigue_prediction.get("confidence", 0.8)
        
        productivity_prediction = ml_service.predict_productivity_loss(features)
        productivity_loss = productivity_prediction.get("loss_hours", 5.0)
        
        # Get productivity zones (mock data for now)
        peak_hours = ["09:00-12:00", "15:00-17:00"]
        fatigue_prone_windows = ["13:00-15:00", "23:00-01:00"]
        
        # Generate recommendations
        recommendations = []
        if fatigue_level == "High":
            recommendations.append("Take a 15-minute break immediately")
            recommendations.append("Avoid screen time for next hour")
            recommendations.append("Consider light stretching exercises")
            recommendations.append("Stay hydrated")
        elif fatigue_level == "Medium":
            recommendations.append("Take short breaks every 45 minutes")
            recommendations.append("Reduce screen brightness")
            recommendations.append("Consider a short walk")
            recommendations.append("Practice 20-20-20 rule")
        else:
            recommendations.append("Maintain current work pace")
            recommendations.append("Stay hydrated")
            recommendations.append("Practice 20-20-20 rule")
            recommendations.append("Get adequate sleep")
        
        return PredictionResponse(
            fatigue_score=float(fatigue_score),
            fatigue_level=fatigue_level,
            productivity_loss=float(productivity_loss),
            confidence=float(confidence),
            peak_hours=peak_hours,
            fatigue_prone_windows=fatigue_prone_windows,
            recommendations=recommendations
        )
        
    except Exception as e:
        print(f"❌ Error in prediction: {e}")
        # Return default prediction on error
        return PredictionResponse(
            fatigue_score=50.0,
            fatigue_level="Medium",
            productivity_loss=5.0,
            confidence=0.6,
            peak_hours=["09:00-12:00", "15:00-17:00"],
            fatigue_prone_windows=["13:00-15:00", "23:00-01:00"],
            recommendations=[
                "System is processing your data",
                "Continue tracking your usage",
                "Take regular breaks"
            ]
        )

@router.get("/user/{user_id}/history")
async def get_prediction_history(user_id: str, limit: int = 20):
    """Get prediction history for a user"""
    
    # In production, you would store predictions in a separate collection
    # For demo, we'll generate a mock history
    
    history = []
    base_time = datetime.utcnow()
    
    for i in range(min(limit, 20)):
        time_offset = timedelta(hours=i * 2)
        prediction_time = base_time - time_offset
        
        # Mock predictions for demo
        fatigue_score = 30 + (i * 3) % 70
        if fatigue_score > 70:
            fatigue_level = "High"
        elif fatigue_score > 40:
            fatigue_level = "Medium"
        else:
            fatigue_level = "Low"
        
        history.append({
            "timestamp": prediction_time.isoformat(),
            "fatigue_score": float(fatigue_score),
            "fatigue_level": fatigue_level,
            "productivity_loss": float(5 + (i * 0.5) % 15),
            "peak_hours": ["09:00-12:00", "15:00-17:00"],
            "fatigue_windows": ["13:00-15:00", "23:00-01:00"]
        })
    
    return {
        "user_id": user_id,
        "predictions": history,
        "total": len(history)
    }