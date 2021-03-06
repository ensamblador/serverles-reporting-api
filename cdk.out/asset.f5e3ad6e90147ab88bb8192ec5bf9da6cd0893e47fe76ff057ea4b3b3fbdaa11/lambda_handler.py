import json
import os
import uuid
import boto3
import datetime


region_name = os.environ.get('ENV_REGION_NAME')
athena = boto3.client('athena',region_name=region_name)
sqs = boto3.client('sqs', region_name=region_name)

def main(event, context):
    log_banner('Log de Ejecución')
    print('request: {}'.format(json.dumps(event)))
    rec = event['Records'][0]
    msg = json.loads(rec['body'])


    res = athena.get_query_execution(
        QueryExecutionId=msg['query_execution_id']
    )
    state = res['QueryExecution']['Status']['State']
    
    if (state =='RUNNING') or (state =='QUEUED'): 
        print('Estado:', state)
        print(json.dumps(res))
        return { 'statusCode': 500 }
     

    if (state =='FAILED') or (state=='CANCELLED'): 
        print(json.dumps(res))

    
    if state == 'SUCCEEDED':

        output_location =res['QueryExecution']['ResultConfiguration']['OutputLocation']
        submission_time = res['QueryExecution']['Status']['SubmissionDateTime'].strftime("%Y/%m/%d %H:%M:%S")
        completion_time = res['QueryExecution']['Status']['CompletionDateTime'].strftime("%Y/%m/%d %H:%M:%S")
        data_scanned = res['QueryExecution']['Statistics']['DataScannedInBytes']
        execution_time = res['QueryExecution']['Statistics']['TotalExecutionTimeInMillis']

        print ('Request Time:', msg['request_time'])
        print ('Submission Time:', submission_time)
        print ('Completion Time:', completion_time)
        print ('Data Scanned (bytes):',data_scanned)
        print ('Execution time (ms):',execution_time)
        print ('File :', output_location)



    source_arn = rec['eventSourceARN']
    parts = source_arn.split('arn:aws:')[1].split(':')
    sqs_url = 'https://{}.amazonaws.com/{}/{}'.format('.'.join(parts[:2]), parts[2], parts[3])
    receipt_handle = rec['receiptHandle']

    sqs.delete_message( QueueUrl=sqs_url, ReceiptHandle=receipt_handle)
    print('Mensaje {} borrado'.format(rec['messageId']))
    print('\n---*** Fin de Ejecución ***---\n')

    return {
        'statusCode': 200,
        'body': json.dumps('OK')
    }


def log_banner(text):
    banner_width = len(text)+8
    print(banner_width*'*')
    print('*** {} ***'.format(text))
    print(banner_width*'*')
