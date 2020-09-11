import json
import os
import uuid
import boto3
import datetime

region_name = os.environ.get('ENV_REGION_NAME')

def main(event, context):

    log_banner('Log de Ejecución')

    print('request: {}'.format(json.dumps(event)))

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }



def log_banner(text):
    banner_width = len(text)+8
    print (banner_width*'*')
    print ('*** {} ***'.format(text))
    print (banner_width*'*')