import os

from aws_cdk import (
    Stack,
    Duration,
    aws_dynamodb,
    RemovalPolicy,
    aws_lambda,
    aws_iam,
)
from constructs import Construct

class CdkUrlShortenerStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        name_prefix: str,
        table_name: str,
        lambda_name: str,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.construct_id = construct_id
        self.name_prefix = name_prefix
        self.table_name = table_name
        self.lambda_name = lambda_name

        # DynamoDB creation
        self.create_dynamodb_table()

        # Lambda function creation
        self.create_policy_statement_for_lambda_to_dynamodb()
        self.create_lambda_role_policy()
        self.create_lambda_role()
        self.create_lambda_function()


    def create_dynamodb_table(self):
        self.table = aws_dynamodb.Table(
            self,
            id="{}-Table".format(self.construct_id),
            table_name="{}{}-Table".format(self.name_prefix, self.table_name),
            read_capacity=1,
            write_capacity=1,
            partition_key=aws_dynamodb.Attribute(name="id", type=aws_dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )


    def create_policy_statement_for_lambda_to_dynamodb(self):
        """
        Method to create IAM policy statement for dynamodb usage.
        """
        self.dynamodb_access_policy_statement = aws_iam.PolicyStatement(
            actions=["dynamodb:*"],
            effect=aws_iam.Effect.ALLOW,
            resources=[self.table.table_arn]
        )

    def create_lambda_role_policy(self):
        """
        Method to create IAM Policy based on all policy statements.
        """
        self.lambda_role_policy = aws_iam.Policy(
            self,
            id="{}-Policy".format(self.construct_id),
            policy_name="{}{}-Policy".format(self.name_prefix, self.lambda_name),
            statements=[
                self.dynamodb_access_policy_statement,
            ]
        )


    def create_lambda_role(self):
        """
        Method that creates the role for Lambda function execution.
        """
        self.lambda_role = aws_iam.Role(
            self,
            id="{}-Role".format(self.construct_id),
            role_name="{}{}-Role".format(self.name_prefix, self.lambda_name),
            description="Role for URL shortener stack",
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")],
        )

        self.lambda_role.attach_inline_policy(self.lambda_role_policy)


    def create_lambda_function(self):
        # Get relative path for folder that contains Lambda function sources
        # ! Note--> we must obtain parent dirs to create path (that's why there is "os.path.dirname()")
        PATH_TO_FUNCTION_FOLDER = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "lambda"
        )
        print("Source code for lambda function obtained from: ", PATH_TO_FUNCTION_FOLDER)

        self.function = aws_lambda.Function(
            self,
            id="{}-Lambda".format(self.construct_id),
            function_name="{}{}".format(self.name_prefix, self.lambda_name),
            code=aws_lambda.Code.from_asset(PATH_TO_FUNCTION_FOLDER),
            handler="url_lambda_function.lambda_handler",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            environment={"TABLE_NAME": self.table_name},
            description="Lambda for URL shortener functionalities (connects with dynamodb to manage URLS).",
            role=self.lambda_role,
            timeout=Duration.seconds(15),
            memory_size=128
        )
