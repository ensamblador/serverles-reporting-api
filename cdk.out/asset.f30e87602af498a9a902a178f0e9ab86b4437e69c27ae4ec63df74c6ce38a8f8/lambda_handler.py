import json
import os
import uuid
import boto3
import datetime
from send_email import envia_email

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
        print(res)
        raise Exception('Estado',state)
     

    if (state =='FAILED') or (state=='CANCELLED'): 
        print('Estado:', state)
        print(res)


    
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

        body_text = 'Se ha ejecutado el reporte <br/>'
        body_text += '<br/><br/>'
        body_text += 'Request Time:'+ msg['request_time']
        body_text += 'Submission Time:'+ submission_time
        body_text += 'Data Scanned (bytes):'+ data_scanned
        body_text += 'Execution time (ms):'+ execution_time
        body_text += 'File :'+ output_location
        
        res_email = envia_email(
            subject="Reporte " + msg['request_time'],
            destinatarios=["enrique.rodriguez.garrido@gmail.com"],
            sender="scanner@chickyshop.cl",
            body=body_text,
        )

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
