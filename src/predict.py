import pandas as pd
import joblib
import os

print("📂 Loading dataset...")

DATA_PATH = "../datasets/usage_with_productivity_zones.csv"
MODEL_PATH = "../ml_models/fatigue_classifier.pkl"
ENCODER_PATH = "../ml_models/fatigue_label_encoder.pkl"
OUTPUT_PATH = "../datasets/predicted_fatigue_results.csv"

# Load dataset
df = pd.read_csv(DATA_PATH)
print("✅ Dataset loaded")
print("🧾 Columns found:", df.columns.tolist())

# Load model & encoder
model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)
print("✅ Model and encoder loaded")

# ✅ FEATURES MUST MATCH TRAINING
feature_columns = [
    "screen_time",
    "avg_session",
    "breaks",
    "night_ratio",
    "productive_ratio"
]

X = df[feature_columns]

# Predict
print("🧠 Running predictions...")
predicted = model.predict(X)
df["predicted_fatigue"] = label_encoder.inverse_transform(predicted)

# Save output
df.to_csv(OUTPUT_PATH, index=False)

print("🎉 SUCCESS!")
print(f"📁 File saved at: {OUTPUT_PATH}")
