import boto3
from botocore.exceptions import ClientError
import json
import ast

"""Get the emails to send the weather to"""
def get_emails():
    # Initialize the low-level DynamoDB client
    client = boto3.client('dynamodb')
    
    # Create a reusable scan paginator
    paginator = client.get_paginator('scan')
    
    all_items = []
    
    # Iterate through all pages of the table
    for page in paginator.paginate(TableName="EmailTableWeatherUpdaterApp"):
        all_items.extend(page.get('Items', []))
        
    return all_items

def send_weather_handler(event, context):
    # 1. Initialize the client
    ses_client = boto3.client('ses', region_name='us-east-1')

    emails = get_emails()

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    weather_table = dynamodb.Table('WeatherTableWeatherUpdaterApp')

    for e in emails:
        weather = weather_table.get_item(
            Key={
                'location': e["location"]["S"]
            }
        ).get('Item')

        weather_list =""
        times = ast.literal_eval(weather["temperatures"])['hourly']['time']
        temps = ast.literal_eval(weather["temperatures"])['hourly']['temperature_2m']

        for i in range(len(times)):
            weather_list += "<li>" + str(times[i]) + ":\t" + str(temps[i]) + "&deg;C"

        # 2. Define email details
        SENDER = "Weather Updater App <weatherupdaterapp@gmail.com>"
        RECIPIENT = e["email"]["S"]
        SUBJECT = "Today's Weather"
        BODY_HTML = "<h1>Today's Weather Outlook:</h1><h2>" + e["location"]["S"] + ":<br></h2><p><ul>" + weather_list + "</ul></p>"

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