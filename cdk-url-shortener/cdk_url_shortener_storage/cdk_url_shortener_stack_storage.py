import os

from aws_cdk import (
    Stack,
    CfnOutput,
    aws_dynamodb,
    RemovalPolicy,
)
from constructs import Construct

class CdkUrlShortenerStackStorage(Stack):

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

        # DynamoDB creation
        self.create_dynamodb_table()

        # Relevant CloudFormation outputs
        self.show_cloudformation_outputs()


    def create_dynamodb_table(self):
        """
        Method to create the DynamoDB Table.
        """
        self.table = aws_dynamodb.Table(
            self,
            id="{}-Table".format(self.construct_id),
            table_name="{}{}-Table".format(self.name_prefix, self.main_resources_name),
            read_capacity=1,
            write_capacity=1,
            partition_key=aws_dynamodb.Attribute(name="id", type=aws_dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,
        )


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
            "DynamoDBTableName",
            value=self.table.table_name,
            description="Name of the DynamoDB table",
        )

        CfnOutput(
            self,
            "DynamoDBTableARN",
            value=self.table.table_arn,
            description="ARN of the DynamoDB table",
            export_name="DynamoDBTableARN"
        )
