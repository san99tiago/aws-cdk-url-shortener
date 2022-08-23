#!/usr/bin/env python3
import aws_cdk as cdk

from cdk_url_shortener.cdk_url_shortener_stack import CdkUrlShortenerStack

DEPLOYMENT_VERSION = "v1"
DEPLOYMENT_ENVIRONMENT = "dev"
NAME_PREFIX = "santi-{}-".format(DEPLOYMENT_ENVIRONMENT)
MAIN_RESOURCES_NAME = "urls-shortener"

app = cdk.App()
cool_stack = CdkUrlShortenerStack(
    app,
    "{}-stack-cdk".format(MAIN_RESOURCES_NAME),
    NAME_PREFIX,
    MAIN_RESOURCES_NAME,
    DEPLOYMENT_ENVIRONMENT,
    DEPLOYMENT_VERSION,
)

cdk.Tags.of(cool_stack).add("Environment", "Development")
cdk.Tags.of(cool_stack).add("RepositoryUrl", "https://github.com/san99tiago/aws-cdk-url-shortener")
cdk.Tags.of(cool_stack).add("Source", "aws-cdk-url-shortener")
cdk.Tags.of(cool_stack).add("Owner", "Santiago Garcia Arango")

app.synth()
