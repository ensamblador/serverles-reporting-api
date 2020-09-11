import json
import os
import uuid
import boto3
import datetime
from botocore.exceptions import ClientError

region_name = os.environ.get('ENV_REGION_NAME')
athena_results = os.environ.get('ENV_ATHENA_RESULTS_BUCKET')
table_name = os.environ['QUERY_DEFINITIONS_TABLE'])

ddb = boto3.resource('dynamodb')
athena = boto3.client('athena')
sqs = boto3.client('sqs', region_name=region_name)


def get_query_definition(customer_id, report_id):
    table = ddb.Table(table_name)
    try:
        response = table.get_item(
            Key={'customer_id': customer_id, 'report_id': report_id})
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False
    else:
        return response['Item']


def main(event, context):
    log_banner('Log de Ejecución')
    print('request: {}'.format(json.dumps(event)))
    rec = event['Records'][0]
    request = json.loads(rec['body'])

    # Reeemplazar con la consulta a la base de datos de reportes para obtener la consulta a realizar
    query = get_query_definition(request['customer_ud'], request['report_id'])

    

    source_arn = rec['eventSourceARN']
    parts = source_arn.split('arn:aws:')[1].split(':')
    sqs_url = 'https://{}.amazonaws.com/{}/{}'.format('.'.join(parts[:2]), parts[2], parts[3])
    receipt_handle = rec['receiptHandle']

    sqs.delete_message( QueueUrl=sqs_url, ReceiptHandle=receipt_handle)
    print('Mensaje {} borrado'.format(rec['messageId']))
    print('\n---*** Fin de Ejecución ***---\n')

    return {
        'statusCode': 200,
        'body': json.dumps(query)
    }


def log_banner(text):
    banner_width = len(text)+8
    print(banner_width*'*')
    print('*** {} ***'.format(text))
    print(banner_width*'*')
