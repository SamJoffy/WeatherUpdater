import boto3

def add_emails_handler(event, context):
    # Initialize the DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    # Reference your table
    email_table = dynamodb.Table('EmailTableWeatherUpdaterApp')

    # Add Emails to table:
    email_table.put_item(
        Item={
            'email': 'sjoffy@hotmail.com',      # Partition key
            'location': 'Canberra'
        }
    )
    email_table.put_item(
        Item={
            'email': 'weatherupdaterapp@gmail.com',      # Partition key
            'location': 'New York'
        }
    )