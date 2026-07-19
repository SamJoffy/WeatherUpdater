from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_lambda,
    BundlingOptions,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    RemovalPolicy,
    Duration,
    aws_s3 as s3,
    aws_events as events,
    aws_events_targets as targets,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks
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

        # Create a secure, managed S3 bucket
        report_bucket = s3.Bucket(
            self, 
            "Reports",
            # Optional: Specify a globally unique bucket name. 
            # If omitted, AWS CDK generates one automatically.
            bucket_name="weather-updater-app-bucket", 
            
            # Enables tracking and recovering older versions of files
            versioned=True,
            
            # Encrypts data at rest using Amazon S3-managed keys
            encryption=s3.BucketEncryption.S3_MANAGED,
            
            # Blocks all public access for security best practices
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            
            # Forces SSL/HTTPS connections for objects data transfers
            enforce_ssl=True,
            
            # DESTROY deletes the bucket during 'cdk destroy' (use RETAIN for production)
            removal_policy=RemovalPolicy.DESTROY,
            
            # Automatically purges existing objects so the bucket can be cleanly destroyed
            auto_delete_objects=True 
        )

        weather_rule = events.Rule(
            self, 
            "DailyExecutionRule",
            schedule=events.Schedule.cron(
                minute="0",
                hour="21",
                day="*",
                month="*",
                year="*"
            ),
            description="Triggers the Lambda functions daily at 21:00 PM UTC"
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
                'ses:SendRawEmail',
                's3:PutObject'
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

        add_emails_task = tasks.LambdaInvoke(
            self, "InvokeAddEmails",
            lambda_function=add_emails_function,
            payload_response_only=True
        )

        pull_weather_task = tasks.LambdaInvoke(
            self, "InvokePullWeather",
            lambda_function=pull_weather_function,
            payload_response_only=True
        )

        send_weather_task = tasks.LambdaInvoke(
            self, "InvokeSendWeather",
            lambda_function=send_weather_function,
            payload_response_only=True
        )

        # 4. Chain the tasks sequentially into a State Machine definition
        definition = add_emails_task.next(pull_weather_task).next(send_weather_task)

        state_machine = sfn.StateMachine(
            self, "SequentialStateMachine",
            definition_body=sfn.DefinitionBody.from_chainable(definition),
            timeout=Duration.minutes(5)
        )

        weather_rule.add_target(targets.SfnStateMachine(state_machine))