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
    QueryExecutionId='414e66ce-c4cf-4518-b1ad-74138582a9df'#query_start['QueryExecutionId']
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
