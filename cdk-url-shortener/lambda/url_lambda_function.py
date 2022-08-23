import logging
import os
import json
import uuid
import datetime
import boto3

# Configure logging
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

# Configure AWS resources
TABLE_NAME = os.environ.get("TABLE_NAME")
dynamodb_resource = boto3.resource("dynamodb")
table = dynamodb_resource.Table(TABLE_NAME)


def create_short_url(event):
    target_url = event["queryStringParameters"]["targetUrl"]

    # Create unique identifier
    unique_id = str(uuid.uuid4())[0:8]

    # Add the item in DynamoDB
    response = table.put_item(Item={
        "id": unique_id,
        "target_url": target_url,
        "last_updated": datetime.datetime.now().strftime("%Y/%m%d %H:%M:%S")
    })
    LOG.debug("create_short_url: put_item response is {}".format(response))

    # Create the "redirect" URL

    url = "{}://{}{}/{}".format(
        "https",
        event["requestContext"]["domainName"],
        event["requestContext"]["path"],
        unique_id
    )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps("Created URL is: {}".format(url), sort_keys=True, default=str)
    }


def read_short_url(event):
    unique_id = event["pathParameters"]["url"]

    # Add the item in DynamoDB
    response = table.get_item(Key={"id": unique_id})
    LOG.debug("get_short_url: get_item response is {}".format(response))

    item = response.get("Item", None)

    if item is None:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps("Redirect not found for: {}".format(unique_id), sort_keys=True, default=str)
        }

    return {
        "statusCode": 301,
        "headers": {
            "Location": item.get("target_url")
        }
    }


def lambda_handler(event, context):
    LOG.info("lambda_handler: EVENT is {}".format(event))

    if event["queryStringParameters"] is not None:
        if event["queryStringParameters"]["targetUrl"] is not None:
            return create_short_url(event)

    if event["pathParameters"] is not None and event["pathParameters"]["url"] is not None:
            return read_short_url(event)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "instructions": "Please call this endpoint as the <type_usage> indicates...",
                "create_usage": "?targetUrl=URL",
                "read_usage": "{id_to_search}",
            }
            , sort_keys=True, default=str)
    }
