import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
POSTGRES_URI = os.getenv("POSTGRES_URI")

OPENWEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

print(POSTGRES_URI)
if not BOT_TOKEN:
    raise ValueError("Не задана переменная окружения BOT_TOKEN")
    
if not OPENWEATHER_API_KEY:
    raise ValueError("Не задана переменная окружения OPENWEATHER_API_KEY") 