from flask import Flask, jsonify
import pandas as pd
import joblib
from datetime import datetime, timedelta

# MongoDB
from db import collection

app = Flask(__name__)

# Load ML model
model = joblib.load("ml/fatigue_model.pkl")
label_encoder = joblib.load("ml/label_encoder.pkl")


@app.route("/")
def home():
    return jsonify({
        "status": "Digital Fatigue API is running"
    })


@app.route("/predict-fatigue", methods=["GET"])
def predict_fatigue():

    # Get last 1 hour data
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)

    data = list(collection.find(
        {"timestamp": {"$gte": one_hour_ago}},
        {"_id": 0}
    ))

    if not data:
        return jsonify({"error": "Not enough data yet"}), 400

    df = pd.DataFrame(data)

    # Feature aggregation
    avg_screen_time = df["screen_time"].mean()
    total_idle_time = df["idle_time"].sum()

    X = [[avg_screen_time, total_idle_time]]

    prediction = model.predict(X)[0]
    fatigue_level = label_encoder.inverse_transform([prediction])[0]

    return jsonify({
        "fatigue_level": fatigue_level,
        "avg_screen_time": round(avg_screen_time, 2),
        "total_idle_time": round(total_idle_time, 2)
    })


if __name__ == "__main__":
    app.run(debug=True)
