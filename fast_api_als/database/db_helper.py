import uuid
import logging
import time
import boto3
import botocore
from boto3.dynamodb.conditions import Key
import dynamodbgeo
from datetime import datetime, timedelta

from fast_api_als import constants
from fast_api_als.utils.boto3_utils import get_boto3_session
"""
    the self.table.some_operation(), return a json object and you can find the http code of the executed operation as this :
    res['ResponseMetadata']['HTTPStatusCode']
    
    write a commong function that logs this response code with appropriate context data
"""

logging.basicConfig(level = logging.INFO , format = '%(asctime)s : %(levelname)s : %(message)s')

def log_HTTP_response_code(caller_fxn_data,res):
    logging.info(f"{caller_fxn_data} returned http response code : {res['ResponseMetadata']['HTTPStatusCode']}")

class DBHelper:
    def __init__(self, session: boto3.session.Session):
        self.session = session
        self.ddb_resource = session.resource('dynamodb', config=botocore.client.Config(max_pool_connections=99))
        self.table = self.ddb_resource.Table(constants.DB_TABLE_NAME)
        self.geo_data_manager = self.get_geo_data_manager()
        self.dealer_table = self.ddb_resource.Table(constants.DEALER_DB_TABLE)
        self.get_api_key_author("Initialize_Connection")

    def get_geo_data_manager(self):
        config = dynamodbgeo.GeoDataManagerConfiguration(self.session.client('dynamodb', config=botocore.client.Config(max_pool_connections=99)), constants.DEALER_DB_TABLE)
        geo_data_manager = dynamodbgeo.GeoDataManager(config)
        return geo_data_manager

    def insert_lead(self, lead_hash: str, lead_provider: str, response: str):
        item = {
            'pk': f'LEAD#{lead_hash}',
            'sk': lead_provider,
            'response': response,
            'ttl': datetime.fromtimestamp(int(time.time())) + timedelta(days=constants.LEAD_ITEM_TTL)
        }
        res = self.table.put_item(Item=item)
        log_HTTP_response_code(f'self.table.put_item in insert_lead', res)

    def insert_oem_lead(self, uuid: str, make: str, model: str, date: str, email: str, phone: str, last_name: str,
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
            'ttl': datetime.fromtimestamp(int(time.time())) + timedelta(days=constants.OEM_ITEM_TTL)
        }

        res = self.table.put_item(Item=item)
        log_HTTP_response_code(f'self.table.put_item in insert_oem_lead', res)

    def check_duplicate_api_call(self, lead_hash: str, lead_provider: str):
        res = self.table.get_item(
            Key={
                'pk': f"LEAD#{lead_hash}",
                'sk': lead_provider
            }
        )
        log_HTTP_response_code(f'self.table.get_item in check_duplicate_api_call', res)
        item = res.get('Item')
        if not item:
            return {
                "Duplicate_Api_Call": {
                    "status": False,
                    "response": "No_Duplicate_Api_Call"
                }
            }
        else:
            return {
                "Duplicate_Api_Call": {
                    "status": True,
                    "response": item['response']
                }
            }

    def accepted_lead_not_sent_for_oem(self, oem: str, date: str):
        res = self.table.query(
            IndexName='gsi-index',
            KeyConditionExpression=Key('gsipk').eq(f"{oem}#{date}")
                                   & Key('gsisk').begins_with("0#0")
        )

        log_HTTP_response_code(f'self.table.query in accepted_lead_not_sent_for_oem', res)

        return res.get('Items', [])

    def update_lead_sent_status(self, uuid: str, oem: str, make: str, model: str):
        res = self.table.get_item(
            Key={
                'pk': f"{uuid}#{oem}"
            }
        )

        log_HTTP_response_code(f'self.table.get_item in update_lead_sent_status', res)

        item = res['Item']
        if not item:
            return False
        item['gsisk'] = "1#0"
        res = self.table.put_item(Item=item)

        log_HTTP_response_code(f'self.table.put_item in update_lead_sent_status', res)

        return True

    def get_make_model_filter_status(self, oem: str):
        res = self.table.get_item(
            Key={
                'pk': f"OEM#{oem}",
                'sk': 'METADATA'
            }
        )
        log_HTTP_response_code(f'self.table.get_item in get_make_model_filter_status', res)

        if res['Item'].get('settings', {}).get('make_model', "False") == 'True':
            return True
        return False

    def verify_api_key(self, apikey: str):
        res = self.table.query(
            IndexName='gsi-index',
            KeyConditionExpression=Key('gsipk').eq(apikey)
        )
        log_HTTP_response_code(f'self.table.query in verify_api_key', res)

        item = res.get('Items', [])
        if len(item) == 0:
            return False
        return True

    def get_auth_key(self, username: str):
        res = self.table.query(
            KeyConditionExpression=Key('pk').eq(username)
        )
        log_HTTP_response_code(f'self.table.query in get_auth_key', res)

        item = res['Items']
        if len(item) == 0:
            return None
        return item[0]['sk']

    def set_auth_key(self, username: str):
        self.delete_3PL(username)
        apikey = str(uuid.uuid4())
        res = self.table.put_item(
            Item={
                'pk': username,
                'sk': apikey,
                'gsipk': apikey
            }
        )

        log_HTTP_response_code(f'self.table.put_item in set_auth_key', res)

        return apikey

    def register_3PL(self, username: str):
        res = self.table.query(
            KeyConditionExpression=Key('pk').eq(username)
        )
        log_HTTP_response_code(f'self.table.query in register_3PL', res)

        item = res.get('Items', [])
        if len(item):
            return None
        return self.set_auth_key(username)

    def set_make_model_oem(self, oem: str, make_model: str):
        item = self.fetch_oem_data(oem)
        item['settings']['make_model'] = make_model
        res = self.table.put_item(Item=item)
        log_HTTP_response_code(f'self.table.put_item in set_make_model_oem', res)

    def fetch_oem_data(self, oem, parallel=False):
        res = self.table.get_item(
            Key={
                'pk': f"OEM#{oem}",
                'sk': "METADATA"
            }
        )
        log_HTTP_response_code(f'self.table.get_item in fetch_oem_data', res)
        if 'Item' not in res:
            return {}
        if parallel:
            return {
                "fetch_oem_data": res['Item']
            }
        else:
            return res['Item']

    def create_new_oem(self, oem: str, make_model: str, threshold: str):
        res = self.table.put_item(
            Item={
                'pk': f"OEM#{oem}",
                'sk': "METADATA",
                'settings': {
                    'make_model': make_model
                },
                'threshold': threshold
            }
        )
        log_HTTP_response_code(f'self.table.put_item in create_new_oem', res)

    def delete_oem(self, oem: str):
        res = self.table.delete_item(
            Key={
                'pk': f"OEM#{oem}",
                'sk': "METADATA"
            }
        )
        log_HTTP_response_code(f'self.table.delete_item in delete_oem', res)

    def delete_3PL(self, username: str):
        authkey = self.get_auth_key(username)
        if authkey:
            res = self.table.delete_item(
                Key={
                    'pk': username,
                    'sk': authkey
                }
            )
            log_HTTP_response_code(f'self.table.delete_item in delete_3PL', res)

    def set_oem_threshold(self, oem: str, threshold: str):
        item = self.fetch_oem_data(oem)
        if item == {}:
            return {
                "error": f"OEM {oem} not found"
            }
        item['threshold'] = threshold
        res = self.table.put_item(Item=item)
        log_HTTP_response_code(f'self.table.put_item in set_oem_threshold', res)

        return {
            "success": f"OEM {oem} threshold set to {threshold}"
        }

    def fetch_nearest_dealer(self, oem: str, lat: str, lon: str):
        query_input = {
            "FilterExpression": "oem = :val1",
            "ExpressionAttributeValues": {
                ":val1": {"S": oem},
            }
        }
        res = self.geo_data_manager.queryRadius(
            dynamodbgeo.QueryRadiusRequest(
                dynamodbgeo.GeoPoint(lat, lon),
                50000,  # radius = 50km
                query_input,
                sort=True
            )
        )
        if len(res) == 0:
            return {}
        res = res[0]
        dealer = {
            'id': {
                '#text': res['dealerCode']['S']
            },
            'vendorname': res['dealerName']['S'],
            'contact': {
                'address': {
                    'postalcode': res['dealerZip']['S']
                }
            }
        }
        return dealer

    def get_dealer_data(self, dealer_code: str, oem: str):
        if not dealer_code:
            return {}
        res = self.dealer_table.query(
            IndexName='dealercode-index',
            KeyConditionExpression=Key('dealerCode').eq(dealer_code) & Key('oem').eq(oem)
        )
        res = res['Items']
        if len(res) == 0:
            return {}
        res = res[0]
        return {
            'postalcode': res['dealerZip'],
            'rating': res['Rating'],
            'recommended': res['Recommended'],
            'reviews': res['LifeTimeReviews']
        }

    def insert_customer_lead(self, uuid: str, email: str, phone: str, last_name: str, make: str, model: str):
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
            'ttl': datetime.fromtimestamp(int(time.time())) + timedelta(days=constants.OEM_ITEM_TTL)
        }
        res = self.table.put_item(Item=item)
        log_HTTP_response_code(f'self.table.put_item in insert_customer_lead', res)


    def lead_exists(self, uuid: str, make: str, model: str):
        lead_exist = False
        if self.get_make_model_filter_status(make):
            res = self.table.query(
                KeyConditionExpression=Key('pk').eq(f"{make}#{uuid}") & Key('sk').eq(f"{make}#{model}")
            )
            log_HTTP_response_code(f'self.table.query in lead_exists', res)

            if len(res['Items']):
                lead_exist = True
        else:
            res = self.table.query(
                KeyConditionExpression=Key('pk').eq(f"{make}#{uuid}")
            )
            log_HTTP_response_code(f'self.table.query in lead_exists', res)

            if len(res['Items']):
                lead_exist = True
        return lead_exist

    def check_duplicate_lead(self, email: str, phone: str, last_name: str, make: str, model: str):
        email_attached_leads = self.table.query(
            IndexName='gsi-index',
            KeyConditionExpression=Key('gsipk').eq(email)
        )
        log_HTTP_response_code(f'self.table.query in check_duplicate_lead', email_attached_leads)

        phone_attached_leads = self.table.query(
            IndexName='gsi1-index',
            KeyConditionExpression=Key('gsipk1').eq(f"{phone}#{last_name}")
        )
        log_HTTP_response_code(f'self.table.query in check_duplicate_lead', phone_attached_leads)

        customer_leads = email_attached_leads['Items'] + phone_attached_leads['Items']

        for item in customer_leads:
            if self.lead_exists(item['pk'], make, model):
                return {"Duplicate_Lead": True}
        return {"Duplicate_Lead": False}

    def get_api_key_author(self, apikey):
        res = self.table.query(
            IndexName='gsi-index',
            KeyConditionExpression=Key('gsipk').eq(apikey)
        )
        log_HTTP_response_code(f'self.table.query in get_api_key_author', res)

        item = res.get('Items', [])
        if len(item) == 0:
            return "unknown"
        return item[0].get("pk", "unknown")

    def update_lead_conversion(self, lead_uuid: str, oem: str, converted: int):
        res = self.table.query(
            KeyConditionExpression=Key('pk').eq(f"{oem}#{lead_uuid}")
        )
        log_HTTP_response_code(f'self.table.query in update_lead_conversion', res)

        items = res.get('Items')
        if len(items) == 0:
            return False, {}
        item = items[0]
        item['oem_responded'] = 1
        item['conversion'] = converted
        item['gsisk'] = f"1#{converted}"
        res = self.table.put_item(Item=item)
        log_HTTP_response_code(f'self.table.put_item in update_lead_conversion', res)
       
        return True, item


def verify_response(response_code):
    if not response_code == 200:
        pass
    else:
        pass


session = get_boto3_session()
db_helper_session = DBHelper(session)
