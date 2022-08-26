import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_url_shortener_storage.cdk_url_shortener_stack_storage import CdkUrlShortenerStackStorage


DEPLOYMENT_VERSION = "v1"
DEPLOYMENT_ENVIRONMENT = "dev"
NAME_PREFIX = "santi-{}-".format(DEPLOYMENT_ENVIRONMENT)
MAIN_RESOURCES_NAME = "urls-shortener"

app = core.App()

stack = CdkUrlShortenerStackStorage(
    app,
    "{}-stack-storage-cdk".format(MAIN_RESOURCES_NAME),
    NAME_PREFIX,
    MAIN_RESOURCES_NAME,
    DEPLOYMENT_ENVIRONMENT,
    DEPLOYMENT_VERSION,
)
template = assertions.Template.from_stack(stack)


def test_dynamodb_table_created():

    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        {
            "KeySchema": [
                {
                    "AttributeName": "id",
                    "KeyType": "HASH"
                }
            ],
            "AttributeDefinitions": [
                {
                    "AttributeName": "id",
                    "AttributeType": "S"
                }
            ],
            "ProvisionedThroughput": {
                "ReadCapacityUnits": 1,
                "WriteCapacityUnits": 1
            },
            "TableName": "santi-dev-urls-shortener-Table",
        }
    )


def test_mandatory_outputs():
    template.has_output(
        "DynamoDBTableARN",
        {
            "Export": {
                "Name": "DynamoDBTableARN"
            }
        })
