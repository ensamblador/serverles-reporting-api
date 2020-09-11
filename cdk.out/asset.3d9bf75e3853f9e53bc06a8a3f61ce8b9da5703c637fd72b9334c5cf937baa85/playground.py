#%%
import boto3
from botocore.exceptions import ClientError

# %%
ddb = boto3.client('dynamodb', 'us-west-1')
#table = ddb.Table('ondemand-reports-REPORTEDEFINICIONC6FAC89F-KUT55K7BGROT')
# %%
response = table.get_item(
    TableName='ondemand-reports-REPORTEDEFINICIONC6FAC89F-KUT55K7BGROT',
    Key={'customer_id': 1, 'report_id':100})
# %%
