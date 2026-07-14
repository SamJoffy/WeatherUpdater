from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_lambda,
    BundlingOptions,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
)
from constructs import Construct

class WeatherUpdaterStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # database_write_role = iam.Role(
        #     self, "DatabaseWriteRole",
        #     assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        # )

        pull_weather_function = aws_lambda.Function(
            self, 
            id="PullWeatherFunction", 
            code=aws_lambda.Code.from_asset("weather_updater/compute", bundling=BundlingOptions(
                image=aws_lambda.Runtime.PYTHON_3_12.bundling_image,
                command=[
                    "bash", "-c",
                    "pip install -r requirements.txt -t /asset-output && cp -r . /asset-output"
                ]
            )), 
            handler="pull_weather.pull_weather_handler",
            runtime=aws_lambda.Runtime.PYTHON_3_12)
        
        weather_table = dynamodb.TableV2(
            self,
            id="WeatherTable",
            partition_key=dynamodb.Attribute(name="location", type=dynamodb.AttributeType.STRING),
            table_name="WeatherTable"
        )

        pull_weather_function.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'dynamodb:PutItem',
            ],
            resources=[
                '*',
            ],
        ))
