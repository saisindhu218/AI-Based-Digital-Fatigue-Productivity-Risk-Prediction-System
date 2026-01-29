from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from models.usage import PredictionRequest, PredictionResponse
from services.ml_service import ml_service
from database import db, sync_db

router = APIRouter(prefix="/prediction", tags=["predictions"])

@router.post("/predict", response_model=PredictionResponse)
async def predict_fatigue(request: PredictionRequest):
    """Generate predictions based on recent usage data"""
    
    # Get recent usage data (last 4 hours)
    cutoff_time = datetime.utcnow() - timedelta(hours=4)
    
    # Get laptop usage data
    laptop_data_cursor = sync_db.usage_data.find({
        "user_id": request.user_id,
        "data_type": "laptop",
        "timestamp": {"$gte": cutoff_time}
    }).sort("timestamp", -1).limit(50)
    
    laptop_data = list(laptop_data_cursor)
    
    # Get mobile usage data
    mobile_data_cursor = sync_db.usage_data.find({
        "user_id": request.user_id,
        "data_type": "mobile",
        "timestamp": {"$gte": cutoff_time}
    }).sort("timestamp", -1).limit(50)
    
    mobile_data = list(mobile_data_cursor)
    
    if not laptop_data and not mobile_data:
        raise HTTPException(
            status_code=404,
            detail="No recent usage data found for prediction"
        )
    
    # Aggregate data for features
    aggregated_laptop = {
        "usage_duration": sum(d.get("usage_duration", 0) for d in laptop_data),
        "session_length": (
            sum(d.get("session_length", 0) for d in laptop_data) / 
            max(len(laptop_data), 1)
        ),
        "idle_time": sum(d.get("idle_time", 0) for d in laptop_data),
        "keystrokes": sum(d.get("keystrokes", 0) for d in laptop_data),
        "mouse_clicks": sum(d.get("mouse_clicks", 0) for d in laptop_data)
    }
    
    aggregated_mobile = {
        "screen_time": sum(d.get("screen_time", 0) for d in mobile_data),
        "notifications_received": sum(d.get("notifications_received", 0) for d in mobile_data)
    }
    
    # Extract features from LIVE data
    features = ml_service.extract_features_from_live_data(
        aggregated_laptop, aggregated_mobile
    )
    
    # Get predictions
    fatigue_score, fatigue_level = ml_service.predict_fatigue(features)
    productivity_loss = ml_service.predict_productivity_loss(features)
    
    # Get productivity zones
    zones = ml_service.detect_productivity_zones({
        "laptop_data": laptop_data,
        "mobile_data": mobile_data
    })
    
    # Generate recommendations
    recommendations = ml_service.generate_recommendations(
        fatigue_score, fatigue_level, productivity_loss
    )
    
    return PredictionResponse(
        fatigue_score=fatigue_score,
        fatigue_level=fatigue_level,
        productivity_loss=productivity_loss,
        confidence=0.85,  # Example confidence score
        peak_hours=zones["peak_hours"],
        fatigue_prone_windows=zones["fatigue_prone_windows"],
        recommendations=recommendations
    )

@router.get("/user/{user_id}/history")
async def get_prediction_history(user_id: str, limit: int = 20):
    """Get prediction history for a user"""
    
    # In production, you would store predictions in a separate collection
    # For demo, we'll generate a mock history
    
    history = []
    base_time = datetime.utcnow()
    
    for i in range(limit):
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
            "fatigue_score": fatigue_score,
            "fatigue_level": fatigue_level,
            "productivity_loss": 5 + (i * 0.5) % 15,
            "peak_hours": ["09:00-12:00"],
            "fatigue_windows": ["14:00-16:00"]
        })
    
    return {
        "user_id": user_id,
        "predictions": history,
        "total": len(history)
    }