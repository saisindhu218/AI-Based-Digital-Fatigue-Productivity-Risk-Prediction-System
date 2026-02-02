#!/usr/bin/env python3
"""
One-click runner for Digital Fatigue Prediction System
Starts all components with a single command
"""
import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

def print_color(text, color):
    """Print colored text"""
    colors = {
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'reset': '\033[0m'
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")

class ComponentRunner:
    """Manages running different components"""
    
    def __init__(self):
        self.processes = []
        self.running = True
        
    def run_backend(self):
        """Start FastAPI backend"""
        print_color("\n🚀 Starting Backend API...", "blue")
        
        backend_dir = Path("backend")
        os.chdir(backend_dir)
        
        # Activate virtual environment
        if sys.platform == "win32":
            python_cmd = "venv\\Scripts\\python"
        else:
            python_cmd = "venv/bin/python"
        
        cmd = [python_cmd, "run.py"]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            self.processes.append(process)
            
            # Start thread to read output
            threading.Thread(
                target=self.read_output,
                args=(process, "BACKEND", "green"),
                daemon=True
            ).start()
            
            # Wait for backend to start
            time.sleep(3)
            return True
            
        except Exception as e:
            print_color(f"❌ Failed to start backend: {e}", "red")
            return False
    
    def run_web_server(self):
        """Start web server"""
        print_color("\n🌐 Starting Web Server...", "blue")
        
        web_dir = Path("web-app")
        os.chdir(web_dir)
        
        # Use Python's HTTP server
        cmd = [sys.executable, "-m", "http.server", "8080"]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            self.processes.append(process)
            
            threading.Thread(
                target=self.read_output,
                args=(process, "WEB", "yellow"),
                daemon=True
            ).start()
            
            # Wait for server to start
            time.sleep(2)
            return True
            
        except Exception as e:
            print_color(f"❌ Failed to start web server: {e}", "red")
            return False
    
    def run_laptop_collector(self):
        """Start laptop data collector"""
        print_color("\n💻 Starting Laptop Data Collector...", "blue")
        
        backend_dir = Path("backend")
        os.chdir(backend_dir)
        
        if sys.platform == "win32":
            python_cmd = "venv\\Scripts\\python"
        else:
            python_cmd = "venv/bin/python"
        
        cmd = [python_cmd, "-m", "src.laptop_collector.activity_logger"]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            self.processes.append(process)
            
            threading.Thread(
                target=self.read_output,
                args=(process, "LAPTOP", "blue"),
                daemon=True
            ).start()
            
            return True
            
        except Exception as e:
            print_color(f"⚠️ Laptop collector failed (normal if no GUI): {e}", "yellow")
            return False
    
    def read_output(self, process, component, color):
        """Read and print process output"""
        while self.running:
            line = process.stdout.readline()
            if line:
                print_color(f"[{component}] {line.rstrip()}", color)
            if process.poll() is not None:
                break
    
    def stop_all(self):
        """Stop all running processes"""
        print_color("\n\n🛑 Stopping all components...", "red")
        self.running = False
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        
        print_color("✅ All components stopped", "green")
    
    def check_mongodb(self):
        """Check if MongoDB is running"""
        print_color("\n🔍 Checking MongoDB...", "blue")
        
        try:
            if sys.platform == "win32":
                result = subprocess.run(
                    "sc query MongoDB",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if "RUNNING" in result.stdout:
                    print_color("✅ MongoDB is running", "green")
                    return True
            else:
                result = subprocess.run(
                    "mongosh --eval 'db.adminCommand(\"ping\")' --quiet",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print_color("✅ MongoDB is running", "green")
                    return True
        except:
            pass
        
        print_color("❌ MongoDB is not running", "red")
        print("\nPlease start MongoDB before continuing:")
        if sys.platform == "win32":
            print("   • Open Services (services.msc)")
            print("   • Start 'MongoDB' service")
        elif sys.platform == "darwin":
            print("   • Run: brew services start mongodb-community")
        else:
            print("   • Run: sudo systemctl start mongod")
        
        return False

def main():
    """Main runner function"""
    print_color("\n" + "="*60, "blue")
    print_color("   DIGITAL FATIGUE PREDICTION SYSTEM", "green")
    print_color("="*60, "blue")
    
    runner = ComponentRunner()
    
    try:
        # Check MongoDB
        if not runner.check_mongodb():
            cont = input("\nContinue without MongoDB? (y/n): ")
            if cont.lower() != 'y':
                return
        
        # Store original directory
        original_dir = os.getcwd()
        
        # Start components
        print_color("\n" + "="*60, "blue")
        print_color("   STARTING SYSTEM COMPONENTS", "green")
        print_color("="*60, "blue")
        
        success = True
        
        # Start backend
        if not runner.run_backend():
            success = False
        
        # Start web server
        if success and not runner.run_web_server():
            success = False
        
        # Start laptop collector
        if success:
            runner.run_laptop_collector()
        
        if success:
            # Open browser
            time.sleep(3)
            print_color("\n🌐 Opening browser...", "green")
            webbrowser.open("http://localhost:8080")
            
            print_color("\n" + "="*60, "green")
            print_color("   SYSTEM IS RUNNING!", "green")
            print_color("="*60, "green")
            print_color("\n📊 Dashboard: http://localhost:8080", "yellow")
            print_color("📚 API Docs: http://localhost:8000/docs", "yellow")
            print_color("\n🛑 Press Ctrl+C to stop all components", "red")
            
            # Keep running
            while runner.running:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    print_color("\n\n🛑 Received Ctrl+C", "red")
                    break
        
        else:
            print_color("\n❌ Failed to start all components", "red")
        
    except Exception as e:
        print_color(f"\n❌ Error: {e}", "red")
    finally:
        # Return to original directory
        os.chdir(original_dir)
        
        # Stop all processes
        runner.stop_all()
        
        print_color("\n" + "="*60, "blue")
        print_color("   SYSTEM STOPPED", "red")
        print_color("="*60, "blue")

if __name__ == "__main__":
    main()