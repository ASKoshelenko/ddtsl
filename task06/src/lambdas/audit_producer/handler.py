import datetime
import os
import uuid
import boto3

dynamodb = boto3.client('dynamodb')
audit_table = os.environ['audit_table']

def lambda_handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_image = record['dynamodb']['NewImage']
            audit_item = {
                'id': {'S': str(uuid.uuid4())},
                'itemKey': {'S': new_image['key']['S']},
                'modificationTime': {'S': datetime.datetime.utcnow().isoformat() + 'Z'},
                'newValue': { 'M': {
                    'key': {'S': new_image['key']['S']},
                    'value': {'N': new_image['value']['N']}
                    }
                }
            }
            dynamodb.put_item(TableName=audit_table,
                              Item=audit_item
                              )
        
        elif record['eventName'] == 'MODIFY':
            old_image = record['dynamodb']['OldImage']
            new_image = record['dynamodb']['NewImage']
            if old_image['value']['N'] != new_image['value']['N']:
                audit_item = {
                    'id': {'S': str(uuid.uuid4())},
                    'itemKey': {'S': new_image['key']['S']},
                    'modificationTime': {'S': datetime.datetime.utcnow().isoformat() + 'Z'},
                    'updatedAttribute': {'S': 'value'},
                    'oldValue': {'N': old_image['value']['N']},
                    'newValue': {'N': new_image['value']['N']}
                }
                dynamodb.put_item(TableName=audit_table,
                              Item=audit_item
                              )
    
    return {
        'StatusCode': 200
        }