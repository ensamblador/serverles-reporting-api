#%%
import boto3
from botocore.exceptions import ClientError

# %%
ddb = boto3.client('dynamodb', region_name='us-west-1')
#table = ddb.Table('ondemand-reports-REPORTEDEFINICIONC6FAC89F-KUT55K7BGROT')
# %%
response = ddb.get_item(
    TableName='ondemand-reports-REPORTEDEFINICIONC6FAC89F-KUT55K7BGROT',
    Key={'customer_id': {'S':str(1)}, 'report_id':{'S':'100'}})
# %%

athena = boto3.client('athena',region_name='us-west-1')

# %%
database_name = response['Item']['database']['S']
query_string = response['Item']['query_string']['S']
# %%
query_start = athena.start_query_execution(
    QueryString=query_string,
    QueryExecutionContext={
        'Database': database_name
    },
    ResultConfiguration={
        'OutputLocation': 's3://ondemand-reports-athenabuckete7ba2094-3z0gyhq54eci/from_lambda/'
    }
)
# %%
res = athena.get_query_execution(
    QueryExecutionId='6f3d9513-9fdb-43af-bb40-3fddb61d181e'#query_start['QueryExecutionId']
)
res['QueryExecution']
# %%
res['QueryExecution']['Statistics']
# %%

output_location =res['QueryExecution']['ResultConfiguration']['OutputLocation']
submission_time = res['QueryExecution']['Status']['SubmissionDateTime'].strftime("%Y/%m/%d %H:%M:%S")
completion_time = res['QueryExecution']['Status']['CompletionDateTime'].strftime("%Y/%m/%d %H:%M:%S")
data_scanned = res['QueryExecution']['Statistics']['DataScannedInBytes']
execution_time = res['QueryExecution']['Statistics']['TotalExecutionTimeInMillis']


print ('Submission Time:', submission_time)
print ('Completion Time:', completion_time)
print ('Data Scanned (bytes):',data_scanned)
print ('Execution time (ms):',execution_time)
print ('File :', output_location)
# %%
res['QueryExecution']
# %%

# %%
raise Exception('Error',)
# %%

def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        print (e)
        return None

    # The response contains the presigned URL
    return response

# %%
create_presigned_url('ondemand-reports-athenabuckete7ba2094-3z0gyhq54eci','from_lambda/563bc2b8-ab1c-4236-b3b3-0e1951f4c548.csv')
# %%
