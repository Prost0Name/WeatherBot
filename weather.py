import aiohttp
import matplotlib.pyplot as plt
import io
from datetime import datetime
from config import OPENWEATHER_API_KEY, OPENWEATHER_API_URL, OPENWEATHER_FORECAST_URL

async def get_weather(city: str) -> str:
    params = {
        'q': city,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric',  
        'lang': 'ru'  
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(OPENWEATHER_API_URL, params=params) as response:
            if response.status != 200:
                raise Exception(f"Не удалось получить данные о погоде. Код ошибки: {response.status}")
            
            data = await response.json()
            
            weather_description = data['weather'][0]['description']
            temperature = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            pressure = data['main']['pressure']
            wind_speed = data['wind']['speed']
            
            weather_info = (
                f"🏙 Погода в городе {city}:\n\n"
                f"🌡 Температура: {temperature}°C\n"
                f"🌡 Ощущается как: {feels_like}°C\n"
                f"☁️ Описание: {weather_description}\n"
                f"💧 Влажность: {humidity}%\n"
                f"🌪 Скорость ветра: {wind_speed} м/с\n"
                f"🔵 Давление: {pressure} гПа"
            )
            
            return weather_info


async def get_weather_by_coords(lat: float, lon: float) -> str:
    params = {
        'lat': lat,
        'lon': lon,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(OPENWEATHER_API_URL, params=params) as response:
            if response.status != 200:
                raise Exception(f"Ошибка получения данных. Код: {response.status}")

            data = await response.json()

            city_name = data.get('name', 'неизвестный город')

            weather_description = data['weather'][0]['description']
            temperature = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            pressure = data['main']['pressure']
            wind_speed = data['wind']['speed']

            weather_info = (
                f"📍 Погода по вашему местоположению ({city_name}):\n\n"
                f"🌡 Температура: {temperature}°C\n"
                f"🌡 Ощущается как: {feels_like}°C\n"
                f"☁️ Описание: {weather_description}\n"
                f"💧 Влажность: {humidity}%\n"
                f"🌪 Скорость ветра: {wind_speed} м/с\n"
                f"🔵 Давление: {pressure} гПа"
            )

            return weather_info

async def get_weather_forecast(city: str) -> str:
    params = {
        'q': city,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(OPENWEATHER_FORECAST_URL, params=params) as response:
            if response.status != 200:
                raise Exception(f"Не удалось получить прогноз погоды. Код ошибки: {response.status}")
            
            data = await response.json()
            
            # Группируем прогноз по дням
            daily_forecasts = {}
            for item in data['list']:
                date = item['dt_txt'].split()[0]  # Получаем только дату
                if date not in daily_forecasts:
                    daily_forecasts[date] = {
                        'temp_min': item['main']['temp_min'],
                        'temp_max': item['main']['temp_max'],
                        'description': item['weather'][0]['description'],
                        'humidity': item['main']['humidity'],
                        'wind_speed': item['wind']['speed']
                    }
            
            # Формируем текст прогноза
            forecast_text = f"📅 Прогноз погоды в городе {city} на 5 дней:\n\n"
            
            for date, forecast in list(daily_forecasts.items())[:5]:  # Берем только 5 дней
                forecast_text += (
                    f"📆 {date}\n"
                    f"🌡 Температура: {forecast['temp_min']:.1f}°C - {forecast['temp_max']:.1f}°C\n"
                    f"☁️ {forecast['description']}\n"
                    f"💧 Влажность: {forecast['humidity']}%\n"
                    f"🌪 Ветер: {forecast['wind_speed']} м/с\n\n"
                )
            
            return forecast_text

async def create_temperature_graph(city: str) -> bytes:
    params = {
        'q': city,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(OPENWEATHER_FORECAST_URL, params=params) as response:
            if response.status != 200:
                raise Exception(f"Не удалось получить прогноз погоды. Код ошибки: {response.status}")
            
            data = await response.json()
            
            # Создаем списки для данных
            times = []
            temps = []
            
            # Собираем данные
            for item in data['list']:
                dt = datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
                times.append(dt)
                temps.append(item['main']['temp'])
            
            # Создаем график
            plt.figure(figsize=(12, 6))
            plt.plot(times, temps, marker='o')
            plt.title(f'Прогноз температуры в городе {city}')
            plt.xlabel('Время')
            plt.ylabel('Температура (°C)')
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Сохраняем график в байты
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()
            
            return buf.getvalue()

async def get_weather_forecast_by_coords(lat: float, lon: float) -> str:
    params = {
        'lat': lat,
        'lon': lon,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(OPENWEATHER_FORECAST_URL, params=params) as response:
            if response.status != 200:
                raise Exception(f"Не удалось получить прогноз погоды. Код ошибки: {response.status}")
            
            data = await response.json()
            city_name = data['city']['name']
            
            # Группируем прогноз по дням
            daily_forecasts = {}
            for item in data['list']:
                date = item['dt_txt'].split()[0]  # Получаем только дату
                if date not in daily_forecasts:
                    daily_forecasts[date] = {
                        'temp_min': item['main']['temp_min'],
                        'temp_max': item['main']['temp_max'],
                        'description': item['weather'][0]['description'],
                        'humidity': item['main']['humidity'],
                        'wind_speed': item['wind']['speed']
                    }
            
            # Формируем текст прогноза
            forecast_text = f"📅 Прогноз погоды в городе {city_name} на 5 дней:\n\n"
            
            for date, forecast in list(daily_forecasts.items())[:5]:  # Берем только 5 дней
                forecast_text += (
                    f"📆 {date}\n"
                    f"🌡 Температура: {forecast['temp_min']:.1f}°C - {forecast['temp_max']:.1f}°C\n"
                    f"☁️ {forecast['description']}\n"
                    f"💧 Влажность: {forecast['humidity']}%\n"
                    f"🌪 Ветер: {forecast['wind_speed']} м/с\n\n"
                )
            
            return forecast_text