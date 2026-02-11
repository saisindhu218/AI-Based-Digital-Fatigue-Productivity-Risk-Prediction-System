import sys
import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Allow importing from Backend/db.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db import collection


# ========================
# Load REAL data from MongoDB
# ========================
data = list(collection.find({}, {"_id": 0}))

if not data:
    raise ValueError("❌ No data found in MongoDB collection")

df = pd.DataFrame(data)

# ========================
# Timestamp processing
# ========================
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"])

# ✅ FIXED HERE (lowercase 'h')
df["hour"] = df["timestamp"].dt.floor("h")

# ========================
# Hourly aggregation
# ========================
hourly = df.groupby("hour").agg(
    avg_screen_time=("screen_time", "mean"),
    total_idle_time=("idle_time", "sum")
).reset_index()

# ========================
# Rule-based fatigue labeling
# ========================
def label_fatigue(row):
    if row["avg_screen_time"] >= 50 and row["total_idle_time"] < 10:
        return "High"
    elif row["avg_screen_time"] >= 30:
        return "Medium"
    else:
        return "Low"

hourly["fatigue_level"] = hourly.apply(label_fatigue, axis=1)

# ========================
# Encode labels
# ========================
le = LabelEncoder()
hourly["fatigue_encoded"] = le.fit_transform(hourly["fatigue_level"])

X = hourly[["avg_screen_time", "total_idle_time"]]
y = hourly["fatigue_encoded"]

# ========================
# Train model
# ========================
model = RandomForestClassifier(random_state=42)
model.fit(X, y)

# ========================
# Save model
# ========================
joblib.dump(model, "fatigue_model.pkl")
joblib.dump(le, "label_encoder.pkl")

print("✅ Model trained successfully using REAL laptop data")
