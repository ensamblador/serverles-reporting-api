import json
import os
import uuid
import boto3
import datetime

sqs_queue_url = os.environ.get('ENV_SQS_QUEUE')
region_name = os.environ.get('ENV_REGION_NAME')
sqs = boto3.client('sqs', region_name=region_name)

def main(event, context):

    log_banner('Log de Ejecución')

    print('request: {}'.format(json.dumps(event)))

    reception_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print ('** enviando mensajes a la cola {}'.format(sqs_queue_url))

    response = sqs.send_message(
        QueueUrl=sqs_queue_url,MessageBody=json.dumps(event))

    return {
        'statusCode': 200,
        'body': json.dumps({
            'send_message': response
        })
    }



def log_banner(text):
    banner_width = len(text)+8
    print (banner_width*'*')
    print ('*** {} ***'.format(text))
    print (banner_width*'*')