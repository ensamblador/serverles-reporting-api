
from aws_cdk import (
    aws_sqs as sqs,
    aws_events as events,
    aws_iam as iam,
    aws_lambda_event_sources,
    aws_lambda as _lambda,
    core
)



class queue_lambda_pub_sub(core.Construct):
    def __init__(self, scope: core.Construct, id: str, publisher_lambda, suscriber_lambda, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
    
        queue_fail = sqs.Queue(self, "queue_fail", visibility_timeout=core.Duration.seconds(15))
        dlq = sqs.DeadLetterQueue( max_receive_count=3, queue=queue_fail)
        self.queue = sqs.Queue(self, "base_queue", visibility_timeout=core.Duration.seconds(15), dead_letter_queue=dlq)


        #Configuramos la lambda para que reciba los mensajes de la cola
        self.queue.grant_consume_messages(suscriber_lambda)
        event_source = aws_lambda_event_sources.SqsEventSource(self.queue, batch_size=1)
        suscriber_lambda.add_event_source(event_source)

        #la lambda que publica mensajes
        self.queue.grant_send_messages(publisher_lambda)

