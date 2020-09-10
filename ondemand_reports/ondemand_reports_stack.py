from aws_cdk import (
    aws_lambda as _lambda,
    aws_s3 as s3,
    core
)

from sqs.queue_lambda_pub_sub import queue_lambda_pub_sub
from api_cors.api_cors import api_cors_lambda


class OndemandReportsStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, athena_bucket_arn, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)


        publish_lambda = _lambda.Function(self, "PUBLISH_", runtime=_lambda.Runtime.PYTHON_3_6,
                                    handler="lambda-handler.main", timeout=core.Duration.seconds(15),
                                    memory_size=3008, code=_lambda.Code.asset("./lambda/report_request"),
                                    description='Agrega un mensaje en cola')
    

        subscribe_lambda = _lambda.Function(self, "SUBSCRIBE_", runtime=_lambda.Runtime.PYTHON_3_6,
                                    handler="lambda-handler.main", timeout=core.Duration.seconds(15),
                                    memory_size=3008, code=_lambda.Code.asset("./lambda/report_process"),
                                    description='Procesa un mensaje de la cola')

        report_queue = queue_lambda_pub_sub(self, "report_queue", publish_lambda, subscribe_lambda)

        publish_lambda.add_environment("ENV_SQS_QUEUE", report_queue.queue.queue_url)
        publish_lambda.add_environment("ENV_REGION", self.region)
        subscribe_lambda.add_environment("ENV_REGION", self.region)

        #la API que le pasa el request al publisher
        api = api_cors_lambda(self, "API", publish_lambda)

        athena_bucket = s3.Bucket.from_bucket_arn(self, 'ATHENA_BUCKET_', athena_bucket_arn)

        athena_bucket.grant_read(subscribe_lambda)