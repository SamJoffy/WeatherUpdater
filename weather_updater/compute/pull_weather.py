import requests
import boto3

"""Holds data for each location"""
class location:
    def __init__(self, name, lat, long, timezone) -> None:
        self.name = name
        self.lat = lat
        self.long = long
        self.timezone = timezone

"""Gets weather from api and adds it to table"""
def pull_weather_handler(event, context):
    # Initialize dynamodb and locations
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    locations = []
    locations.append(location("Canberra", -35.28, 149.13, "Australia/Sydney"))
    locations.append(location("Sydney", -33.8688, 151.2093, "Australia/Canberra"))
    locations.append(location("New York", 40.7128, -74.006, "America/New_York"))
    table = dynamodb.Table('WeatherTableWeatherUpdaterApp')

    for l in locations:
        # Get weather from api
        url = "https://api.open-meteo.com/v1/forecast?latitude=" + str(l.lat) + "&longitude=" + str(l.long) + "&timezone=" + l.timezone + "&hourly=temperature_2m&forecast_days=1"
        response = requests.get(url)

        # Add to table
        if response.status_code == 200:
            table.put_item(
                Item={
                    'location': l.name,      # Partition key
                    'temperatures': str(response.json())
                }
            )
        else:
            print('data not found')