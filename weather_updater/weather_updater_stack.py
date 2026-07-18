from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_lambda,
    BundlingOptions,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    RemovalPolicy,
    Duration
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
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            timeout=Duration.seconds(20))
        
        send_weather_function = aws_lambda.Function(
            self, 
            id="SendWeatherFunction", 
            code=aws_lambda.Code.from_asset("weather_updater/compute", bundling=BundlingOptions(
                image=aws_lambda.Runtime.PYTHON_3_12.bundling_image,
                command=[
                    "bash", "-c",
                    "pip install -r requirements.txt -t /asset-output && cp -r . /asset-output"
                ]
            )), 
            handler="send_weather.send_weather_handler",
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            timeout=Duration.seconds(20))
        
        add_emails_function =aws_lambda.Function(
            self, 
            id="AddEmailsFunction", 
            code=aws_lambda.Code.from_asset("weather_updater/compute", bundling=BundlingOptions(
                image=aws_lambda.Runtime.PYTHON_3_12.bundling_image,
                command=[
                    "bash", "-c",
                    "pip install -r requirements.txt -t /asset-output && cp -r . /asset-output"
                ]
            )), 
            handler="add_emails.add_emails_handler",
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            timeout=Duration.seconds(20))
        
        weather_table = dynamodb.TableV2(
            self,
            id="WeatherTableWeatherUpdaterApp",
            partition_key=dynamodb.Attribute(name="location", type=dynamodb.AttributeType.STRING),
            table_name="WeatherTableWeatherUpdaterApp",
            removal_policy=RemovalPolicy.DESTROY
        )

        email_table = dynamodb.TableV2(
            self,
            id="EmailTableWeatherUpdaterApp",
            partition_key=dynamodb.Attribute(name="email", type=dynamodb.AttributeType.STRING),
            table_name="EmailTableWeatherUpdaterApp",
            removal_policy=RemovalPolicy.DESTROY
        )

        pull_weather_function.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'dynamodb:PutItem'
            ],
            resources=[
                '*',
            ],
        ))

        send_weather_function.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'dynamodb:GetItem',
                'dynamodb:Scan',
                'ses:SendEmail',
                'ses:SendRawEmail'
            ],
            resources=[
                '*',
            ],
        ))

        add_emails_function.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'dynamodb:PutItem'
            ],
            resources=[
                '*',
            ],
        ))