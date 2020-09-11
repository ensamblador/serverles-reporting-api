from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_s3 as s3,
    aws_dynamodb as ddb,
    core
)

from sqs.queue_lambda_pub_sub import queue_lambda_pub_sub
from api_cors.api_cors import api_cors_lambda


class OndemandReportsStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str,  **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        reports_prefix = 'from_lambda/'

        athena_bucket = s3.Bucket(self, 'ATHENA_BUCKET_', versioned=False)


        publish_lambda = _lambda.Function(self, "PUBLISH_", runtime=_lambda.Runtime.PYTHON_3_6,
                                          handler="lambda_handler.main", timeout=core.Duration.seconds(20),
                                          memory_size=128, code=_lambda.Code.asset("./lambda/report_request"),
                                          description='Agrega un mensaje en cola')

        subscribe_lambda = _lambda.Function(self, "SUBSCRIBE_", runtime=_lambda.Runtime.PYTHON_3_6,
                                            handler="lambda_handler.main", timeout=core.Duration.seconds(20),
                                            memory_size=128, code=_lambda.Code.asset("./lambda/report_process"),
                                            description='Procesa un mensaje de la cola')

        poll_query_lambda = _lambda.Function(self, "POLL_QUERY_", runtime=_lambda.Runtime.PYTHON_3_6,
                                            handler="lambda_handler.main", timeout=core.Duration.seconds(20),
                                            memory_size=128, code=_lambda.Code.asset("./lambda/poll_query"),
                                            description='Monitorea la query mediante una cola')


        report_queue = queue_lambda_pub_sub(self, "report_queue", publish_lambda, subscribe_lambda)
        poll_query_queue = queue_lambda_pub_sub(self, "poll_query_queue", subscribe_lambda, poll_query_lambda)

        reports_definitions_table = ddb.Table(self, "REPORTE_DEFINICION_",partition_key=ddb.Attribute(name="customer_id", type=ddb.AttributeType.STRING),sort_key=ddb.Attribute(name="report_id", type=ddb.AttributeType.STRING))


        reports_definitions_table.grant_read_data(subscribe_lambda)

        publish_lambda.add_environment("ENV_SQS_QUEUE", report_queue.queue.queue_url)
        publish_lambda.add_environment("ENV_REGION", self.region)

        subscribe_lambda.add_environment("ENV_REGION", self.region)
        subscribe_lambda.add_environment("ENV_ATHENA_RESULTS_BUCKET", athena_bucket.bucket_name)
        subscribe_lambda.add_environment("ENV_ATHENA_RESULTS_PREFIX", reports_prefix)

        subscribe_lambda.add_environment("QUERY_DEFINITIONS_TABLE", reports_definitions_table.table_name)
        subscribe_lambda.add_environment("ENV_SQS_QUEUE", poll_query_queue.queue.queue_url)

        poll_query_lambda.add_environment("ENV_REGION", self.region)


        # la API que le pasa el request al publisher
        api = api_cors_lambda(self, "API", publish_lambda)

        #Permisos de Lectura para el bucket de Athena así la lambda lo puede leer

        athena_bucket.grant_read(poll_query_lambda)
        athena_bucket.grant_read_write(subscribe_lambda)

        subscribe_lambda.add_to_role_policy(iam.PolicyStatement(actions=["athena:StartQueryExecution", "athena:GetQueryExecution"],resources=['*']))
        subscribe_lambda.add_to_role_policy(iam.PolicyStatement(actions=["glue:GetTable", "glue:GetPartitions"],resources=['*']))
        subscribe_lambda.add_to_role_policy(iam.PolicyStatement(actions=["s3:*"],resources=['*']))
        #athena_full_access = iam.ManagedPolicy.from_aws_managed_policy_name('AmazonAthenaFullAccess')
        #subscribe_lambda.role.add_managed_policy(athena_full_access)

        poll_query_lambda.add_to_role_policy(iam.PolicyStatement(actions=["athena:GetQueryExecution"],resources=['*']))
        poll_query_lambda.add_to_role_policy(iam.PolicyStatement(actions=["ses:SendEmail","ses:SendRawEmail"],resources=["*"]))