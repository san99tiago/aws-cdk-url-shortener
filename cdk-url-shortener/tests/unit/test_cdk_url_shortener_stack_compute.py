import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_url_shortener_compute.cdk_url_shortener_stack_compute import CdkUrlShortenerStackCompute

DEPLOYMENT_VERSION = "v1"
DEPLOYMENT_ENVIRONMENT = "dev"
NAME_PREFIX = "santi-{}-".format(DEPLOYMENT_ENVIRONMENT)
MAIN_RESOURCES_NAME = "urls-shortener"

app = core.App()

stack = CdkUrlShortenerStackCompute(
    app,
    "{}-stack-compute-cdk".format(MAIN_RESOURCES_NAME),
    NAME_PREFIX,
    MAIN_RESOURCES_NAME,
    DEPLOYMENT_ENVIRONMENT,
    DEPLOYMENT_VERSION,
)
template = assertions.Template.from_stack(stack)

def test_iam_policy_for_lambda_created():

    template.has_resource_properties(
        "AWS::IAM::Policy",
        {
            "PolicyDocument": {
                "Statement": [
                    {
                        "Action": [
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
                        "Effect": "Allow",
                    }
                ]
            },
            "PolicyName": "santi-dev-urls-shortener-Policy",
        }
    )


def test_iam_role_for_lambda_created():
    template.has_resource_properties(
        "AWS::IAM::Role",
        {
            "AssumeRolePolicyDocument": {
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    }
                }
            ],
            },
            "RoleName": "santi-dev-urls-shortener-Role",
        }
    )


def test_lambda_created():
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "FunctionName": "santi-dev-urls-shortener",
            "Handler": "url_lambda_function.lambda_handler",
            "MemorySize": 128,
            "Runtime": "python3.9",
            "Timeout": 15
        }
    )


def test_api_created():
    template.has_resource_properties(
        "AWS::ApiGateway::RestApi",
        {
            "Name": "santi-dev-urls-shortener",
        }
    )
    template.has_resource_properties(
        "AWS::ApiGateway::Stage",
        {
            "StageName": "v1",
        }
    )
    template.has_resource_properties(
        "AWS::ApiGateway::Resource",
        {
            "PathPart": "{url}",
        }
    )
    template.has_resource_properties(
        "AWS::ApiGateway::Resource",
        {
            "PathPart": "urls",
        }
    )

