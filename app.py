from flask import Flask, request, jsonify, send_from_directory
import requests
from azure.cosmos import CosmosClient
from datetime import datetime, timedelta
import uuid
import os

# --- Configuration ---
app = Flask(__name__, static_folder='')

# Weather API (Budapest)
WEATHER_API_KEY = "0dc56c73b23058eb4f000e8aca70267b"
LAT = 47.4979   # Budapest latitude
LON = 19.0402   # Budapest longitude

# Cosmos DB
COSMOS_ENDPOINT = "https://smarthome123.documents.azure.com:443/"
COSMOS_KEY = "HCsbAKEvZe4KVcg94dylaMJazC3vb2vnzFlFHF8W1SsAJerM6CqSwl1WeGTbpNovR7Y39dFlrpiXACDbqH12Mw=="
DATABASE_NAME = "SmartHome"
CONTAINER_NAME = "HomeContainer"

# Initialize Cosmos client
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

# --- Routes ---

# Serve index.html
@app.route("/")
def index():
    return send_from_directory("", "index.html")

# --- Weather ---
@app.route("/weeklyWeather")
def weekly_weather():
    try:
        url = f"https://api.openweathermap.org/data/2.5/onecall?lat={LAT}&lon={LON}&exclude=current,minutely,hourly,alerts&units=metric&appid={WEATHER_API_KEY}"
        data = requests.get(url).json()
        weekly = []
        for day in data.get('daily', []):
            weekly.append({
                "date": datetime.utcfromtimestamp(day['dt']).strftime('%Y-%m-%d'),
                "temp_avg": day['temp']['day'],
                "rain_chance": day.get('pop', 0) * 100
            })
        return jsonify(weekly)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Calendar ---
@app.route("/upcomingEvents")
def upcoming_events():
    try:
        today = datetime.utcnow().date()
        four_weeks = today + timedelta(weeks=4)
        query = f"SELECT * FROM c WHERE c.date >= '{today}' AND c.date <= '{four_weeks}'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/addEvent", methods=["POST"])
def add_event():
    try:
        body = request.json
        body['id'] = str(uuid.uuid4())
        container.create_item(body)
        return jsonify(body)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/deleteEvent/<event_id>", methods=["DELETE"])
def delete_event(event_id):
    try:
        container.delete_item(event_id, partition_key=event_id)
        return jsonify({"status": "deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Grocery List ---
@app.route("/items")
def get_items():
    try:
        items = list(container.read_all_items())
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/addItem", methods=["POST"])
def add_item():
    try:
        body = request.json
        body['id'] = str(uuid.uuid4())
        body['checked'] = False
        container.create_item(body)
        return jsonify(body)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/deleteItem/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    try:
        container.delete_item(item_id, partition_key=item_id)
        return jsonify({"status": "deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/toggleItem/<item_id>", methods=["POST"])
def toggle_item(item_id):
    try:
        item = container.read_item(item_id, partition_key=item_id)
        item["checked"] = not item.get("checked", False)
        container.replace_item(item, item)
        return jsonify(item)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Run App ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
