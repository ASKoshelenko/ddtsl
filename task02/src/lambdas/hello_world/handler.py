import json

def lambda_handler(event, context):
    path = event['requestContext']['http']['path']
    method = event['requestContext']['http']['method']
    if path == '/hello' and method == 'GET':
        response = {
            'statusCode': 200,
            'body': json.dumps({'statusCode': 200, 'message': 'Hello from Lambda'})
        }
    else:
        response = {
            'statusCode': 400,
            'body': json.dumps({'statusCode': 400, 'message': f'Bad request syntax or unsupported method. Request path: {path}. HTTP method: {method}'})
        }
    return response
