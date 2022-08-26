#!/usr/bin/env python3
import aws_cdk as cdk

import add_tags
from cdk_url_shortener_compute.cdk_url_shortener_stack_compute import CdkUrlShortenerStackCompute


DEPLOYMENT_VERSION = "v1"
DEPLOYMENT_ENVIRONMENT = "dev"
NAME_PREFIX = "santi-{}-".format(DEPLOYMENT_ENVIRONMENT)
MAIN_RESOURCES_NAME = "urls-shortener"

app = cdk.App()

compute_stack = CdkUrlShortenerStackCompute(
    app,
    "{}-stack-compute-cdk".format(MAIN_RESOURCES_NAME),
    NAME_PREFIX,
    MAIN_RESOURCES_NAME,
    DEPLOYMENT_ENVIRONMENT,
    DEPLOYMENT_VERSION,
)

add_tags.add_tags_to_stack(compute_stack)

app.synth()
