import json
import os
import uuid
import boto3
import datetime
from botocore.exceptions import ClientError

ddb = boto3.resource('dynamodb')
athena = boto3.client('athena')

region_name = os.environ.get('ENV_REGION_NAME')
athena_results = os.environ.get('ENV_ATHENA_RESULTS_BUCKET')
table_name = ddb.Table(os.environ['QUERY_DEFINITIONS_TABLE'])


def get_query_definition(customer_id, report_id):
    table = ddb.Table(table_name)
    try:
        response = table.get_item(
            Key={'customer_id': customer_id, 'report_id': report_id})
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False
    else:
        return response['Item']['query_definition']


def main(event, context):
    log_banner('Log de Ejecución')
    print('request: {}'.format(json.dumps(event)))
    
    # Reeemplazar con la consulta a la base de datos de reportes para obtener la consulta a realizar
    query = get_query_definition(event['customer_ud'], event['report_id'])

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }


def log_banner(text):
    banner_width = len(text)+8
    print(banner_width*'*')
    print('*** {} ***'.format(text))
    print(banner_width*'*')
