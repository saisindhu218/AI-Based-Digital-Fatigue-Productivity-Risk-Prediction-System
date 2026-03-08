import customtkinter as ctk
import requests
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

API_URL = "http://127.0.0.1:5000/predict"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class FatigueDashboard(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("AI Digital Fatigue Monitor")
        self.geometry("900x600")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---------- Sidebar ----------
        sidebar = ctk.CTkFrame(self, width=200)
        sidebar.grid(row=0, column=0, sticky="ns")

        title = ctk.CTkLabel(
            sidebar,
            text="Fatigue Monitor",
            font=("Arial", 22, "bold")
        )
        title.pack(pady=30)

        analyze_btn = ctk.CTkButton(
            sidebar,
            text="Analyze Session",
            command=self.analyze
        )
        analyze_btn.pack(pady=10)

        quit_btn = ctk.CTkButton(
            sidebar,
            text="Exit",
            fg_color="red",
            command=self.destroy
        )
        quit_btn.pack(pady=10)

        # ---------- Main Frame ----------
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        main_frame.grid_columnconfigure((0, 1), weight=1)

        # Fatigue Card
        self.fatigue_card = ctk.CTkFrame(main_frame)
        self.fatigue_card.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.fatigue_label = ctk.CTkLabel(
            self.fatigue_card,
            text="Fatigue Level",
            font=("Arial", 18)
        )
        self.fatigue_label.pack(pady=10)

        self.fatigue_value = ctk.CTkLabel(
            self.fatigue_card,
            text="--",
            font=("Arial", 26, "bold")
        )
        self.fatigue_value.pack(pady=10)

        # Productivity Card
        self.productivity_card = ctk.CTkFrame(main_frame)
        self.productivity_card.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        prod_title = ctk.CTkLabel(
            self.productivity_card,
            text="Productivity Score",
            font=("Arial", 18)
        )
        prod_title.pack(pady=10)

        self.progress = ctk.CTkProgressBar(self.productivity_card)
        self.progress.pack(pady=10, padx=20)

        self.prod_label = ctk.CTkLabel(
            self.productivity_card,
            text="0%",
            font=("Arial", 20)
        )
        self.prod_label.pack(pady=5)

        # Chart Frame
        chart_frame = ctk.CTkFrame(main_frame)
        chart_frame.grid(row=1, column=0, columnspan=2, pady=20, sticky="nsew")

        chart_title = ctk.CTkLabel(
            chart_frame,
            text="Cognitive Load Visualization",
            font=("Arial", 18)
        )
        chart_title.pack()

        self.figure = plt.Figure(figsize=(5, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack()

        # Recommendations
        rec_frame = ctk.CTkFrame(main_frame)
        rec_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        rec_title = ctk.CTkLabel(
            rec_frame,
            text="Recommendations",
            font=("Arial", 18)
        )
        rec_title.pack()

        self.rec_box = ctk.CTkTextbox(
            rec_frame,
            height=120
        )
        self.rec_box.pack(pady=10, padx=10, fill="x")

    def analyze(self):

        try:

            res = requests.get(API_URL)
            data = res.json()

            if "error" in data:
                messagebox.showinfo("Info", data["error"])
                return

            fatigue = data["fatigue_level"]
            productivity = data["productivity_score"]

            self.fatigue_value.configure(text=fatigue)

            self.progress.set(productivity / 100)
            self.prod_label.configure(text=f"{productivity}%")

            self.rec_box.delete("1.0", "end")

            for rec in data["recommendations"]:
                self.rec_box.insert("end", "• " + rec + "\n")

            # Chart example visualization
            self.ax.clear()
            values = [productivity, 100 - productivity]
            labels = ["Productive", "Fatigue Impact"]

            self.ax.pie(values, labels=labels, autopct="%1.1f%%")
            self.ax.set_title("Productivity Distribution")

            self.canvas.draw()

            if fatigue == "High":
                messagebox.showwarning(
                    "Fatigue Alert",
                    "⚠ High fatigue detected. Please take a break."
                )

        except:
            messagebox.showerror(
                "Error",
                "Backend server not running"
            )


app = FatigueDashboard()
app.mainloop()