from flask import Flask, jsonify, send_from_directory
import requests
from datetime import datetime, timedelta
import os

# --- Configuration ---
app = Flask(__name__, static_folder='')

# Weather API (Budapest)
WEATHER_API_KEY = "0dc56c73b23058eb4f000e8aca70267b"
LAT = 47.4979   # Budapest latitude
LON = 19.0402   # Budapest longitude

# --- Routes ---

# Serve index.html
@app.route("/")
def index():
    return send_from_directory("", "index.html")

# --- Weather ---
@app.route("/weeklyWeather")
def weekly_weather():
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/onecall"
            f"?lat={LAT}&lon={LON}&exclude=current,minutely,hourly,alerts"
            f"&units=metric&appid={WEATHER_API_KEY}"
        )
        data = requests.get(url).json()

        # Find Monday of this week (UTC)
        today = datetime.utcnow().date()
        monday = today - timedelta(days=today.weekday())  # 0 = Monday
        friday = monday + timedelta(days=4)

        weekdays = []
        for day in data.get("daily", []):
            date = datetime.utcfromtimestamp(day["dt"]).date()
            if monday <= date <= friday:
                weekdays.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "temp_avg": round(day["temp"]["day"], 1),
                    "rain_chance": round(day.get("pop", 0) * 100, 1)
                })

        return jsonify(weekdays)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Run App ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
