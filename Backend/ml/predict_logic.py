import sys
import os
import pandas as pd
import joblib

# Import DB
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db import collection


# Load model and encoder ONCE
model = joblib.load(os.path.join(os.path.dirname(__file__), "fatigue_model.pkl"))
label_encoder = joblib.load(os.path.join(os.path.dirname(__file__), "label_encoder.pkl"))


def predict_fatigue_last_hour():
    # Fetch last 60 minutes of data
    data = list(
        collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(60)
    )

    if not data:
        return {"error": "No data available"}

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    avg_screen_time = df["screen_time"].mean()
    total_idle_time = df["idle_time"].sum()

    X = pd.DataFrame([{
        "avg_screen_time": avg_screen_time,
        "total_idle_time": total_idle_time
    }])

    prediction = model.predict(X)[0]
    fatigue_level = label_encoder.inverse_transform([prediction])[0]

    return {
        "avg_screen_time": round(avg_screen_time, 2),
        "total_idle_time": round(total_idle_time, 2),
        "fatigue_level": fatigue_level
    }
