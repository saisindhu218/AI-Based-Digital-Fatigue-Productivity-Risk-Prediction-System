from flask import Blueprint, jsonify
from pymongo import MongoClient
import joblib
import pandas as pd
import os

predict_bp = Blueprint("predict", __name__)

# MongoDB
MONGO_URI = "mongodb+srv://fatigueproject:Taylorswift1988@forthsem.tdsu3zu.mongodb.net/digital_fatigue_db?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["digital_fatigue_db"]

usage_col = db["device_usage"]
prediction_col = db["fatigue_predictions"]

# Load ML model
MODEL_PATH = os.path.join("ml", "fatigue_model.pkl")
ENCODER_PATH = os.path.join("ml", "label_encoder.pkl")

model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)

@predict_bp.route("/predict", methods=["GET"])
def predict_fatigue():
    data = list(usage_col.find().sort("timestamp", -1).limit(20))

    if not data:
        return jsonify({"error": "No data available"}), 400

    df = pd.DataFrame(data)

    # Feature engineering (VERY IMPORTANT)
    features = pd.DataFrame([{
        "screen_time": df["screen_time"].sum(),
        "idle_time": df["idle_time"].mean(),
        "night_ratio": 0.0  # placeholder for now
    }])

    prediction = model.predict(features)[0]
    fatigue_level = encoder.inverse_transform([prediction])[0]

    result = {
        "fatigue_level": fatigue_level,
        "screen_time": features["screen_time"][0],
        "idle_time": round(features["idle_time"][0], 2)
    }

    prediction_col.insert_one(result)

    return jsonify(result)
