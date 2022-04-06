import os
import json
import boto3
from datetime import date, timedelta
import logging
from boto3.dynamodb.conditions import Key
import requests
logger = logging.getLogger()
logger.setLevel('INFO')
OEM_ENDPOINT = {
     'Hyundai': "https://hyundai_submit_lead.com/",
     'BMW': "https://BMW_submit_lead.com/"
 }

DB_TABLE_NAME = os.getenv('DB_TABLE_NAME', 'auto-lead-scoring')
ddb_resource = boto3.resource('dynamodb')
table = ddb_resource.Table(DB_TABLE_NAME)

def get_unsent_lead_on_a_date(val):
    res = table.query(
            IndexName='gsi-index',
            KeyConditionExpression=Key('gsipk').eq(val) & Key('gsisk').begins_with('0#')
        )
    return res['Items']

def get_unsent_leads(oem):
    todays_date = date.today()
    previous_date = todays_date - timedelta(days=1)

    leadsa = get_unsent_lead_on_a_date( f"{oem}#{str(todays_date)}" )
    leadsb = get_unsent_lead_on_a_date( f"{oem}#{str(previous_date)}" )
    return leadsa+leadsb

def lambda_handler(event, context):

    oem = event['oem']

    unsent_leads = get_unsent_leads(oem)
    logger.info(unsent_leads)

    try:
        response = requests.post(OEM_ENDPOINT.get(oem, ""), data=json.dumps(unsent_leads))
        return {
        'statusCode': response.status_code,
        }
    except Exception as e:
        logger.info(f"exception occured while sending lead top oem endpoint: {e}")
        return {
            "statusCode": "406"
        }
