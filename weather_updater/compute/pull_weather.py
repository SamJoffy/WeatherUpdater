import requests
import boto3

class location:
    def __init__(self, name, lat, long, timezone) -> None:
        self.name = name
        self.lat = lat
        self.long = long
        self.timezone = timezone

def pull_weather_handler(event, context):
    # Initialize the DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    locations = []
    locations.append(location("Canberra", -35.28, 149.13, "AEST"))
    locations.append(location("Sydney", -33.8688, 151.2093, "AEST"))
    locations.append(location("New York", 40.7128, -74.006, "EST"))

    # Reference your table
    table = dynamodb.Table('WeatherTableWeatherUpdaterApp')

    for l in locations:
        url = "https://api.open-meteo.com/v1/forecast?latitude=" + str(l.lat) + "&longitude=" + str(l.long) + "&timezone=" + l.timezone + "&hourly=temperature_2m&forecast_days=1"

        response = requests.get(url)

        if response.status_code == 200:
            table.put_item(
                Item={
                    'location': l.name,      # Partition key
                    'temperatures': str(response.json())
                }
            )
        else:
            print('data not found')