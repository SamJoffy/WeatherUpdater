import boto3
from botocore.exceptions import ClientError
import ast
from datetime import datetime

"""Get the emails and locations they're subscribed to"""
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

"""Uploads report to the s3 bucket"""
def upload_html_string(html_content, bucket_name, object_name):
    s3_client = boto3.client('s3')
    
    try:
        # Convert string to bytes and upload
        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_name,
            Body=html_content.encode('utf-8'),
            ContentType='text/html'
        )
        print(f"Successfully uploaded HTML string to {bucket_name}/{object_name}")
    except Exception as e:
        print(f"Error uploading content: {e}")

"""Sends the weather to subscribers and stores it in the s3 bucket"""
def send_weather_handler(event, context):
    # Initialize email client and tables
    ses_client = boto3.client('ses', region_name='us-east-1')
    emails = get_emails()
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    weather_table = dynamodb.Table('WeatherTableWeatherUpdaterApp')

    for e in emails:
        # Get subscribed location
        weather = weather_table.get_item(
            Key={
                'location': e["location"]["S"]
            }
        ).get('Item')

        # Get weather at location
        weather_list =""
        times = ast.literal_eval(weather["temperatures"])['hourly']['time']
        temps = ast.literal_eval(weather["temperatures"])['hourly']['temperature_2m']

        for i in range(len(times)):
            weather_list += "<li>" + str(times[i]) + ":\t" + str(temps[i]) + "&deg;C"

        # Define email details
        SENDER = "Weather Updater App <weatherupdaterapp@gmail.com>"
        RECIPIENT = e["email"]["S"]
        SUBJECT = "Today's Weather"
        BODY_HTML = "<h1>Today's Weather Outlook:</h1><h2>" + e["location"]["S"] + ":<br></h2><p><ul>" + weather_list + "</ul></p>"

        # Upload to s3 bucket
        upload_html_string(BODY_HTML, "weather-updater-app-bucket", str(e["location"]["S"]) + "_" + str(datetime.now()) + "_weather.html")

        # Send the email
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