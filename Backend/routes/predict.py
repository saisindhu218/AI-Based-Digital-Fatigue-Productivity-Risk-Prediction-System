import sys
import os

# Fix path so db.py can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, backend_dir)

from flask import Blueprint, jsonify
from datetime import datetime, timedelta
from db import metrics_collection
import pandas as pd
import joblib

predict_bp = Blueprint("predict", __name__)

# Load ML model
model = joblib.load("ml/fatigue_model.pkl")
encoder = joblib.load("ml/label_encoder.pkl")

@predict_bp.route("/predict", methods=["GET"])
def predict():

    fifteen_minutes_ago = datetime.utcnow() - timedelta(minutes=15)

    data = list(metrics_collection.find({
        "timestamp": {"$gte": fifteen_minutes_ago}
    }))

    if len(data) < 5:
        return jsonify({"error": "Not enough data"})

    df = pd.DataFrame(data)

    avg_screen_time = df["screen_time"].mean()
    total_idle_time = df["idle_time"].sum()
    avg_keystrokes = df["keystrokes"].mean()
    avg_mouse = df["mouse_movements"].mean()
    avg_cognitive_load = df["cognitive_load"].mean()
    session_length = len(df)

    features = [[
        avg_screen_time,
        total_idle_time,
        avg_keystrokes,
        avg_mouse,
        avg_cognitive_load,
        session_length
    ]]

    prediction = model.predict(features)
    fatigue_level = encoder.inverse_transform(prediction)[0]

    productivity_score = (
        (avg_cognitive_load * 0.5) +
        (1 - (total_idle_time / 900)) * 0.3 +
        (avg_keystrokes / 200) * 0.2
    ) * 100

    productivity_score = round(max(0, min(productivity_score, 100)), 2)

    return jsonify({
        "fatigue_level": fatigue_level,
        "productivity_score": productivity_score
    })