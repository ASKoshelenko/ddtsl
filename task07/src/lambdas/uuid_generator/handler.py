import json
import uuid
from datetime import datetime
import boto3
import os

s3 = boto3.client('s3')
bucket_name = os.environ['bucket_name'] 

def lambda_handler(event, context):
    uuids = [str(uuid.uuid4()) for _ in range(10)]
    file_name = datetime.utcnow().isoformat() + 'Z'
    
    data = {
        "ids": uuids
    }
    
    s3.put_object(
        Bucket=bucket_name,
        Key=file_name,
        Body=json.dumps(data),
        ContentType='application/json'
    )
    
    return {
        'statusCode': 200
    }

