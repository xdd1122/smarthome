from flask import Flask, request, jsonify
import requests
from azure.cosmos import CosmosClient

app = Flask(__name__)

# Weather API
WEATHER_API_KEY = "0dc56c73b23058eb4f000e8aca70267b"
CITY = "Hungary"

# Cosmos DB
COSMOS_ENDPOINT = "https://smarthome123.documents.azure.com:443/"
COSMOS_KEY = "HCsbAKEvZe4KVcg94dylaMJazC3vb2vnzFlFHF8W1SsAJerM6CqSwl1WeGTbpNovR7Y39dFlrpiXACDbqH12Mw=="
DATABASE_NAME = "SmartHome"
CONTAINER_NAME = "HomeContainer"

client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

# Weather endpoint
@app.route("/weather")
def weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
    data = requests.get(url).json()
    return jsonify({
        "name": data["name"],
        "temp": data["main"]["temp"],
        "description": data["weather"][0]["description"]
    })

# Calendar endpoints
@app.route("/addEvent", methods=["POST"])
def add_event():
    body = request.json
    container.create_item(body)
    return jsonify(body)

@app.route("/events")
def get_events():
    date = request.args.get("date")
    query = f"SELECT * FROM c WHERE c.date='{date}'"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    return jsonify(items)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
