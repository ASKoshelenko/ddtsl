import requests

class OpenMeteoAPI:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    @staticmethod
    def get_weather(latitude, longitude):
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'hourly': 'temperature_2m'
        }
        response = requests.get(OpenMeteoAPI.BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
