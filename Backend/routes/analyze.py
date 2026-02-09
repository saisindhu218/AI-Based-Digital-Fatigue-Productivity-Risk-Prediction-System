from flask import Blueprint, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
import pandas as pd
import joblib

analyze_bp = Blueprint("analyze", __name__)

# MongoDB
MONGO_URI = "mongodb+srv://fatigueproject:Taylorswift1988@forthsem.tdsu3zu.mongodb.net/digital_fatigue_db?retryWrites=true&w=majority&appName=forthsem"
client = MongoClient(MONGO_URI)
db = client["digital_fatigue_db"]

usage_col = db["device_usage"]
result_col = db["fatigue_results"]

# Load ML model
model = joblib.load("ml/fatigue_model.pkl")
label_encoder = joblib.load("ml/label_encoder.pkl")

@analyze_bp.route("/analyze", methods=["GET"])
def analyze_fatigue():
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)

    cursor = usage_col.find({
        "timestamp": {"$gte": start_time}
    })

    data = list(cursor)

    if len(data) < 10:
        return jsonify({"message": "Not enough data yet"}), 400

    df = pd.DataFrame(data)

    avg_screen_time = df["screen_time"].mean()
    avg_idle_time = df["idle_time"].mean()
    idle_ratio = avg_idle_time / max(avg_screen_time, 1)
    session_length = len(df)

    dominant_app = df["active_app"].mode()[0]

    # ML input
    X = [[avg_screen_time, avg_idle_time, idle_ratio, session_length]]
    prediction = model.predict(X)[0]
    fatigue_label = label_encoder.inverse_transform([prediction])[0]

    result = {
        "analysis_window": "1 hour",
        "avg_screen_time": round(avg_screen_time, 2),
        "avg_idle_time": round(avg_idle_time, 2),
        "idle_ratio": round(idle_ratio, 2),
        "dominant_app": dominant_app,
        "fatigue_level": fatigue_label,
        "timestamp": datetime.utcnow()
    }

    result_col.insert_one(result)

    return jsonify(result)
