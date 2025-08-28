from flask import Flask, request, jsonify, send_from_directory
from azure.cosmos import CosmosClient
from datetime import datetime, timedelta
import uuid
import os

# --- Configuration ---
app = Flask(__name__, static_folder="")

# Cosmos DB
COSMOS_ENDPOINT = os.environ.get("COSMOS_ENDPOINT", "https://smarthome123.documents.azure.com:443/")
COSMOS_KEY = os.environ.get("COSMOS_KEY", "YOUR_COSMOS_KEY_HERE")
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
        body["id"] = str(uuid.uuid4())
        body["type"] = "event"   # tag so we know it's a calendar event
        container.create_item(body)
        return jsonify(body)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/deleteEvent/<event_id>", methods=["DELETE"])
def delete_event(event_id):
    try:
        # ✅ Important: use the same partition key as when creating the item (id here)
        container.delete_item(item=event_id, partition_key=event_id)
        return jsonify({"status": "deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Run App ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
