import requests
import boto3

def pull_weather_handler(event, context):
    # Initialize the DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    # Reference your table
    table = dynamodb.Table('WeatherTableWeatherUpdaterApp')
    
    url = "https://api.open-meteo.com/v1/forecast?latitude=-35.28&longitude=149.13&hourly=temperature_2m&forecast_days=1"

    response = requests.get(url)

    if response.status_code == 200:
        table.put_item(
            Item={
                'location': 'Canberra',      # Partition key
                'temperatures': str(response.json())
            }
        )
    else:
        print('data not found')