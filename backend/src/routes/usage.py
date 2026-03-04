from fastapi import APIRouter
from datetime import datetime, timedelta
from src.models.usage import LaptopUsageData, MobileUsageData
from src.database import db
from src.services.feature_extractor import LiveFeatureExtractor
from src.services.ml_service import ml_service
import uuid

router = APIRouter(prefix="/usage", tags=["usage-data"])

feature_extractor = LiveFeatureExtractor()


# ---------------- LAPTOP USAGE ----------------

@router.post("/laptop")
async def receive_laptop_usage(usage_data: LaptopUsageData):

    now = datetime.utcnow()

    usage_record = {
        "_id": str(uuid.uuid4()),
        "device_id": usage_data.device_id,
        "user_id": usage_data.user_id,
        "timestamp": now,
        "data_type": "laptop",

        "active_app": usage_data.active_app,
        "app_category": getattr(usage_data, "app_category", "MEDIUM"),

        "usage_duration": usage_data.usage_duration,
        "idle_time_seconds": getattr(usage_data, "idle_time_seconds", 0),

        "keystrokes": usage_data.keystrokes,
        "mouse_clicks": usage_data.mouse_clicks,
        "mouse_moves": getattr(usage_data, "mouse_moves", 0),
        "app_switches": getattr(usage_data, "app_switches", 0),
    }

    await db.db.usage_data.insert_one(usage_record)

    # -------- GET RECENT DATA FOR ML --------
    cutoff = datetime.utcnow() - timedelta(hours=6)

    laptop_data = await db.db.usage_data.find({
        "user_id": usage_data.user_id,
        "data_type": "laptop",
        "timestamp": {"$gte": cutoff}
    }).to_list(200)

    mobile_data = await db.db.usage_data.find({
        "user_id": usage_data.user_id,
        "data_type": "mobile",
        "timestamp": {"$gte": cutoff}
    }).to_list(200)

    # -------- FEATURE EXTRACTION --------
    features = feature_extractor.extract_features_from_live_data(
        laptop_data,
        mobile_data,
        usage_data.user_id
    )

    # -------- ML PREDICTIONS --------
    fatigue_result = ml_service.predict_fatigue(features)
    productivity_loss = ml_service.predict_productivity_loss(features)

    productivity_score = max(0, 100 - productivity_loss * 5)

    prediction_record = {
        "_id": str(uuid.uuid4()),
        "user_id": usage_data.user_id,
        "timestamp": now,

        "fatigue_level": fatigue_result["level"],
        "fatigue_score": fatigue_result["score"],
        "confidence": fatigue_result["confidence"],

        "productivity_loss_hours": productivity_loss,
        "productivity_score": productivity_score,
    }

    await db.db.predictions.insert_one(prediction_record)

    return {
        "status": "ok",
        "fatigue_score": fatigue_result["score"],
        "fatigue_level": fatigue_result["level"],
        "productivity_score": productivity_score
    }


# ---------------- MOBILE USAGE ----------------

@router.post("/mobile")
async def receive_mobile_usage(usage_data: MobileUsageData):

    now = datetime.utcnow()

    usage_record = {
        "_id": str(uuid.uuid4()),
        "device_id": usage_data.device_id,
        "user_id": usage_data.user_id,
        "timestamp": now,
        "data_type": "mobile",

        "app_name": usage_data.app_name,
        "screen_time": usage_data.screen_time,
        "notifications_received": usage_data.notifications_received
    }

    await db.db.usage_data.insert_one(usage_record)

    return {"status": "ok"}


# ---------------- GET RECENT ----------------

@router.get("/user/{user_id}/recent")
async def get_recent_usage(user_id: str, hours: int = 24):

    cutoff = datetime.utcnow() - timedelta(hours=hours)

    laptop = await db.db.usage_data.find({
        "user_id": user_id,
        "data_type": "laptop",
        "timestamp": {"$gte": cutoff}
    }).sort("timestamp", -1).to_list(500)

    mobile = await db.db.usage_data.find({
        "user_id": user_id,
        "data_type": "mobile",
        "timestamp": {"$gte": cutoff}
    }).sort("timestamp", -1).to_list(500)

    predictions = await db.db.predictions.find({
        "user_id": user_id,
        "timestamp": {"$gte": cutoff}
    }).sort("timestamp", -1).limit(50).to_list(50)

    total_laptop = sum(x.get("usage_duration", 0) for x in laptop)
    total_mobile = sum(x.get("screen_time", 0) for x in mobile)

    avg_fatigue = 0
    avg_productivity = 0

    if predictions:
        avg_fatigue = sum(x["fatigue_score"] for x in predictions) / len(predictions)
        avg_productivity = sum(x["productivity_score"] for x in predictions) / len(predictions)

    return {
        "laptop_usage": laptop,
        "mobile_usage": mobile,
        "predictions": predictions,
        "summary": {
            "total_screen_time_minutes": total_laptop + total_mobile,
            "avg_fatigue_score": round(avg_fatigue, 2),
            "avg_productivity_score": round(avg_productivity, 2)
        }
    }