#!/usr/bin/env python3
"""
One-click setup for Digital Fatigue Prediction System
Run this once to setup the entire project
"""
import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

# ===========================
# SAFE COMMAND RUNNER (FIXED)
# ===========================
def print_header(text):
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def run_command(cmd, cwd=None):
    """Run shell command safely (UTF-8 FIX)"""
    print(f"  Running: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",   # ⭐ FIX: prevent cp1252 decode error
            errors="ignore"     # ⭐ FIX: ignore bad characters
        )

        if result.returncode != 0:
            print(f"  Error: {result.stderr}")

        return result

    except Exception as e:
        print(f"  Command failed: {e}")
        return None


# ===========================
# CHECK PYTHON
# ===========================
def check_python():
    print_header("Checking Python Installation")

    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current: Python {sys.version}")
        return False

    print(f"✅ Python {sys.version} detected")
    return True


# ===========================
# CHECK MONGODB
# ===========================
def check_mongodb():
    print_header("Checking MongoDB")

    system = platform.system()

    if system == "Windows":
        result = run_command("sc query MongoDB")
        if result and result.stdout and "RUNNING" in result.stdout:
            print("✅ MongoDB is running")
            return True
        else:
            print("⚠️ MongoDB not found or not running")
            return False

    return True


# ===========================
# SETUP BACKEND
# ===========================
def setup_backend():
    print_header("Setting Up Backend")

    backend_dir = Path("backend")

    print("Creating Python virtual environment...")
    run_command("python -m venv venv", cwd=backend_dir)

    print("\nInstalling Python dependencies...")

    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\python -m pip"
    else:
        pip_cmd = "venv/bin/python -m pip"

    # ⭐ FIXED pip upgrade command
    run_command(f"{pip_cmd} install --upgrade pip", cwd=backend_dir)

    result = run_command(
        f"{pip_cmd} install -r requirements.txt",
        cwd=backend_dir
    )

    if result and result.returncode == 0:
        print("✅ Backend dependencies installed")
        return True

    print("❌ Failed to install backend dependencies")
    return False


# ===========================
# WEB APP
# ===========================
def setup_web_app():
    print_header("Setting Up Web Application")
    print("Web app is static HTML/JS - no setup needed!")
    print("✅ Web app ready")
    return True


# ===========================
# ⭐ FIXED MOBILE APP CHECK
# ===========================
def setup_mobile_app():
    print_header("Checking Mobile App Setup")

    result = run_command("flutter --version")

    if result and result.returncode == 0:
        print("✅ Flutter is installed")

        # ⭐ SAFE PRINT (no crash now)
        if result.stdout:
            first_line = result.stdout.splitlines()
            if len(first_line) > 0:
                print(f"   {first_line[0]}")

        print("\nChecking device setup...")
        devices = run_command("flutter devices")
        if devices and devices.stdout:
            print(devices.stdout)

        return True

    print("⚠️ Flutter not found")
    return False


# ===========================
# TRAIN ML
# ===========================
def train_ml_models():
    print_header("Training ML Models")

    data_science_dir = Path("data_science")

    dataset = data_science_dir / "datasets" / "digital_usage_data.csv"
    if not dataset.exists():
        print("❌ Dataset not found")
        return False

    print("Installing ML dependencies...")
    run_command("pip install pandas scikit-learn joblib numpy")

    print("\nTraining ML models...")
    result = run_command("python train_models.py", cwd=data_science_dir)

    if result and result.returncode == 0:
        print("✅ ML models trained and saved")
        return True

    print("❌ Failed to train ML models")
    return False


# ===========================
# ENV FILE
# ===========================
def create_env_file():
    print_header("Creating Configuration File")

    backend_dir = Path("backend")
    env_example = backend_dir / ".env.example"
    env_file = backend_dir / ".env"

    if env_example.exists() and not env_file.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        return True

    if env_file.exists():
        print("✅ .env file already exists")
        return True

    print("❌ .env.example not found")
    return False


# ===========================
# COMPLETE
# ===========================
def setup_complete():
    print_header("SETUP COMPLETE")

    print("🎉 Digital Fatigue Prediction System is ready!")
    print("\nRun:")
    print("   python run_project.py")
    print("\nOpen:")
    print("   http://localhost:8080")


# ===========================
# MAIN
# ===========================
def main():
    print_header("DIGITAL FATIGUE PREDICTION SYSTEM SETUP")

    if not check_python():
        sys.exit(1)

    check_mongodb()

    steps = [
        ("Backend", setup_backend),
        ("Web App", setup_web_app),
        ("Mobile App", setup_mobile_app),
        ("ML Models", train_ml_models),
        ("Configuration", create_env_file),
    ]

    all_success = True
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n⚠️ {step_name} setup had issues")
            cont = input("Continue anyway? (y/n): ")
            if cont.lower() != 'y':
                all_success = False
                break

    if all_success:
        setup_complete()
    else:
        print("\n❌ Setup incomplete.")


if __name__ == "__main__":
    main()
