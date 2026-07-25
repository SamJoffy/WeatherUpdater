import boto3

"""Adds/updates list of emails and subscribers. For demonstration purposes 
I just have a static list of users, but if I were to make this a public application,
this is where the logic to handle subscribers would go"""
def add_emails_handler(event, context):
    # Initialize the DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    email_table = dynamodb.Table('EmailTableWeatherUpdaterApp')

    # Add emails to table:
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