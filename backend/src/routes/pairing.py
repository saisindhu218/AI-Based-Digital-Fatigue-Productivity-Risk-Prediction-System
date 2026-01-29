from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from models.device import DeviceCreate, DeviceInDB, QRToken, DevicePairingStatus
from services.qr_service import QRService
from database import db
import uuid

router = APIRouter(prefix="/pairing", tags=["device-pairing"])

@router.post("/generate-qr", response_model=QRToken)
async def generate_qr_code(device_data: DeviceCreate):
    """Generate QR code for device pairing"""
    
    # Check if device already exists
    existing_device = await db.db.devices.find_one({
        "device_id": device_data.device_id,
        "user_id": device_data.user_id
    })
    
    if existing_device:
        # Update existing device
        await db.db.devices.update_one(
            {"_id": existing_device["_id"]},
            {"$set": {"last_active": datetime.utcnow()}}
        )
        device_id = existing_device["_id"]
    else:
        # Create new device
        device_id = str(uuid.uuid4())
        device = {
            "_id": device_id,
            "device_id": device_data.device_id,
            "device_type": device_data.device_type,
            "device_name": device_data.device_name,
            "user_id": device_data.user_id,
            "paired_at": None,
            "pairing_status": DevicePairingStatus.PENDING,
            "last_active": datetime.utcnow()
        }
        await db.db.devices.insert_one(device)
    
    # Generate QR token
    qr_data = QRService.generate_qr_token(
        user_id=device_data.user_id,
        device_type=device_data.device_type
    )
    
    # Store QR token in database
    await db.db.qr_tokens.insert_one({
        "token": qr_data["token"],
        "user_id": device_data.user_id,
        "device_id": device_id,
        "device_type": device_data.device_type,
        "expires_at": qr_data["expires_at"],
        "created_at": datetime.utcnow()
    })
    
    return QRToken(
        token=qr_data["token"],
        qr_code_url=qr_data["qr_code_url"],
        expires_at=qr_data["expires_at"]
    )

@router.post("/verify-pairing")
async def verify_pairing(token: str, scanning_device_id: str):
    """Verify QR token and complete device pairing"""
    
    # Find QR token
    qr_token = await db.db.qr_tokens.find_one({"token": token})
    if not qr_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid QR token"
        )
    
    # Check if expired
    if datetime.utcnow() > qr_token["expires_at"]:
        await db.db.qr_tokens.delete_one({"_id": qr_token["_id"]})
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="QR token has expired"
        )
    
    # Update scanning device
    await db.db.devices.update_one(
        {"device_id": scanning_device_id},
        {
            "$set": {
                "user_id": qr_token["user_id"],
                "paired_at": datetime.utcnow(),
                "pairing_status": DevicePairingStatus.PAIRED,
                "last_active": datetime.utcnow()
            }
        }
    )
    
    # Update original device
    await db.db.devices.update_one(
        {"_id": qr_token["device_id"]},
        {
            "$set": {
                "paired_at": datetime.utcnow(),
                "pairing_status": DevicePairingStatus.PAIRED,
                "last_active": datetime.utcnow()
            }
        }
    )
    
    # Delete used QR token
    await db.db.qr_tokens.delete_one({"_id": qr_token["_id"]})
    
    # Add devices to user's device list
    await db.db.users.update_one(
        {"_id": qr_token["user_id"]},
        {
            "$addToSet": {
                "devices": {
                    "$each": [qr_token["device_id"], scanning_device_id]
                }
            }
        }
    )
    
    return {
        "message": "Devices paired successfully",
        "user_id": qr_token["user_id"]
    }