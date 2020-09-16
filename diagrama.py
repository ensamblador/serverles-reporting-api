#%%

#https://diagrams.mingrammer.com/docs/guides/diagram

from diagrams import Diagram,Cluster, Edge

from diagrams.generic.blank import Blank

from diagrams.aws.analytics import KinesisDataFirehose as KFH
from diagrams.aws.analytics import ElasticsearchService as ESS
from diagrams.elastic.elasticsearch import Kibana
from diagrams.aws.general import Users
from diagrams.aws.storage import S3
from diagrams.aws.security import Cognito
from diagrams.aws.analytics import Athena
from diagrams.aws.analytics import GlueCrawlers
from diagrams.aws.analytics import GlueDataCatalog
from diagrams.aws.compute import Lambda 
from diagrams.aws.mobile import APIGatewayEndpoint,APIGateway
from diagrams.onprem.client import Client
from diagrams.aws.database import DynamodbTable,DDB
from diagrams.aws.engagement import SES
from diagrams.aws.integration import SQS

graph_attr = {
    "esep": "+20",
    "fontsize": "45"
}
node_attr = {
       "esep": "+20",
    "fontsize": "10" 
}


with Diagram("On Demand Athena Reports", show=True, direction='LR',
            graph_attr=graph_attr, node_attr =node_attr):



    _ddb = DDB('DynamoDB Table \nReports Definitions (queries)')

    _lambda = Lambda('Lambda Publisher \nPOST {report_id: 100, client_id:1}')
    _lambda << Edge() >> _ddb 

    _api = APIGateway('Rest API')
    _client = Client('Client API Request Report ID=100')
    _client >> _api
    _api >> Edge(color="darkgreen") >> _lambda


    with Cluster("Reports Queue "):
        _sqs =SQS('Amazon SQS\nReport Request Queue')
        _lambda >> _sqs
        _lambda2 = Lambda('Lambda Subscriber \nProcess Queue Messages \n (start query)')
        _sqs >> _lambda2

    

    with Cluster('Repor Process'):
        with Cluster('Data'):
            _athena = Athena('Amazon Anthena') 
            data_stack = [S3('Dataset'),
            GlueDataCatalog('Catalog')] 
            _athena <<Edge(color="darkgreen") >> data_stack
        
        with Cluster("Query Status"):
            _sqs2 =SQS('Amazon SQS\nOngoing queries')
            _lambda3 = Lambda('Poll status queue \nif SUCCESS Generate presigned url with results')
            _sqs2 <<Edge()>> _lambda3


    lambda_destinations = [_sqs2, _athena]


    _lambda2 >>Edge()>> lambda_destinations

    _lambda3 << Edge(label='Get query Execution')>> _athena

    _lambda3 >> SES('Email report')



