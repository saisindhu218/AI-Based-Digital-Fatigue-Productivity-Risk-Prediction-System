import sys
import os

# ✅ Fix Python path so db.py can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, backend_dir)

from db import metrics_collection

import time
from datetime import datetime
from pynput import keyboard, mouse

# Global counters
keystroke_count = 0
mouse_click_count = 0

# Keyboard listener
def on_key_press(key):
    global keystroke_count
    keystroke_count += 1

# Mouse listener
def on_click(x, y, button, pressed):
    global mouse_click_count
    if pressed:
        mouse_click_count += 1

# Start listeners
keyboard_listener = keyboard.Listener(on_press=on_key_press)
mouse_listener = mouse.Listener(on_click=on_click)

keyboard_listener.start()
mouse_listener.start()

# Cognitive Load Calculation
def calculate_cognitive_load(keystrokes, mouse_clicks, idle_time):
    norm_keys = min(keystrokes / 200, 1)
    norm_mouse = min(mouse_clicks / 300, 1)
    norm_idle = min(idle_time / 60, 1)

    load = (
        0.4 * norm_keys +
        0.3 * norm_mouse +
        0.3 * (1 - norm_idle)
    )

    return round(min(load, 1), 2)

print("🚀 Laptop Tracker Started... Collecting data every 60 seconds.")

while True:
    try:
        start_time = time.time()

        # For now, idle_time is assumed 0 (can improve later)
        idle_time = 0
        screen_time = 1  # Since system is active

        time.sleep(60)

        cognitive_load = calculate_cognitive_load(
            keystroke_count,
            mouse_click_count,
            idle_time
        )

        data = {
            "screen_time": screen_time,
            "idle_time": idle_time,
            "keystrokes": keystroke_count,
            "mouse_movements": mouse_click_count,
            "cognitive_load": cognitive_load,
            "timestamp": datetime.utcnow()
        }

        metrics_collection.insert_one(data)

        print("✅ Data inserted:", data)

        # Reset counters
        keystroke_count = 0
        mouse_click_count = 0

    except Exception as e:
        print("❌ Error:", e)