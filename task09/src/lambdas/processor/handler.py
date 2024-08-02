import json
import requests
import boto3
import uuid
import os
from decimal import Decimal

from commons.log_helper import get_logger

# DynamoDB client

'''dynamodb = boto3.client('dynamodb')
table =os.environ['table_name']'''
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['table_name']
table = dynamodb.Table(table_name)

_LOG = get_logger('Processor-handler')
BASE_URL = 'https://api.open-meteo.com/v1/forecast?latitude=50.4375&longitude=30.5&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m'

def lambda_handler(event, context):
    """
    Explain incoming event here
    """
    response = requests.get(BASE_URL)
    weather_data = response.json()
    _LOG.info(f'{weather_data}')
    
    item = {
        "id": str(uuid.uuid4()),
        "forecast": {
            "elevation": weather_data["elevation"],
            "generationtime_ms": weather_data['generationtime_ms'],
            "hourly": {
                "temperature_2m": weather_data["hourly_units"]["temperature_2m"],
                "time": weather_data['hourly']['time']
            },
            "hourly_units": {
                "temperature_2m": weather_data["hourly_units"]["temperature_2m"],
                "time": weather_data['hourly_units']['time']
            },
            "latitude": weather_data["latitude"],
            "longitude": (weather_data["longitude"]),
            "timezone": weather_data["timezone"],
            "timezone_abbreviation": weather_data["timezone_abbreviation"],
            "utc_offset_seconds": weather_data['utc_offset_seconds']
            }
        }
    item = json.loads(json.dumps(item), parse_float=Decimal)
    res = table.put_item(Item=item)
    _LOG.info(f'{res}')
    # Insert item into DynamoDB
    #dynamodb.put_item(TableName=table,
                    #Item=item)
    
    return res
