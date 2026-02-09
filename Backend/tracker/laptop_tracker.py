import time
import psutil
import requests
from pynput import keyboard, mouse

BACKEND_URL = "http://127.0.0.1:5000/collect-data"

last_activity_time = time.time()

def on_activity(*args):
    global last_activity_time
    last_activity_time = time.time()

# Keyboard & mouse listeners
keyboard.Listener(on_press=on_activity).start()
mouse.Listener(on_move=on_activity).start()

def get_active_app():
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            return proc.info['name']
    except:
        return "Unknown"

print("💻 Laptop tracker started...")

while True:
    idle_time = time.time() - last_activity_time

    payload = {
        "device": "laptop",
        "screen_time": 1,              # 1 minute per loop
        "active_app": get_active_app(),
        "idle_time": round(idle_time, 2)
    }

    try:
        requests.post(BACKEND_URL, json=payload)
        print("📤 Data sent:", payload)
    except:
        print("❌ Backend not reachable")

    time.sleep(60)
