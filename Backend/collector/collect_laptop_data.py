import time
import psutil
from pynput import keyboard, mouse
from pymongo import MongoClient
import certifi
from datetime import datetime

MONGO_URI = "YOUR_MONGO_URI"

client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where()
)

db = client["digital_fatigue_db"]
collection = db["device_usage"]

keystroke_count = 0
mouse_move_count = 0

def on_press(key):
    global keystroke_count
    keystroke_count += 1

def on_move(x, y):
    global mouse_move_count
    mouse_move_count += 1

keyboard.Listener(on_press=on_press).start()
mouse.Listener(on_move=on_move).start()

def calculate_idle_time():
    return psutil.cpu_percent(interval=1)  # proxy idle behavior

while True:
    start_time = time.time()

    idle_time = calculate_idle_time()
    screen_time = 1  # assume screen active if system running

    # Normalize values
    keystrokes = keystroke_count
    mouse_moves = mouse_move_count

    idle_ratio = min(idle_time / 100, 1)

    # Cognitive Load Calculation
    physical_load = (
        (keystrokes / 200) * 0.5 +
        (mouse_moves / 500) * 0.3 +
        (1 - idle_ratio) * 0.2
    )

    contextual_load = 0

    if keystrokes > 50 and mouse_moves < 300:
        contextual_load = 0.9  # coding pattern
    elif mouse_moves > 400 and keystrokes < 20:
        contextual_load = 0.3  # streaming pattern
    else:
        contextual_load = 0.6

    cognitive_load = min((physical_load * 0.6 + contextual_load * 0.4), 1)

    document = {
        "screen_time": screen_time,
        "idle_time": idle_time,
        "keystrokes": keystrokes,
        "mouse_movements": mouse_moves,
        "cognitive_load": cognitive_load,
        "timestamp": datetime.utcnow()
    }

    collection.insert_one(document)

    keystroke_count = 0
    mouse_move_count = 0

    time.sleep(max(0, 60 - (time.time() - start_time)))