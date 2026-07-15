import requests
import boto3
from botocore.exceptions import ClientError

def send_weather_handler(event, context):
    # 1. Initialize the client
    ses_client = boto3.client('ses', region_name='us-east-1')

    # 2. Define email details
    SENDER = "Weather Updater App <weatherupdaterapp@gmail.com>"
    RECIPIENT = "sjoffy@hotmail.com"
    SUBJECT = "Test Email via Boto3"
    BODY_HTML = "<h1>Today's Weather Outlook:</h1><h2>Canberra:<br></h2><p><ul><li>9 - 30&deg;C<li>10 - 30&deg;C<li>11 - 40&deg;C</ul></p>"

    # 3. Send the email
    try:
        response = ses_client.send_email(
            Source=SENDER,
            Destination={'ToAddresses': [RECIPIENT]},
            Message={
                'Subject': {'Data': SUBJECT},
                'Body': {'Html': {'Data': BODY_HTML}}
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print(f"Sent! Message ID: {response['MessageId']}")