from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
from models.usage import LaptopUsageData, MobileUsageData
from database import db
import uuid

router = APIRouter(prefix="/usage", tags=["usage-data"])

@router.post("/laptop")
async def receive_laptop_usage(usage_data: LaptopUsageData):
    """Receive laptop usage data from background service"""
    
    # Store usage data
    usage_record = {
        "_id": str(uuid.uuid4()),
        "device_id": usage_data.device_id,
        "user_id": usage_data.user_id,
        "timestamp": usage_data.timestamp,
        "session_id": usage_data.session_id,
        "data_type": "laptop",
        "active_app": usage_data.active_app,
        "usage_duration": usage_data.usage_duration,
        "session_length": usage_data.session_length,
        "idle_time": usage_data.idle_time,
        "time_of_day": usage_data.time_of_day,
        "keystrokes": usage_data.keystrokes,
        "mouse_clicks": usage_data.mouse_clicks
    }
    
    await db.db.usage_data.insert_one(usage_record)
    
    # Update device last active
    await db.db.devices.update_one(
        {"device_id": usage_data.device_id},
        {"$set": {"last_active": datetime.utcnow()}}
    )
    
    return {"message": "Laptop usage data received", "record_id": usage_record["_id"]}

@router.post("/mobile")
async def receive_mobile_usage(usage_data: MobileUsageData):
    """Receive mobile usage data from Flutter app"""
    
    # Store usage data
    usage_record = {
        "_id": str(uuid.uuid4()),
        "device_id": usage_data.device_id,
        "user_id": usage_data.user_id,
        "timestamp": usage_data.timestamp,
        "session_id": usage_data.session_id,
        "data_type": "mobile",
        "app_name": usage_data.app_name,
        "screen_time": usage_data.screen_time,
        "category": usage_data.category,
        "notifications_received": usage_data.notifications_received
    }
    
    await db.db.usage_data.insert_one(usage_record)
    
    # Update device last active
    await db.db.devices.update_one(
        {"device_id": usage_data.device_id},
        {"$set": {"last_active": datetime.utcnow()}}
    )
    
    return {"message": "Mobile usage data received", "record_id": usage_record["_id"]}

@router.get("/user/{user_id}/recent")
async def get_recent_usage(user_id: str, hours: int = 24):
    """Get recent usage data for a user"""
    
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Get laptop usage
    laptop_data = await db.db.usage_data.find({
        "user_id": user_id,
        "data_type": "laptop",
        "timestamp": {"$gte": cutoff_time}
    }).sort("timestamp", -1).limit(100).to_list(100)
    
    # Get mobile usage
    mobile_data = await db.db.usage_data.find({
        "user_id": user_id,
        "data_type": "mobile",
        "timestamp": {"$gte": cutoff_time}
    }).sort("timestamp", -1).limit(100).to_list(100)
    
    # Calculate totals
    total_laptop_time = sum(d.get('usage_duration', 0) for d in laptop_data)
    total_mobile_time = sum(d.get('screen_time', 0) for d in mobile_data)
    
    return {
        "laptop_usage": laptop_data,
        "mobile_usage": mobile_data,
        "totals": {
            "laptop_minutes": total_laptop_time,
            "mobile_minutes": total_mobile_time,
            "total_screen_time": total_laptop_time + total_mobile_time
        },
        "period_hours": hours
    }