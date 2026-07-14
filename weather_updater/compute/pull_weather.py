import requests
import boto3

def pull_weather_handler(event, context):
    # Initialize the DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    # Reference your table
    table = dynamodb.Table('WeatherTable')

    # Insert the item
    response = table.put_item(
        Item={
            'location': 'user_12345',      # Partition key
            'name': 'Jane Doe',
            'age': 30,                    # Automatically inferred as Number (N)
            'is_active': True,            # Automatically inferred as Boolean (BOOL)
            'roles': ['admin', 'editor']  # Automatically inferred as List (L)
        }
    )

    print(response)
    url = "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m"

    response = requests.get(url)

    if response.status_code == 200:
        print('data:', response.json())
    else:
        print('data not found')