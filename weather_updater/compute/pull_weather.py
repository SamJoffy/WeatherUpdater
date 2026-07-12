import requests

def pull_weather_handler(event, context):
    url = "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m"

    response = requests.get(url)

    if response.status_code == 200:
        print('data:', response.json())
    else:
        print('data not found')