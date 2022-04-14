import os

import json

import boto3

import time

from datetime import datetime, date, timedelta

import logging

from boto3.dynamodb.conditions import Key

import requests

logger = logging.getLogger()

logger.setLevel('INFO')

TABLE_NAME = os.getenv('DDB_TABLE_NAME', 'auto-lead-scoring')

BUCKET_NAME = os.getenv("ALS_QUICKSIGHT_BUCKET_NAME", "auto-lead-scoring-quicksight")

ALS_AWS_SECRET_KEY = os.getenv("ALS_AWS_SECRET_KEY")

ALS_AWS_ACCESS_KEY = os.getenv("ALS_AWS_ACCESS_KEY")


def get_ddb_table():
    session = get_boto3_session()
    resource = session.resource('dynamodb')
    return resource.Table(TABLE_NAME)

def get_boto3_session():
    """
    Create boto3 session for AWS operations
    Returns:
        Returns boto3 session with given credentials
    """
    logger.info(f'Get boto3 session from credentials')
    aws_region_name = 'us-east-1'
    aws_access_key_id = ALS_AWS_ACCESS_KEY
    aws_secret_access_key = ALS_AWS_SECRET_KEY

    session = boto3.Session(region_name=aws_region_name, aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key)

    # check if credentials are valid
    try:
        session.client('sts').get_caller_identity()
        return session
    except Exception as e:
        raise Exception('Invalid AWS credentials')

table = get_ddb_table()
s3_client = get_boto3_session().client('s3')

def verify_response(response, data):
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if not status_code == 200:
        logger.error(f"Failed to add {data} to the database.")
    else:
        logger.info(f"New entry {data} added successfully.")


def put_file(item, path):
    res = s3_client.put_object(
        Body=json.dumps(item),
        Bucket=BUCKET_NAME,
        Key=path
    )
    verify_response(res, path)


def insert_lead(lead_hash: str, lead_provider: str, response: str):
    item = {
        'pk': f'LEAD#{lead_hash}',
        'sk': lead_provider,
        'response': response,
        'ttl': int( (datetime.fromtimestamp(int(time.time()))+ timedelta(days=120)).timestamp())
    }
    res = table.put_item(Item=item)
    verify_response(res, f"{lead_provider}+'-'+{lead_hash}")


def insert_oem_lead(uuid: str, make: str, model: str, date: str, email: str, phone: str, last_name: str,
                    timestamp: str, make_model_filter_status: str, lead_hash: str, dealer: str, provider: str,
                    postalcode: str):
    item = {
        'pk': f"{make}#{uuid}",
        'sk': f"{make}#{model}",
        'gsipk': f"{make}#{date}",
        'gsisk': "0#0",
        'make': make,
        'model': model,
        'email': email,
        'phone': phone,
        'last_name': last_name,
        'timestamp': timestamp,
        'conversion': "0",
        "make_model_filter_status": make_model_filter_status,
        "lead_hash": lead_hash,
        "dealer": dealer,
        "3pl": provider,
        "postalcode": postalcode,
        'ttl': int( (datetime.fromtimestamp(int(time.time()))+ timedelta(days=30)).timestamp())
    }

    response = table.put_item(Item=item)

    verify_response(response, f"{make}#{email}#{phone}#{last_name}")


def insert_customer_lead(uuid: str, email: str, phone: str, last_name: str, make: str, model: str):
    item = {
        'pk': uuid,
        'sk': 'CUSTOMER_LEAD',
        'gsipk': email,
        'gsisk': uuid,
        'gsipk1': f"{phone}#{last_name}",
        'gsisk1': uuid,
        'oem': make,
        'make': make,
        'model': model,
        'ttl': int( (datetime.fromtimestamp(int(time.time()))+ timedelta(days=30)).timestamp())
    }
    res = table.put_item(Item=item)

    verify_response(res, f"{uuid}#{email}#{phone}")


def lambda_handler(event, context):
    # TODO implement
    logger.info(event)
    body = json.loads(event['Records'][0]['body'])
    logger.info(f"body: {body}" )

    if 'initialize' in body:
        return {
        'statusCode': 200,
        'body': 'Initialized'
    }

    put_file_data = body['put_file']
    insert_lead_data = body['insert_lead']
    insert_customer_lead_data = body.get('insert_customer_lead', None)
    insert_oem_lead_data = body.get('insert_oem_lead', None)

    put_file(item=put_file_data['item'], path=put_file_data['path'])
    insert_lead(
        lead_hash=insert_lead_data['lead_hash'],
        lead_provider=insert_lead_data['service'],
        response=insert_lead_data['response'])

    if insert_customer_lead_data:
        insert_customer_lead(
            uuid=insert_customer_lead_data['lead_uuid'],
            email=insert_customer_lead_data['email'],
            phone=insert_customer_lead_data['phone'],
            last_name=insert_customer_lead_data['last_name'],
            make=insert_customer_lead_data['make'],
            model=insert_customer_lead_data['model']
        )

        insert_oem_lead(
            uuid=insert_oem_lead_data['lead_uuid'],
            make=insert_oem_lead_data['make'],
            model=insert_oem_lead_data['model'],
            date=insert_oem_lead_data['date'],
            email=insert_oem_lead_data['email'],
            phone=insert_oem_lead_data['phone'],
            last_name=insert_oem_lead_data['last_name'],
            timestamp=insert_oem_lead_data['timestamp'],
            make_model_filter_status=insert_oem_lead_data['make_model_filter'],
            lead_hash=insert_oem_lead_data['lead_hash'],
            dealer=insert_oem_lead_data['vendor'],
            provider=insert_oem_lead_data['service'],
            postalcode=insert_oem_lead_data['postalcode']
        )

    return {
        'statusCode': 200,
        'body': 'Done'
    }
