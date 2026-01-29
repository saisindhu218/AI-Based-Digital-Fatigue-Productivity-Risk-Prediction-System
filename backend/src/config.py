import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME = "Digital Fatigue Prediction System"
    VERSION = "1.0.0"
    API_V1_STR = "/api/v1"
    
    # MongoDB
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME = "fatigue_prediction"
    
    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # ML Models Path
    ML_MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "ml_models")
    
    # QR Code
    QR_CODE_EXPIRY_MINUTES = 5
    
    # Notification Thresholds
    FATIGUE_HIGH_THRESHOLD = 70
    PRODUCTIVITY_LOSS_THRESHOLD = 10  # hours/week

settings = Settings()