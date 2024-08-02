from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
import boto3
import json
import uuid
import os
from decimal import Decimal
from datetime import datetime

_LOG = get_logger('ApiHandler-handler')

client = boto3.client('cognito-idp')
user_pool_name = os.environ['USER_POOL']
client_app = 'client-app'

user_pool_id = None
response = client.list_user_pools(MaxResults = 60)
for user_pool in response['UserPools']:
    if user_pool['Name'] == user_pool_name:
        user_pool_id = user_pool['Id']
        break
_LOG.info(f'user pool id: {user_pool_id}')

client_app_id = None
response = client.list_user_pool_clients(UserPoolId = user_pool_id)
for user_pool_client in response['UserPoolClients']:
    if user_pool_client['ClientName'] == client_app:
        client_app_id = user_pool_client['ClientId']
        break
_LOG.info(f'Client app id: {client_app_id}')

dynamodb = boto3.resource('dynamodb')
tables_name = dynamodb.Table(os.environ['TABLES'])
reservations_name = dynamodb.Table(os.environ['RESERVATIONS'])

def decimal_serializer(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError("Type not serializable")

def lambda_handler(event, context):

    path = event['path']
    http_method = event['httpMethod']
    
    _LOG.info(f'{path} {http_method}')
    try:
        if path == '/signup' and http_method == 'POST':
            body = json.loads(event['body'])

            email = body['email']
            first_name = body['firstName']
            last_name = body['lastName']
            password = body['password']
            _LOG.info(f'{email}, {first_name}, {last_name}, {password}')

            response = client.admin_create_user(
                UserPoolId = user_pool_id,
                Username = email,
                UserAttributes = [
                    {
                        'Name': 'email',
                        'Value': email
                    },
                    {
                        'Name': 'given_name',
                        'Value': first_name
                    },
                    {
                        'Name': 'family_name',
                        'Value': last_name
                    }
                ],
                TemporaryPassword = password,
                MessageAction = 'SUPPRESS'
            )
            _LOG.info(f'Create User Response: {response}')

            response = client.admin_set_user_password(
                UserPoolId = user_pool_id,
                Username = email,
                Password = password,
                Permanent=True
            )
            _LOG.info(f'Set password Response: {response}')

            return {
                'statusCode': 200,
                'body': json.dumps({"message": "Sign-up process is successful"})
            }
            
        elif path == '/signin' and http_method == 'POST':
            body = json.loads(event['body'])
            email = body['email']
            password = body['password']
            _LOG.info(f'{email}, {password}')

            response = client.initiate_auth(
                AuthFlow = 'USER_PASSWORD_AUTH',
                AuthParameters = {
                    'USERNAME': email,
                    'PASSWORD': password
                    },
                ClientId=client_app_id
            )
            access_token = response['AuthenticationResult']['AccessToken']
            id_token = response['AuthenticationResult']['IdToken']
            _LOG.info(f'accessToken: {access_token}')
            return {
                'statusCode': 200,
                'body': json.dumps({'accessToken': id_token})
            }
        
        elif path == '/tables' and http_method == 'GET': #work

            response = tables_name.scan()
            _LOG.info(response)
            items = response['Items']
            tables = {'tables': sorted(items, key=lambda item: item['id'])}
            body = json.dumps(tables, default=decimal_serializer)
            _LOG.info(f"{body=}")
            
            return {
                'statusCode': 200,
                'body': body
            }
        
        elif path == '/tables' and http_method == 'POST': # work
            body = json.loads(event['body'])
            item = {
                 "id": int(body['id']),
                 "number": body['number'],
                 "places": body['places'],
                 "isVip": body['isVip'],
                 "minOrder": body['minOrder']
             }

            item = json.loads(json.dumps(item))
            response = tables_name.put_item(Item=item)
            
            return {
                'statusCode': 200,
                'body': json.dumps({"id": body['id']})
            }
        
        elif event['resource']  == '/tables/{tableId}' and http_method == 'GET': #work
            table_id = int(event['path'].split('/')[-1])
            _LOG.info(f"table id {table_id}")
            item = tables_name.get_item(Key={'id': int(table_id)})
            body = item["Item"]
            _LOG.info(f"tablesid {body}")
            
            return {
                'statusCode': 200,
                'body': json.dumps(body, default=decimal_serializer)
            }
        
        elif path == '/reservations' and http_method == 'GET': 
            # Format the response
            _LOG.info("reservations get")
            response = reservations_name.scan()
            items = response['Items']
            _LOG.info(f'Reservation get {items}')
            for i in items:
                del i["id"]
            _LOG.info(items)
            items = sorted(items, key=lambda item: item['tableNumber'])
            _LOG.info(items)
            reservations = {"reservations": items}
            _LOG.info(reservations)
            
            return {
                'statusCode': 200,
                'body': json.dumps(reservations, default=decimal_serializer)
            }
        
        elif path == '/reservations' and http_method == 'POST': #work fully

            item = json.loads(event['body'])
            _LOG.info(item)
            # check if table exsist
            tables_response = tables_name.scan()
            tables = tables_response['Items']
            _LOG.info(f'reservattions post Tables {tables}')
            table_numbers = [ table["number"] for table in tables]
            if item['tableNumber'] not in table_numbers:
                raise ValueError("No such table.")
                
            # check slots
            proposed_time_start = datetime.strptime(item["slotTimeStart"], "%H:%M").time()
            proposed_time_end = datetime.strptime(item["slotTimeEnd"], "%H:%M").time()

            reservations_response = reservations_name.scan()
            reservations = reservations_response['Items']
            _LOG.info(f'reservations table: {reservations}')

            for reserved in reservations:
                if reserved['tableNumber'] != item['tableNumber']:
                    continue
                if reserved['date'] != item['date']:
                    continue

                reserved_time_start = datetime.strptime(reserved["slotTimeStart"], "%H:%M").time()
                reserved_time_end = datetime.strptime(reserved["slotTimeEnd"], "%H:%M").time()
                if any([reserved_time_start <= proposed_time <= reserved_time_end for proposed_time in (proposed_time_start, proposed_time_end)]):
                    raise ValueError('Time already reserved')
            
            reservation_id = str(uuid.uuid4())
            response = reservations_name.put_item(Item={"id": reservation_id, **item})
            _LOG.info(response)
            
            return {
                'statusCode': 200,
                'body': json.dumps({"reservationId": reservation_id})
            }
    
    except Exception as e:
        _LOG.error(f'{e}')
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Something wrong'})
        }

