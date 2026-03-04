"""
Laptop Activity Logger - REAL LIVE TRACKING VERSION
Privacy-safe: tracks counts only, not content
Tracks:
- Screen time
- Idle time
- Keystrokes count
- Mouse clicks
- Mouse movement
- Active app
- Cognitive load category
- App switches
"""

import time
import json
from datetime import datetime, timedelta
import threading
import schedule
import requests
import uuid
import sys
import os
from pynput import keyboard, mouse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings


class LaptopActivityLogger:

    def __init__(self, user_id, device_id, api_base_url="http://localhost:8000"):

        self.user_id = user_id
        self.device_id = device_id
        self.api_base_url = api_base_url

        self.session_id = str(uuid.uuid4())
        self.session_start = datetime.now()

        # activity counters
        self.keystroke_count = 0
        self.mouse_click_count = 0
        self.mouse_move_count = 0

        # idle tracking
        self.last_input_time = datetime.now()
        self.total_idle_seconds = 0

        # app tracking
        self.current_app = "Unknown"
        self.last_app = None
        self.app_switch_count = 0

        # buffer
        self.activity_buffer = []

        # start listeners
        self.start_input_listeners()

    # ---------------- INPUT LISTENERS ----------------

    def start_input_listeners(self):

        def on_key_press(key):
            self.keystroke_count += 1
            self.last_input_time = datetime.now()

        def on_click(x, y, button, pressed):
            if pressed:
                self.mouse_click_count += 1
                self.last_input_time = datetime.now()

        def on_move(x, y):
            self.mouse_move_count += 1

        keyboard.Listener(on_press=on_key_press, daemon=True).start()
        mouse.Listener(on_click=on_click, on_move=on_move, daemon=True).start()

    # ---------------- ACTIVE WINDOW ----------------

    def get_active_app(self):

        try:
            if sys.platform == "win32":
                import win32gui
                import win32process
                import psutil

                window = win32gui.GetForegroundWindow()
                _, pid = win32process.GetWindowThreadProcessId(window)
                process = psutil.Process(pid)
                app = process.name()

            elif sys.platform == "darwin":
                from AppKit import NSWorkspace
                app = NSWorkspace.sharedWorkspace().frontmostApplication().localizedName()

            else:
                import subprocess
                result = subprocess.run(
                    ['xdotool', 'getwindowfocus', 'getwindowname'],
                    capture_output=True, text=True
                )
                app = result.stdout.strip()

            app = app.split(".")[0]
            return app

        except:
            return "Unknown"

    # ---------------- COGNITIVE LOAD ----------------

    def get_app_category(self, app):

        high = ["code", "pycharm", "intellij", "studio", "notepad++", "sublime"]
        medium = ["word", "excel", "powerpoint", "docs"]
        low = ["youtube", "netflix", "spotify", "instagram", "facebook"]

        name = app.lower()

        if any(x in name for x in high):
            return "HIGH"
        elif any(x in name for x in medium):
            return "MEDIUM"
        elif any(x in name for x in low):
            return "LOW"
        else:
            return "MEDIUM"

    # ---------------- IDLE TIME ----------------

    def calculate_idle(self):

        idle = (datetime.now() - self.last_input_time).total_seconds()

        if idle > 60:
            self.total_idle_seconds += idle
            self.last_input_time = datetime.now()

        return idle

    # ---------------- MAIN COLLECTION ----------------

    def collect_activity(self):

        now = datetime.now()

        app = self.get_active_app()

        if self.last_app and self.last_app != app:
            self.app_switch_count += 1

        self.last_app = app
        self.current_app = app

        idle_seconds = self.calculate_idle()

        session_minutes = (now - self.session_start).total_seconds() / 60

        category = self.get_app_category(app)

        hour = now.hour

        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 22:
            time_of_day = "evening"
        else:
            time_of_day = "night"

        data = {
            "user_id": self.user_id,
            "device_id": self.device_id,
            "session_id": self.session_id,
            "timestamp": now.isoformat(),
            "active_app": app,
            "app_category": category,
            "usage_duration": 1,
            "session_length": session_minutes,
            "idle_time_seconds": idle_seconds,
            "keystrokes": self.keystroke_count,
            "mouse_clicks": self.mouse_click_count,
            "mouse_moves": self.mouse_move_count,
            "app_switches": self.app_switch_count,
            "time_of_day": time_of_day
        }

        self.activity_buffer.append(data)

        print(f"Collected: {app} | Keys:{self.keystroke_count} Clicks:{self.mouse_click_count} Idle:{idle_seconds:.1f}s")

        # reset counters
        self.keystroke_count = 0
        self.mouse_click_count = 0
        self.mouse_move_count = 0

        if len(self.activity_buffer) >= 5:
            self.send_to_server()

    # ---------------- SEND ----------------

    def send_to_server(self):

        for activity in self.activity_buffer:

            try:
                r = requests.post(
                    f"{self.api_base_url}/api/v1/usage/laptop",
                    json=activity
                )

                if r.status_code == 200:
                    print("Sent OK")
                else:
                    print("Send failed")

            except Exception as e:
                print("Send error:", e)

        self.activity_buffer.clear()

    # ---------------- START ----------------

    def start(self):

        print("Starting REAL Laptop Activity Logger")
        print("User:", self.user_id)
        print("Device:", self.device_id)

        schedule.every(1).minutes.do(self.collect_activity)
        schedule.every(5).minutes.do(self.send_to_server)

        def loop():
            while True:
                schedule.run_pending()
                time.sleep(1)

        threading.Thread(target=loop, daemon=True).start()

        while True:
            time.sleep(1)


# ---------------- MAIN ----------------

def main():

    USER_ID = "demo_user"
    DEVICE_ID = "laptop_" + uuid.uuid4().hex[:6]

    logger = LaptopActivityLogger(USER_ID, DEVICE_ID)

    logger.start()


if __name__ == "__main__":
    main()