from flask import Blueprint, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
import pandas as pd

analyze_bp = Blueprint("analyze", __name__, url_prefix="/analyze")

client = MongoClient(
    "YOUR_ATLAS_URI",
    tls=True,
    tlsAllowInvalidCertificates=True
)

db = client["digital_fatigue_db"]
collection = db["device_usage"]

@analyze_bp.route("/hourly")
def analyze_hourly():
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)

    data = list(collection.find({
        "timestamp": {"$gte": one_hour_ago}
    }))

    if not data:
        return jsonify({"message": "No data for last hour"})

    df = pd.DataFrame(data)

    result = {
        "avg_screen_time": df["screen_time"].mean(),
        "avg_idle_time": df["idle_time"].mean(),
        "records": len(df)
    }

    return jsonify(result)
