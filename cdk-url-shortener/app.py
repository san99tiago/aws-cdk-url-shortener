#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_url_shortener.cdk_url_shortener_stack import CdkUrlShortenerStack

NAME_PREFIX = "Santi-Dev-"
TABLE_NAME = "Urls"
LAMBDA_NAME = "Url-Shortener-Lambda"

app = cdk.App()
cool_stack = CdkUrlShortenerStack(
    app,
    "{}CdkUrlShortenerStack".format(NAME_PREFIX),
    NAME_PREFIX,
    TABLE_NAME,
    LAMBDA_NAME
)

cdk.Tags.of(cool_stack).add("Environment", "Development")
cdk.Tags.of(cool_stack).add("RepositoryUrl", "https://github.com/san99tiago/aws-cdk-url-shortener")
cdk.Tags.of(cool_stack).add("Source", "aws-cdk-url-shortener")
cdk.Tags.of(cool_stack).add("Owner", "Santiago Garcia Arango")

app.synth()
