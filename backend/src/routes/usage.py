from fastapi import APIRouter
from datetime import datetime,timedelta
from src.database import db
from src.services.feature_extractor import LiveFeatureExtractor
from src.services.ml_service import ml_service
import uuid

router=APIRouter(prefix="/usage",tags=["usage"])
feature_extractor=LiveFeatureExtractor()

@router.post("/laptop")
async def receive_laptop_usage(data:dict):
    record={
        "_id":str(uuid.uuid4()),
        "user_id":data.get("user_id"),
        "device_id":data.get("device_id"),
        "session_id":data.get("session_id"),
        "timestamp":datetime.utcnow(),
        "data_type":"laptop",
        "active_app":data.get("active_app"),
        "app_category":data.get("app_category"),
        "usage_duration":data.get("usage_duration",1),
        "session_length_minutes":data.get("session_length_minutes",0),
        "idle_time_seconds":data.get("idle_time_seconds",0),
        "keystrokes":data.get("keystrokes",0),
        "mouse_clicks":data.get("mouse_clicks",0),
        "mouse_moves":data.get("mouse_moves",0),
        "app_switches":data.get("app_switches",0),
        "time_of_day":data.get("time_of_day")
    }
    await db.db.usage_data.insert_one(record)
    await run_prediction(data.get("user_id"))
    return {"status":"ok"}

@router.post("/laptop/batch")
async def receive_laptop_batch(payload:dict):
    records=payload.get("records",[])
    inserted=0
    for r in records:
        record={
            "_id":str(uuid.uuid4()),
            "user_id":r.get("user_id"),
            "device_id":r.get("device_id"),
            "session_id":r.get("session_id"),
            "timestamp":datetime.utcnow(),
            "data_type":"laptop",
            "active_app":r.get("active_app"),
            "app_category":r.get("app_category"),
            "usage_duration":r.get("usage_duration",1),
            "session_length_minutes":r.get("session_length_minutes",0),
            "idle_time_seconds":r.get("idle_time_seconds",0),
            "keystrokes":r.get("keystrokes",0),
            "mouse_clicks":r.get("mouse_clicks",0),
            "mouse_moves":r.get("mouse_moves",0),
            "app_switches":r.get("app_switches",0),
            "time_of_day":r.get("time_of_day")
        }
        await db.db.usage_data.insert_one(record)
        inserted+=1
    if inserted>0:
        await run_prediction(records[0].get("user_id"))
    return {"status":"ok","records_inserted":inserted}

@router.post("/mobile")
async def receive_mobile_usage(data:dict):
    record={
        "_id":str(uuid.uuid4()),
        "user_id":data.get("user_id"),
        "device_id":data.get("device_id"),
        "timestamp":datetime.utcnow(),
        "data_type":"mobile",
        "app_name":data.get("app_name"),
        "screen_time":data.get("screen_time"),
        "notifications_received":data.get("notifications_received")
    }
    await db.db.usage_data.insert_one(record)
    await run_prediction(data.get("user_id"))
    return {"status":"ok"}

async def run_prediction(user_id:str):
    cutoff=datetime.utcnow()-timedelta(hours=6)
    laptop_data=await db.db.usage_data.find({
        "user_id":user_id,
        "data_type":"laptop",
        "timestamp":{"$gte":cutoff}
    }).to_list(200)
    mobile_data=await db.db.usage_data.find({
        "user_id":user_id,
        "data_type":"mobile",
        "timestamp":{"$gte":cutoff}
    }).to_list(200)
    features=feature_extractor.extract_features_from_live_data(laptop_data,mobile_data,user_id)
    fatigue_result=ml_service.predict_fatigue(features)
    productivity_loss=ml_service.predict_productivity_loss(features)
    productivity_score=max(0,100-productivity_loss*5)
    prediction_record={
        "_id":str(uuid.uuid4()),
        "user_id":user_id,
        "timestamp":datetime.utcnow(),
        "fatigue_level":fatigue_result["level"],
        "fatigue_score":fatigue_result["score"],
        "confidence":fatigue_result["confidence"],
        "productivity_loss_hours":productivity_loss,
        "productivity_score":productivity_score
    }
    await db.db.predictions.insert_one(prediction_record)

@router.get("/user/{user_id}/recent")
async def get_recent_usage(user_id:str,hours:int=24):
    cutoff=datetime.utcnow()-timedelta(hours=hours)
    laptop=await db.db.usage_data.find({
        "user_id":user_id,
        "data_type":"laptop",
        "timestamp":{"$gte":cutoff}
    }).sort("timestamp",-1).to_list(500)
    mobile=await db.db.usage_data.find({
        "user_id":user_id,
        "data_type":"mobile",
        "timestamp":{"$gte":cutoff}
    }).sort("timestamp",-1).to_list(500)
    predictions=await db.db.predictions.find({
        "user_id":user_id,
        "timestamp":{"$gte":cutoff}
    }).sort("timestamp",-1).limit(50).to_list(50)
    return {"laptop_usage":laptop,"mobile_usage":mobile,"predictions":predictions}