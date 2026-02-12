from flask import Blueprint, request, jsonify
import joblib
import numpy as np

predict_bp = Blueprint("predict", __name__, url_prefix="/predict")

model = joblib.load("ml/fatigue_model.pkl")
encoder = joblib.load("ml/label_encoder.pkl")

@predict_bp.route("/", methods=["POST"])
def predict():
    data = request.json

    features = np.array([[
        data["screen_time"],
        data["idle_time"]
    ]])

    prediction = model.predict(features)
    label = encoder.inverse_transform(prediction)

    return jsonify({"fatigue_level": label[0]})
