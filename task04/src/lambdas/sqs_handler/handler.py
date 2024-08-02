# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
def lambda_handler(event, context):
    for message in event['Records']:
        process_message(message)

def process_message(message):
    try:
        print(message['body'])
    except Exception as err:
        print("An error occurred")
        raise err
