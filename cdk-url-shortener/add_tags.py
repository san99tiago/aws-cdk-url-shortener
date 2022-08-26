#!/usr/bin/env python3
import aws_cdk as cdk

def add_tags_to_stack(stack):
    """
    Simple function to add custom tags to stack in a centralized (equal) approach.
    """

    cdk.Tags.of(stack).add("Environment", "Development")
    cdk.Tags.of(stack).add("RepositoryUrl", "https://github.com/san99tiago/aws-cdk-url-shortener")
    cdk.Tags.of(stack).add("Source", "aws-cdk-url-shortener")
    cdk.Tags.of(stack).add("Owner", "Santiago Garcia Arango")
