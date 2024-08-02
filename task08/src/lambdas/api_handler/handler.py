from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
import json
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

_LOG = get_logger('ApiHandler-handler')


class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        """
        Explain incoming event here
        """
        latitude = event.get('latitude', 52.52)
        longitude = event.get('longitude', 13.419998)

        try:
            weather_data = OpenMeteoAPI.get_weather(latitude, longitude)
            return {
                'statusCode': 200,
                'body': json.dumps(weather_data)
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }
    

HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
