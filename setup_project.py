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

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

def run_command(cmd, cwd=None):
    """Run shell command and return output"""
    print(f"  Running: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"  Error: {result.stderr}")
        return result
    except Exception as e:
        print(f"  Command failed: {e}")
        return None

def check_python():
    """Check Python version"""
    print_header("Checking Python Installation")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current: Python {sys.version}")
        print("\nPlease install Python 3.8 or later from:")
        print("   https://www.python.org/downloads/")
        return False
    
    print(f"✅ Python {sys.version} detected")
    return True

def check_mongodb():
    """Check if MongoDB is installed"""
    print_header("Checking MongoDB")
    
    system = platform.system()
    
    if system == "Windows":
        # Check MongoDB service on Windows
        result = run_command("sc query MongoDB")
        if result and "RUNNING" in result.stdout:
            print("✅ MongoDB is running")
            return True
        else:
            print("⚠️ MongoDB not found or not running")
            print("\nTo install MongoDB on Windows:")
            print("1. Download from: https://www.mongodb.com/try/download/community")
            print("2. Install MongoDB Community Edition")
            print("3. Run MongoDB as a service")
            return False
    
    elif system == "Darwin":  # macOS
        result = run_command("brew services list | grep mongodb")
        if result and "started" in result.stdout:
            print("✅ MongoDB is running")
            return True
        else:
            print("⚠️ MongoDB not found or not running")
            print("\nTo install MongoDB on macOS:")
            print("1. Install Homebrew if not installed:")
            print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            print("2. Install MongoDB:")
            print("   brew tap mongodb/brew")
            print("   brew install mongodb-community")
            print("3. Start MongoDB:")
            print("   brew services start mongodb/brew/mongodb-community")
            return False
    
    else:  # Linux
        result = run_command("systemctl is-active mongod")
        if result and "active" in result.stdout:
            print("✅ MongoDB is running")
            return True
        else:
            print("⚠️ MongoDB not found or not running")
            print("\nTo install MongoDB on Linux:")
            print("1. Follow instructions at: https://docs.mongodb.com/manual/administration/install-on-linux/")
            print("2. Start MongoDB:")
            print("   sudo systemctl start mongod")
            print("   sudo systemctl enable mongod")
            return False

def setup_backend():
    """Setup Python backend"""
    print_header("Setting Up Backend")
    
    backend_dir = Path("backend")
    
    # Create virtual environment
    print("Creating Python virtual environment...")
    result = run_command("python -m venv venv", cwd=backend_dir)
    if not result:
        return False
    
    # Install requirements
    print("\nInstalling Python dependencies...")
    
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    # Upgrade pip first
    run_command(f"{pip_cmd} install --upgrade pip", cwd=backend_dir)
    
    # Install requirements
    result = run_command(
        f"{pip_cmd} install -r requirements.txt", 
        cwd=backend_dir
    )
    
    if result and result.returncode == 0:
        print("✅ Backend dependencies installed")
        return True
    else:
        print("❌ Failed to install backend dependencies")
        return False

def setup_web_app():
    """Setup web application"""
    print_header("Setting Up Web Application")
    
    print("Web app is static HTML/JS - no setup needed!")
    print("✅ Web app ready")
    return True

def setup_mobile_app():
    """Check Flutter setup"""
    print_header("Checking Mobile App Setup")
    
    # Check if Flutter is installed
    result = run_command("flutter --version")
    if result and result.returncode == 0:
        print("✅ Flutter is installed")
        print(f"   {result.stdout.splitlines()[0]}")
        
        # Check Android/iOS setup
        print("\nChecking device setup...")
        devices = run_command("flutter devices")
        if devices:
            print(devices.stdout)
        
        return True
    else:
        print("⚠️ Flutter not found")
        print("\nTo install Flutter:")
        print("1. Download from: https://flutter.dev/docs/get-started/install")
        print("2. Add to PATH")
        print("3. Run: flutter doctor")
        return False

def train_ml_models():
    """Train ML models from static data"""
    print_header("Training ML Models")
    
    data_science_dir = Path("data_science")
    
    # Check if dataset exists
    dataset = data_science_dir / "datasets" / "digital_usage_data.csv"
    if not dataset.exists():
        print("❌ Dataset not found")
        print(f"   Expected: {dataset}")
        print("\nPlease place your friend's dataset at:")
        print("   data_science/datasets/digital_usage_data.csv")
        return False
    
    # Install required packages
    print("Installing ML dependencies...")
    result = run_command("pip install pandas scikit-learn joblib numpy")
    
    # Train models
    print("\nTraining ML models...")
    result = run_command("python train_models.py", cwd=data_science_dir)
    
    if result and result.returncode == 0:
        print("✅ ML models trained and saved")
        return True
    else:
        print("❌ Failed to train ML models")
        return False

def create_env_file():
    """Create .env file from example"""
    print_header("Creating Configuration File")
    
    backend_dir = Path("backend")
    env_example = backend_dir / ".env.example"
    env_file = backend_dir / ".env"
    
    if env_example.exists() and not env_file.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("   Please edit 'backend/.env' with your configuration")
        return True
    elif env_file.exists():
        print("✅ .env file already exists")
        return True
    else:
        print("❌ .env.example not found")
        return False

def setup_complete():
    """Print completion message"""
    print_header("SETUP COMPLETE")
    
    print("🎉 Digital Fatigue Prediction System is ready!")
    print("\nNext steps:")
    print("1. Edit configuration:")
    print("   nano backend/.env")
    print("\n2. Start MongoDB (if not already running):")
    
    system = platform.system()
    if system == "Windows":
        print("   Run 'MongoDB' from Start Menu")
    elif system == "Darwin":
        print("   brew services start mongodb-community")
    else:
        print("   sudo systemctl start mongod")
    
    print("\n3. Run the system:")
    print("   python run_project.py")
    print("\n4. Open in browser:")
    print("   http://localhost:8080")
    print("\n5. For mobile app:")
    print("   cd mobile-app")
    print("   flutter run")

def main():
    """Main setup function"""
    print_header("DIGITAL FATIGUE PREDICTION SYSTEM SETUP")
    
    # Check requirements
    if not check_python():
        sys.exit(1)
    
    # Check MongoDB
    if not check_mongodb():
        print("\n⚠️ Continuing without MongoDB...")
        print("   You'll need to install MongoDB before running the app")
        cont = input("Continue anyway? (y/n): ")
        if cont.lower() != 'y':
            sys.exit(1)
    
    # Setup components
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
        print("\n❌ Setup incomplete. Please fix the issues above.")

if __name__ == "__main__":
    main()