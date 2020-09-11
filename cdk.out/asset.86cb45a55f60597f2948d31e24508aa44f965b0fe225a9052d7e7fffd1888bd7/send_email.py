import boto3
from botocore.exceptions import ClientError
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

def envia_email_adjunto(subject="Asunto",fileLocation="", filename="", destinatarios=[],sender="noreply@chickyshop.cl", body=""):
    client = boto3.client('ses', region_name='us-east-1')
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = ', '.join(destinatarios)
    part = MIMEText(body, 'html')
    message.attach(part)
    part = MIMEApplication(open(fileLocation, 'rb').read())
    part.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(part)
    try:
        response = client.send_raw_email(
            Source=message['From'],
            Destinations=destinatarios,
            RawMessage={
                'Data': message.as_string()
            }
        )
    except ClientError as e:
        response = repr(e)
    return response


def envia_email(subject="Asunto",destinatarios=[],sender="noreply@chickyshop.cl", body=""):
    client = boto3.client('ses', region_name='us-east-1')
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = ', '.join(destinatarios)
    part = MIMEText(body, 'html')
    message.attach(part)
    try:
        response = client.send_raw_email(
            Source=message['From'],
            Destinations=destinatarios,
            RawMessage={
                'Data': message.as_string()
            }
        )
    except ClientError as e:
        response = repr(e)
    return response