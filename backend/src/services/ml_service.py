import joblib
import numpy as np
from pathlib import Path
from src.config import settings


class MLService:

    def __init__(self):

        self.fatigue_classifier = None
        self.fatigue_label_encoder = None
        self.productivity_model = None

        self.is_loaded = False
        self.models_dir = Path(settings.ML_MODELS_DIR)

    # ---------------- LOAD MODELS ----------------

    def load_models(self):

        try:

            if not self.models_dir.exists():
                print("⚠️ ML models directory not found")
                self.is_loaded = False
                return

            classifier = self.models_dir / "fatigue_classifier.pkl"
            encoder = self.models_dir / "fatigue_label_encoder.pkl"
            productivity = self.models_dir / "productivity_loss_model.pkl"

            if classifier.exists():
                self.fatigue_classifier = joblib.load(classifier)

            if encoder.exists():
                self.fatigue_label_encoder = joblib.load(encoder)

            if productivity.exists():
                self.productivity_model = joblib.load(productivity)

            self.is_loaded = (
                self.fatigue_classifier is not None and
                self.fatigue_label_encoder is not None and
                self.productivity_model is not None
            )

            if self.is_loaded:
                print("✅ ML models loaded successfully")
            else:
                print("⚠️ Using behavioral prediction fallback")

        except Exception as e:

            print("❌ Model load error:", e)
            self.is_loaded = False

    # ---------------- FATIGUE PREDICTION ----------------

    def predict_fatigue(self, features: dict):

        try:

            screen = features.get("screen_time", 0)
            idle = features.get("idle_ratio", 0)
            switches = features.get("switches_per_hour", 0)
            keys = features.get("keystrokes_per_hour", 0)
            mouse = features.get("mouse_per_hour", 0)
            cognitive = features.get("cognitive_load", 2)
            night = features.get("night_ratio", 0)
            productive = features.get("productive_ratio", 0)

            behavioral_score = (
                screen * 12 +
                idle * 40 +
                switches * 1.5 +
                cognitive * 8 +
                night * 25 -
                productive * 20 -
                keys * 0.01 -
                mouse * 0.005
            )

            behavioral_score = max(0, min(100, behavioral_score))

            if self.is_loaded:

                X = np.array([[
                    features.get("screen_time", 0),
                    features.get("avg_session", 0),
                    features.get("breaks", 0),
                    features.get("night_ratio", 0),
                    features.get("productive_ratio", 0)
                ]])

                pred = self.fatigue_classifier.predict(X)[0]
                label = self.fatigue_label_encoder.inverse_transform([pred])[0]

                if hasattr(self.fatigue_classifier, "predict_proba"):
                    confidence = float(
                        max(self.fatigue_classifier.predict_proba(X)[0])
                    )
                else:
                    confidence = 0.85

                if label == "Low":
                    score = behavioral_score * 0.5
                elif label == "Medium":
                    score = behavioral_score * 0.8
                else:
                    score = behavioral_score

            else:

                score = behavioral_score
                confidence = 0.82

                if score < 35:
                    label = "Low"
                elif score < 65:
                    label = "Medium"
                else:
                    label = "High"

            return {
                "level": label,
                "score": round(float(score), 2),
                "confidence": confidence
            }

        except Exception as e:

            print("⚠️ Fatigue prediction error:", e)

            return {
                "level": "Medium",
                "score": 50,
                "confidence": 0.7
            }

    # ---------------- PRODUCTIVITY LOSS ----------------

    def predict_productivity_loss(self, features: dict, fatigue_score=None):

        try:

            screen = features.get("screen_time", 0)
            productive = features.get("productive_ratio", 0.5)
            focus = features.get("focus_score", 50)

            if fatigue_score is None:
                fatigue_score = self.predict_fatigue(features)["score"]

            behavioral_loss = (
                screen * 0.15 +
                fatigue_score * 0.03 +
                (1 - productive) * 3 +
                (100 - focus) * 0.02
            )

            behavioral_loss = max(0, min(8, behavioral_loss))

            if self.is_loaded:

                X = np.array([[
                    features.get("screen_time", 0),
                    features.get("avg_session", 0),
                    features.get("breaks", 0),
                    features.get("night_ratio", 0),
                    features.get("productive_ratio", 0),
                    fatigue_score
                ]])

                loss = float(self.productivity_model.predict(X)[0])

            else:

                loss = behavioral_loss

            return round(float(loss), 2)

        except Exception as e:

            print("⚠️ Productivity prediction error:", e)

            return 2.0

    # ---------------- PRODUCTIVITY SCORE ----------------

    def calculate_productivity_score(self, fatigue_score, productive_ratio, focus_score):

        try:

            score = (
                productive_ratio * 60 +
                focus_score * 0.3 +
                (100 - fatigue_score) * 0.4
            )

            return round(max(0, min(100, score)), 2)

        except:
            return 65.0


# GLOBAL INSTANCE
ml_service = MLService()
ml_service.load_models()