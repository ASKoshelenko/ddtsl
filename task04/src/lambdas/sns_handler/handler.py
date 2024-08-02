# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
def lambda_handler(event, context):
    for record in event['Records']:
        process_message(record)

def process_message(record):
    try:
        message = record['Sns']['Message']
        print(message)
        
    except Exception as e:
        print("An error occurred")
        raise e


