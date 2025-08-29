import os
import requests
import tkinter as tk
from PIL import ImageTk, Image
from io import BytesIO
from dotenv import load_dotenv
import datetime

# Load API key
env_path = r"C:\Users\rodef\Downloads\ByteWeather\.env"
load_dotenv(dotenv_path=env_path, override=True)
API_KEY = os.getenv("OPENWEATHER_KEY")


class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ByteWeather")
        self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{self.width}x{self.height}")

        # placeholders
        self.bg_image = None
        self.data = {}
        self.URL = None
        self.bg_label = None

        # search bar
        self.create_search_bar()

        # default city = Austin
        self.search_city(default="Austin")

    # -------------------------
    # UI Components
    # -------------------------
    def create_search_bar(self):
        search_frame = tk.Frame(self, bg="#1e1e2f")
        search_frame.place(relx=0.5, rely=0.05, anchor=tk.CENTER)

        self.city_entry = tk.Entry(search_frame, font=("Segoe UI", 16), width=20)
        self.city_entry.insert(0, "Austin")
        self.city_entry.pack(side="left", padx=5)

        search_btn = tk.Button(search_frame, text="Search", font=("Segoe UI", 14, "bold"),
                               bg="#ef233c", fg="white", command=self.search_city)
        search_btn.pack(side="left")

    def make_card(self, parent, w, h, bg, text=None, font=("Segoe UI", 20), fg="white"):
        frame = tk.Frame(parent, bg=bg, width=w, height=h, highlightthickness=0)
        frame.pack(side="left", expand=True, padx=10, pady=10)
        if text:
            label = tk.Label(frame, text=text, font=font, fg=fg, bg=bg, justify="center")
            label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        return frame

    # -------------------------
    # Weather Data Handling
    # -------------------------
    def build_url(self, city):
        return f"http://api.openweathermap.org/data/2.5/weather?q={city},US&units=imperial&appid={API_KEY}"

    def search_city(self, default=None):
        city = default if default else self.city_entry.get().strip()
        if not city:
            return
        self.URL = self.build_url(city)
        self.get_weather_data()
        self.set_background()
        self.set_weather_data()

    def get_weather_data(self):
        if not API_KEY or not self.URL:
            self.data = {"temp": "—", "temp_min": "—", "temp_max": "—",
                         "feels_like": "—", "humidity": "—", "icon": "01d",
                         "main": "Clear", "city_name": "Unknown"}
            return
        try:
            resp = requests.get(self.URL, timeout=10)
            resp.raise_for_status()
            raw = resp.json()
            self.data = raw.get("main", {})
            self.data["icon"] = raw["weather"][0]["icon"]
            self.data["main"] = raw["weather"][0]["main"]
            self.data["city_name"] = raw.get("name", "Unknown")
        except Exception as e:
            print("API error:", e)
            self.data = {"temp": "—", "temp_min": "—", "temp_max": "—",
                         "feels_like": "—", "humidity": "—", "icon": "01d",
                         "main": "Clear", "city_name": "Unknown"}

    # -------------------------
    # Background
    # -------------------------
    def set_background(self):
        condition = self.data.get("main", "Clear").lower()

        bg_map = {
            "clear": "backgrounds/clear.jpg",
            "clouds": "backgrounds/cloudy.jpg",
            "rain": "backgrounds/rain.jpg",
            "drizzle": "backgrounds/rain.jpg",
            "thunderstorm": "backgrounds/storm.jpg",
            "snow": "backgrounds/snow.jpg"
        }

        bg_file = bg_map.get(condition, "backgrounds/default.jpg")

        try:
            img = Image.open(bg_file).resize((self.width, self.height))
            self.bg_image = ImageTk.PhotoImage(img)
        except:
            # fallback solid color
            img = Image.new("RGB", (self.width, self.height), (135, 206, 250))
            self.bg_image = ImageTk.PhotoImage(img)

        if self.bg_label:
            self.bg_label.destroy()

        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()

    # -------------------------
    # Cards
    # -------------------------
    def set_weather_data(self):
        # Clear old frames (but keep search bar & background intact)
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame) and widget not in [self.city_entry.master]:
                widget.destroy()

        # --------- Top Section (Main Card) ---------
        top_frame = tk.Frame(self, bg="", highlightthickness=0)
        top_frame.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        city_name = self.data.get("city_name", "Unknown")
        condition = self.data.get("main", "—")

        header = tk.Label(top_frame, text=f"{city_name} — {condition}",
                          font=("Segoe UI", 24, "bold"),
                          fg="white", bg="#2b2d42", padx=20, pady=10)
        header.pack(fill="x", pady=(0, 5))

        temp_label = tk.Label(top_frame,
                              text=f"{self.data.get('temp', '—')}°F",
                              font=("Segoe UI", 65, "bold"),
                              fg="white", bg="#2b2d42", padx=20)
        temp_label.pack(fill="x")

        # Weather Icon
        try:
            icon_url = f"http://openweathermap.org/img/wn/{self.data.get('icon', '01d')}@2x.png"
            icon_img = Image.open(BytesIO(requests.get(icon_url, stream=True).content)).resize((120, 120))
            icon = ImageTk.PhotoImage(icon_img)
            icon_label = tk.Label(top_frame, image=icon, bg="#2b2d42")
            icon_label.image = icon
            icon_label.pack()
        except:
            tk.Label(top_frame, text="☀️", font=("Segoe UI", 40), bg="#2b2d42", fg="white").pack()

        # --------- Bottom Section (Two Equal Cards) ---------
        bottom_frame = tk.Frame(self, bg="", highlightthickness=0)
        bottom_frame.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

        minMAXText = f"Min: {self.data.get('temp_min', '—')}°F\nMax: {self.data.get('temp_max', '—')}°F"
        self.make_card(bottom_frame, 350, 180, "#8d99ae",
                       text=minMAXText, font=("Segoe UI", 22))

        extraText = f"Feels Like: {self.data.get('feels_like', '—')}°F\nHumidity: {self.data.get('humidity', '—')}%"
        self.make_card(bottom_frame, 350, 180, "#ef233c",
                       text=extraText, font=("Segoe UI", 22))

        # --------- Footer (Timestamp) ---------
        timestamp = datetime.datetime.now().strftime("%I:%M %p")
        footer = tk.Label(self, text=f"Last updated: {timestamp}",
                          font=("Segoe UI", 14), fg="white", bg="#1e1e2f")
        footer.place(relx=0.5, rely=0.95, anchor=tk.CENTER)


if __name__ == "__main__":
    WeatherApp().mainloop()
