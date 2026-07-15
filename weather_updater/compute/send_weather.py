import requests
import boto3

def send_weather_handler(event, context):
    print("Sending weather")