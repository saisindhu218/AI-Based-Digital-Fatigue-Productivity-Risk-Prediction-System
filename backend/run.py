#!/usr/bin/env python3
"""
Simple runner for FastAPI backend
"""

import sys
from pathlib import Path
import uvicorn

# --------------------------------------------------
# PATH SETUP (MOST IMPORTANT PART)
# --------------------------------------------------

# backend directory
BACKEND_DIR = Path(__file__).parent

# project root directory
PROJECT_ROOT = BACKEND_DIR.parent

# add paths so imports work everywhere
sys.path.insert(0, str(BACKEND_DIR / "src"))   # for app, routes, services
sys.path.insert(0, str(PROJECT_ROOT))          # for data_science

# --------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("   Digital Fatigue Prediction System - Backend")
    print("=" * 60)

    # Check .env
    env_file = BACKEND_DIR / ".env"
    if not env_file.exists():
        print("⚠️  Warning: .env file not found")
        print("   Copy .env.example to .env and configure it")

    # Check ML models
    models_dir = BACKEND_DIR / "ml_models"
    required_models = [
        "fatigue_classifier.pkl",
        "fatigue_label_encoder.pkl",
        "productivity_loss_model.pkl",
    ]

    missing_models = [m for m in required_models if not (models_dir / m).exists()]

    if missing_models:
        print("⚠️  Warning: Missing ML models:")
        for model in missing_models:
            print(f"   - {model}")
        print("\n   To create models, run:")
        print("   cd data_science")
        print("   python train_models.py")

    print("\n" + "=" * 60)
    print("Starting FastAPI server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("=" * 60)

    try:
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)
