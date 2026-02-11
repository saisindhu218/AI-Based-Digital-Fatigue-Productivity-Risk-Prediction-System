import sys
import os
import pandas as pd
import joblib

# Allow importing db
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db import collection


# ========================
# Load model & encoder
# ========================
model = joblib.load("fatigue_model.pkl")
label_encoder = joblib.load("label_encoder.pkl")


# ========================
# Fetch last 1 hour data
# ========================
data = list(
    collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(60)
)

if not data:
    raise ValueError("No recent data found")

df = pd.DataFrame(data)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# ========================
# Aggregate last hour
# ========================
avg_screen_time = df["screen_time"].mean()
total_idle_time = df["idle_time"].sum()

X = pd.DataFrame([{
    "avg_screen_time": avg_screen_time,
    "total_idle_time": total_idle_time
}])

# ========================
# Predict
# ========================
prediction = model.predict(X)[0]
fatigue_level = label_encoder.inverse_transform([prediction])[0]

print("📊 Last 1 hour analysis:")
print(f"Avg Screen Time: {avg_screen_time:.2f} min")
print(f"Total Idle Time: {total_idle_time:.2f} min")
print(f"🧠 Predicted Fatigue Level: {fatigue_level}")
