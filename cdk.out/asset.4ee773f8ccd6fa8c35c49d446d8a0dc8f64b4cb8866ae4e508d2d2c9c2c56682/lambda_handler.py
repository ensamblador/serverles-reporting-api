import json
import os
import uuid
import boto3
import datetime
from botocore.exceptions import ClientError

region_name = os.environ.get('ENV_REGION_NAME')
athena_results = os.environ.get('ENV_ATHENA_RESULTS_BUCKET')
reports_prefix = os.environ.get('ENV_ATHENA_RESULTS_PREFIX')
table_name = os.environ.get('QUERY_DEFINITIONS_TABLE')
poll_queue = os.environ.get('ENV_SQS_QUEUE')

ddb = boto3.client('dynamodb',region_name=region_name)
athena = boto3.client('athena',region_name=region_name)
sqs = boto3.client('sqs', region_name=region_name)


def get_query_definition(customer_id, report_id):
    try:
        response = ddb.get_item(
            TableName=table_name,
            Key={'customer_id': {'S':str(customer_id)}, 'report_id':{'S':str(report_id)}})
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

    if ('customer_id' in request) & ('report_id' in request):
        cid = request['customer_id']
        rid = request['report_id']
        request_time = request['request_time']
    else: 
        return {'statusCode': 200, 'body': 'Faltan Parámetros'}

    # Reeemplazar con la consulta a la base de datos de reportes para obtener la consulta a realizar
    query_item = get_query_definition(cid, rid)

    if query_item:
        database_name = query_item['database']['S']
        query_string = query_item['query_string']['S']
        detination_email = query_item['destination_email']['S']
    else:
        return {'statusCode': 200, 'body': 'Item {}/{} no encontrado'.format(cid, rid)}


    print('Item {}|{}:\n\nQueryString:{}\n\nDatabaseName:{}\n'.format(cid, rid, query_string, database_name))
    

    query_start = athena.start_query_execution(
        QueryString=query_string,
        QueryExecutionContext={
            'Database': database_name
        },
        ResultConfiguration={
            'OutputLocation': 's3://{}/{}'.format(athena_results, reports_prefix)
        }
    )

    print ('** query {} iniciada'.format(query_start['QueryExecutionId']))

    polling_message = {
            'customer_id': cid,
            'report_id': rid,
            'destination_email': detination_email,
            'query_string':query_string,
            'database_name': database_name,
            'request_time' : request_time,
            'query_execution_id': query_start['QueryExecutionId']
        }

    response = sqs.send_message(QueueUrl=poll_queue,MessageBody=json.dumps(polling_message))

    log_banner('Resultado')
    print(json.dumps(polling_message))

    source_arn = rec['eventSourceARN']
    parts = source_arn.split('arn:aws:')[1].split(':')
    sqs_url = 'https://{}.amazonaws.com/{}/{}'.format('.'.join(parts[:2]), parts[2], parts[3])
    receipt_handle = rec['receiptHandle']

    sqs.delete_message( QueueUrl=sqs_url, ReceiptHandle=receipt_handle)
    print('Mensaje {} borrado'.format(rec['messageId']))
    print('\n---*** Fin de Ejecución ***---\n')

    return {
        'statusCode': 200,
        'body': json.dumps(polling_message)
    }


def log_banner(text):
    banner_width = len(text)+8
    print(banner_width*'*')
    print('*** {} ***'.format(text))
    print(banner_width*'*')
