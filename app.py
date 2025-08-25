from flask import Flask, request, jsonify, send_from_directory
import requests
from azure.cosmos import CosmosClient
import os

# --- Configuration ---

app = Flask(__name__, static_folder='')

# Weather API
WEATHER_API_KEY = "0dc56c73b23058eb4f000e8aca70267b"  # Replace with your OpenWeatherMap API key
CITY = "Hungary"  # Change to your preferred city

# Cosmos DB
COSMOS_ENDPOINT = "https://smarthome123.documents.azure.com:443/"  # Replace with your Cosmos DB URI
COSMOS_KEY = "HCsbAKEvZe4KVcg94dylaMJazC3vb2vnzFlFHF8W1SsAJerM6CqSwl1WeGTbpNovR7Y39dFlrpiXACDbqH12Mw=="            # Replace with your Cosmos DB Primary Key
DATABASE_NAME = "SmartHome"          # Your database name
CONTAINER_NAME = "HomeContainer"                    # Your container name

# Initialize Cosmos DB client
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

# --- Routes ---

# Serve the frontend dashboard
@app.route("/")
def index():
    return send_from_directory("", "index.html")

# Weather endpoint
@app.route("/weather")
def weather():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()
        return jsonify({
            "name": data["name"],
            "temp": data["main"]["temp"],
            "description": data["weather"][0]["description"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add calendar event
@app.route("/addEvent", methods=["POST"])
def add_event():
    try:
        body = request.json
        container.create_item(body)
        return jsonify(body)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get events for a date
@app.route("/events")
def get_events():
    try:
        date = request.args.get("date")
        query = f"SELECT * FROM c WHERE c.date='{date}'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Run app ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
