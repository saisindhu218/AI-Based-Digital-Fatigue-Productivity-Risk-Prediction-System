import tkinter as tk
import requests

API_URL = "http://127.0.0.1:5000/predict"


def analyze():

    try:
        res = requests.get(API_URL)

        data = res.json()

        if "error" in data:
            fatigue_label.config(text=data["error"])
            return

        fatigue_label.config(
            text="Fatigue Level: " + data["fatigue_level"]
        )

        productivity_label.config(
            text="Productivity Score: " + str(data["productivity_score"]) + "%"
        )

        rec_text.delete("1.0", tk.END)

        for r in data["recommendations"]:
            rec_text.insert(tk.END, "• " + r + "\n")

    except:
        fatigue_label.config(text="Backend not running")


root = tk.Tk()

root.title("Digital Fatigue Monitor")
root.geometry("400x350")

title = tk.Label(
    root,
    text="Digital Fatigue Monitor",
    font=("Arial", 16)
)

title.pack(pady=10)

fatigue_label = tk.Label(
    root,
    text="Fatigue Level: --",
    font=("Arial", 12)
)

fatigue_label.pack()

productivity_label = tk.Label(
    root,
    text="Productivity Score: --",
    font=("Arial", 12)
)

productivity_label.pack()

btn = tk.Button(
    root,
    text="Analyze Now",
    command=analyze
)

btn.pack(pady=10)

rec_label = tk.Label(root, text="Recommendations")
rec_label.pack()

rec_text = tk.Text(root, height=6, width=40)
rec_text.pack()

root.mainloop()