import json

def lambda_handler(event, context):
    response = {
        'statusCode': 200, 
        'message': 'Hello from Lambda'
    }
    return response
