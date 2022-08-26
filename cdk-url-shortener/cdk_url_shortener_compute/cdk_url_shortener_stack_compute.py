import os

from aws_cdk import (
    Stack,
    CfnOutput,
    Fn,
    Duration,
    aws_lambda,
    aws_iam,
    aws_apigateway,
)
from constructs import Construct

class CdkUrlShortenerStackCompute(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        name_prefix: str,
        main_resources_name: str,
        deployment_environment: str,
        deployment_version: str,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.construct_id = construct_id
        self.name_prefix = name_prefix
        self.main_resources_name = main_resources_name
        self.deployment_environment = deployment_environment
        self.deployment_version = deployment_version

        # Obtain important values from outputs of other stacks
        self.load_values_from_other_stacks_outputs()

        # Lambda function creation
        self.create_policy_statement_for_lambda_to_dynamodb()
        self.create_lambda_role_policy()
        self.create_lambda_role()
        self.create_lambda_function()

        # API gateway creation
        self.create_api_gateway()

        # Relevant CloudFormation outputs
        self.show_cloudformation_outputs()


    def load_values_from_other_stacks_outputs(self):
        """
        Method to load outputs from other stacks to use in this one (decoupled approach).
        """
        self.table_arn = Fn.import_value("DynamoDBTableARN")
        print("Loaded <table_arn> value from other stack output is: ", self.table_arn)


    def create_policy_statement_for_lambda_to_dynamodb(self):
        """
        Method to create IAM policy statement for dynamodb usage.
        """
        self.dynamodb_access_policy_statement = aws_iam.PolicyStatement(
            actions=[
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:BatchWriteItem",
                "dynamodb:GetItem",
                "dynamodb:BatchGetItem",
                "dynamodb:Scan",
                "dynamodb:Query",
                "dynamodb:ConditionCheckItem"
            ],
            effect=aws_iam.Effect.ALLOW,
            resources=[
                self.table_arn,
                "{}/index/*".format(self.table_arn),
            ],
        )


    def create_lambda_role_policy(self):
        """
        Method to create IAM Policy based on all policy statements.
        """
        self.lambda_role_policy = aws_iam.Policy(
            self,
            id="{}-Policy".format(self.construct_id),
            policy_name="{}{}-Policy".format(self.name_prefix, self.main_resources_name),
            statements=[
                self.dynamodb_access_policy_statement,
            ],
        )


    def create_lambda_role(self):
        """
        Method that creates the role for Lambda function execution.
        """
        self.lambda_role = aws_iam.Role(
            self,
            id="{}-Role".format(self.construct_id),
            role_name="{}{}-Role".format(self.name_prefix, self.main_resources_name),
            description="Role for URL shortener stack",
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")],
        )

        self.lambda_role.attach_inline_policy(self.lambda_role_policy)


    def create_lambda_function(self):
        """
        Method that creates the main Lambda function.
        """
        # Get relative path for folder that contains Lambda function sources
        # ! Note--> we must obtain parent dirs to create path (that's why there is "os.path.dirname()")
        PATH_TO_FUNCTION_FOLDER = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "lambda"
        )
        print("Source code for lambda function obtained from: ", PATH_TO_FUNCTION_FOLDER)

        self.lambda_function = aws_lambda.Function(
            self,
            id="{}-Lambda".format(self.construct_id),
            function_name="{}{}".format(self.name_prefix, self.main_resources_name),
            code=aws_lambda.Code.from_asset(PATH_TO_FUNCTION_FOLDER),
            handler="url_lambda_function.lambda_handler",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            environment={"TABLE_NAME": "{}{}-Table".format(self.name_prefix, self.main_resources_name)},
            description="Lambda for URL shortener functionalities (connects with dynamodb to manage URLS).",
            role=self.lambda_role,
            timeout=Duration.seconds(15),
            memory_size=128,
        )

        self.lambda_function.add_alias(self.deployment_environment)


    def create_api_gateway(self):
        """
        Method that creates the API Gateway.
        """

        self.api = aws_apigateway.LambdaRestApi(
            self,
            id="{}-RestApi".format(self.construct_id),
            rest_api_name="{}{}".format(self.name_prefix, self.main_resources_name),
            description="API to create/read URLs for the shortener stack",
            handler=self.lambda_function,
            default_cors_preflight_options=aws_apigateway.CorsOptions(
                allow_origins=aws_apigateway.Cors.ALL_ORIGINS,
                allow_methods=["GET"],
            ),
            deploy_options=aws_apigateway.StageOptions(
                stage_name=self.deployment_version,
                description="{} release for handling requests that interact with the URL shortener stack".format(self.deployment_environment),
            ),
            deploy=True,
            retain_deployments=False,
            proxy=False,
        )

        self.urls_resource = self.api.root.add_resource("urls")
        self.urls_resource.add_method("GET") # GET /urls

        self.api_items = self.urls_resource.add_resource("{url}")
        self.api_items.add_method("GET") # GET /urls/{url}


    def show_cloudformation_outputs(self):
        """
        Method to create/add the relevant CloudFormation outputs.
        """
        CfnOutput(
            self,
            "DeploymentVersion",
            value=self.deployment_version,
            description="Current deployment's version",
        )

        CfnOutput(
            self,
            "DeploymentEnvironment",
            value=self.deployment_environment,
            description="Deployment environment",
        )

        CfnOutput(
            self,
            "NamePrefixes",
            value=self.name_prefix,
            description="Name prefixes for the resources",
        )

        CfnOutput(
            self,
            "LambdaFunctionARN",
            value=self.lambda_function.function_arn,
            description="ARN of the created Lambda function",
        )

        CfnOutput(
            self,
            "LambdaFunctionRoleARN",
            value=self.lambda_function.role.role_arn,
            description="Role for the created Lambda function",
        )

        CfnOutput(
            self,
            "BaseApiUrl",
            value=self.api.rest_api_id,
            description="Base URL for the API endpoint (includes latest stage)",
        )

        CfnOutput(
            self,
            "CompleteApiUrl",
            value="{}{}".format(self.api.url, "urls"),
            description="Complete URL for the API endpoint",
        )
