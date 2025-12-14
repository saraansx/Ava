import logging
import httpx
from config import Config

class WeatherTool:
    def __init__(self):
        self.name = "weather"
        self.description = "Get current weather for a city. Input should be the city name."
        self.logger = logging.getLogger("WeatherTool")
        self.api_key = Config.OPEN_WEATHER_API_KEY
        if self.api_key:
            self.api_key = self.api_key.strip()
        
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def execute(self, city="Kolkata"):
        if not self.api_key:
            return "Error: OpenWeather API Key is missing."

        if not city or city.lower() == "none":
            city = "Kolkata"

        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            response = httpx.get(self.base_url, params=params)
            data = response.json()

            if response.status_code == 200:
                weather_desc = data['weather'][0]['description']
                temp = data['main']['temp']
                humidity = data['main']['humidity']
                return f"The weather in {city} is {weather_desc}, {temp}°C, {humidity}% humidity."
            else:
                error_msg = data.get('message', 'Unknown error')
                self.logger.error(f"Weather API Error: {error_msg}")
                return f"Error fetching weather for {city}: {error_msg}"
        except Exception as e:
            self.logger.error(f"Weather Fetch Error: {e}")
            return f"An error occurred: {e}"
