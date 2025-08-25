const express = require('express');
const axios = require('axios');
const { CosmosClient } = require("@azure/cosmos");

const app = express();
app.use(express.json());

const WEATHER_API_KEY = "0dc56c73b23058eb4f000e8aca70267b";
const CITY = "Hungary";

const endpoint = "https://smarthome123.documents.azure.com:443/";
const key = "HCsbAKEvZe4KVcg94dylaMJazC3vb2vnzFlFHF8W1SsAJerM6CqSwl1WeGTbpNovR7Y39dFlrpiXACDbqH12Mw==";
const client = new CosmosClient({ endpoint, key });
const database = client.database("SmartHome");
const container = database.container("HomeContainer");

// Weather endpoint
app.get("/weather", async (req, res) => {
  try {
    const response = await axios.get(
      `https://api.openweathermap.org/data/2.5/weather?q=${CITY}&appid=${WEATHER_API_KEY}&units=metric`
    );
    res.json(response.data);
  } catch (err) {
    res.status(500).send(err.message);
  }
});

// Calendar endpoints
app.post("/addEvent", async (req, res) => {
  const { date, description } = req.body;
  const { resource } = await container.items.create({ date, description });
  res.json(resource);
});

app.get("/events", async (req, res) => {
  const { date } = req.query;
  const querySpec = {
    query: "SELECT * FROM c WHERE c.date=@date",
    parameters: [{ name: "@date", value: date }],
  };
  const { resources } = await container.items.query(querySpec).fetchAll();
  res.json(resources);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
