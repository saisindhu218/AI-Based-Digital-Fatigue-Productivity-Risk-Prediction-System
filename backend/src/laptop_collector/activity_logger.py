"""
Laptop Activity Logger - Background Service
Collects LIVE usage data from laptop
"""
import time
import json
from datetime import datetime
import threading
import schedule
import requests
import uuid
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings

class LaptopActivityLogger:
    def __init__(self, user_id: str, device_id: str, api_base_url: str = "http://localhost:8000"):
        self.user_id = user_id
        self.device_id = device_id
        self.api_base_url = api_base_url
        self.session_id = str(uuid.uuid4())
        self.current_app = "Unknown"
        self.session_start = datetime.now()
        self.activity_buffer = []
        
    def collect_activity(self):
        """Collect current laptop activity"""
        try:
            # Platform-specific imports
            if sys.platform == "win32":
                import win32gui
                import win32process
                import psutil
                
                window = win32gui.GetForegroundWindow()
                _, pid = win32process.GetWindowThreadProcessId(window)
                process = psutil.Process(pid)
                app_name = process.name()
                
            elif sys.platform == "darwin":  # macOS
                from AppKit import NSWorkspace
                app = NSWorkspace.sharedWorkspace().frontmostApplication()
                app_name = app.localizedName()
                
            else:  # Linux
                # You might need xdotool: sudo apt-get install xdotool
                import subprocess
                result = subprocess.run(
                    ['xdotool', 'getwindowfocus', 'getwindowname'],
                    capture_output=True, text=True
                )
                app_name = result.stdout.strip() or "Unknown"
                
            self.current_app = app_name.split('.')[0] if '.' in app_name else app_name
            
            # Simulate keystrokes and mouse clicks (in real app, use proper tracking)
            keystrokes = 0
            mouse_clicks = 0
            
            # Time calculations
            now = datetime.now()
            session_duration = (now - self.session_start).total_seconds() / 60  # minutes
            
            # Determine time of day
            hour = now.hour
            if 5 <= hour < 12:
                time_of_day = "morning"
            elif 12 <= hour < 17:
                time_of_day = "afternoon"
            elif 17 <= hour < 22:
                time_of_day = "evening"
            else:
                time_of_day = "night"
            
            activity_data = {
                "device_id": self.device_id,
                "user_id": self.user_id,
                "timestamp": now.isoformat(),
                "session_id": self.session_id,
                "active_app": self.current_app,
                "usage_duration": 1.0,  # 1 minute since last collection
                "session_length": session_duration,
                "idle_time": 0.0,  # Would need idle detection
                "time_of_day": time_of_day,
                "keystrokes": keystrokes,
                "mouse_clicks": mouse_clicks
            }
            
            self.activity_buffer.append(activity_data)
            
            # If buffer has 5 minutes of data, send to server
            if len(self.activity_buffer) >= 5:
                self.send_to_server()
                
        except Exception as e:
            print(f"Error collecting activity: {e}")
    
    def send_to_server(self):
        """Send buffered data to backend API"""
        if not self.activity_buffer:
            return
            
        try:
            for activity in self.activity_buffer:
                response = requests.post(
                    f"{self.api_base_url}/api/v1/usage/laptop",
                    json=activity,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    print(f"Sent activity data: {activity['active_app']}")
                else:
                    print(f"Failed to send data: {response.status_code}")
            
            # Clear buffer after successful send
            self.activity_buffer = []
            
        except requests.exceptions.RequestException as e:
            print(f"Error sending to server: {e}")
    
    def start(self):
        """Start the activity logger"""
        print(f"Starting Laptop Activity Logger for user {self.user_id}")
        print(f"Session ID: {self.session_id}")
        
        # Schedule collection every minute
        schedule.every(1).minutes.do(self.collect_activity)
        
        # Schedule sending every 5 minutes
        schedule.every(5).minutes.do(self.send_to_server)
        
        # Run scheduler in background thread
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(1)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        print("Laptop Activity Logger started. Press Ctrl+C to stop.")
        
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping Laptop Activity Logger...")
            # Send any remaining data
            if self.activity_buffer:
                self.send_to_server()

def main():
    """Main function to run the laptop logger"""
    # In production, these would come from configuration or user input
    USER_ID = "demo_user_123"
    DEVICE_ID = f"laptop_{uuid.uuid4().hex[:8]}"
    
    logger = LaptopActivityLogger(
        user_id=USER_ID,
        device_id=DEVICE_ID
    )
    
    logger.start()

if __name__ == "__main__":
    main()