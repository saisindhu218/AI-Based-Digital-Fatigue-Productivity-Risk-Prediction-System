import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

df = pd.read_csv("../../datasets/final_fatigue_productivity_data.csv")

X = df[
    [
        "avg_screen_time",
        "total_idle_time",
        "avg_keystrokes",
        "avg_mouse",
        "avg_cognitive_load",
        "session_length"
    ]
]

y = df["fatigue_label"]

encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

model = RandomForestClassifier()
model.fit(X, y_encoded)

joblib.dump(model, "fatigue_model.pkl")
joblib.dump(encoder, "label_encoder.pkl")

print("Model trained successfully.")