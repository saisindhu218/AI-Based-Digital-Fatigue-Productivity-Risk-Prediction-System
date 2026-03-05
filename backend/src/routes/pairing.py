from fastapi import APIRouter, HTTPException
from datetime import datetime
from src.models.device import DeviceCreate, QRToken, DevicePairingStatus
from src.services.qr_service import QRService
from src.database import db
import uuid

router = APIRouter(prefix="/pairing", tags=["device-pairing"])

# store currently active user in memory
ACTIVE_USER = {"user_id": None}


@router.post("/save-user")
async def save_active_user(data: dict):

    user_id = data.get("user_id")

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")

    ACTIVE_USER["user_id"] = user_id

    return {
        "message": "Active user saved",
        "user_id": user_id
    }


@router.get("/active-user")
async def get_active_user():

    if not ACTIVE_USER["user_id"]:
        return {"user_id": None}

    return {"user_id": ACTIVE_USER["user_id"]}


@router.post("/generate-qr", response_model=QRToken)
async def generate_qr_code(device_data: DeviceCreate):

    existing_device = await db.db.devices.find_one({
        "device_id": device_data.device_id,
        "user_id": device_data.user_id
    })

    if existing_device:

        await db.db.devices.update_one(
            {"_id": existing_device["_id"]},
            {"$set": {"last_active": datetime.utcnow()}}
        )

        device_id = existing_device["_id"]

    else:

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

    qr_data = QRService.generate_qr_token(
        user_id=device_data.user_id,
        device_type=device_data.device_type
    )

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

    qr_token = await db.db.qr_tokens.find_one({"token": token})

    if not qr_token:
        raise HTTPException(status_code=404, detail="Invalid QR token")

    if datetime.utcnow() > qr_token["expires_at"]:

        await db.db.qr_tokens.delete_one({"_id": qr_token["_id"]})

        raise HTTPException(status_code=410, detail="QR token expired")

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

    await db.db.qr_tokens.delete_one({"_id": qr_token["_id"]})

    return {
        "message": "Devices paired successfully",
        "user_id": qr_token["user_id"]
    }