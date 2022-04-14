import time
import uuid
from fastapi import APIRouter, BackgroundTasks
import logging

from datetime import datetime

from fastapi import Request, HTTPException, Depends
from fastapi.security.api_key import APIKey
from starlette.status import HTTP_403_FORBIDDEN
from concurrent.futures import ThreadPoolExecutor, as_completed

from fast_api_als.constants import SUPPORTED_OEMS
from fast_api_als.services.authenticate import get_api_key
from fast_api_als.services.enrich.customer_info import get_contact_details
from fast_api_als.services.enrich.demographic_data import get_customer_coordinate
from fast_api_als.services.enrich_lead import get_enriched_lead_json
from fast_api_als.services.new_verify_phone_and_email import new_verify_phone_and_email
from fast_api_als.utils.adf import parse_xml, check_validation
from fast_api_als.utils.calculate_lead_hash import calculate_lead_hash
from fast_api_als.database.db_helper import db_helper_session
from fast_api_als.services.ml_helper import conversion_to_ml_input, score_ml_input, check_threshold
from fast_api_als.utils.quicksight_utils import create_quicksight_data
from fast_api_als.quicksight.s3_helper import s3_helper_client
from fast_api_als.utils.sqs_utils import sqs_helper_session

router = APIRouter()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


def calculate_time(t1):
    elapsed_time = int(time.time() * 1000.0) - t1[0]
    t1[0] = int(time.time() * 1000.0)
    return elapsed_time


@router.post("/submit/")
async def submit(file: Request, background_tasks: BackgroundTasks, apikey: APIKey = Depends(get_api_key)):
    start = int(time.time() * 1000.0)
    t1 = [int(time.time() * 1000.0)]
    if not db_helper_session.verify_api_key(apikey):
        logger.info(f"Wrong Api Key Received")
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Wrong API Key"
        )
    body = await file.body()
    body = str(body, 'utf-8')

    logger.info(f"input body to XML took: {calculate_time(t1)} ms")
    obj = parse_xml(body)
    logger.info(f"XML verification took parsed: {calculate_time(t1)} ms")

    # check if xml is not parsable
    if not obj:
        logger.info(f"Error occured while parsing XML")
        provider = db_helper_session.get_api_key_author(apikey)
        obj = {
            'provider': {
                'service': provider
            }
        }
        item, path = create_quicksight_data(obj, 'unknown_hash', 'REJECTED', '1_INVALID_XML', {})
        s3_helper_client.put_file(item, path)
        return {
            "status": "REJECTED",
            "code": "1_INVALID_XML",
            "message": "Error occured while parsing XML"
        }
    logger.info(f"Adf file successfully parsed {obj}")
    lead_hash = calculate_lead_hash(obj)
    logger.info(f"Lead hash calculated: {lead_hash}")
    logger.info(f"Lead hash verification took: {calculate_time(t1)} ms")

    # check if adf xml is valid
    validation_check, validation_code, validation_message = check_validation(obj)

    logger.info(f"validation message: {validation_message}")
    logger.info(f"ADF Validation took: {calculate_time(t1)} ms")

    if not validation_check:
        item, path = create_quicksight_data(obj['adf']['prospect'], lead_hash, 'REJECTED', validation_code, {})
        s3_helper_client.put_file(item, path)
        return {
            "status": "REJECTED",
            "code": validation_code,
            "message": validation_message
        }

    # check if vendor is available here
    dealer_available = True if obj['adf']['prospect'].get('vendor', None) else False
    email, phone, last_name = get_contact_details(obj)
    make = obj['adf']['prospect']['vehicle']['make']
    model = obj['adf']['prospect']['vehicle']['model']

    logger.info(f"{dealer_available}::{email}:{phone}:{last_name}::{make}")

    fetched_oem_data = {}
    # check if 3PL is making a duplicate call or it is a duplicate lead
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(db_helper_session.check_duplicate_api_call, lead_hash,
                                   obj['adf']['prospect']['provider']['service']),
                   executor.submit(db_helper_session.check_duplicate_lead, email, phone, last_name, make, model),
                   executor.submit(db_helper_session.fetch_oem_data, make, True)
                   ]
        for future in as_completed(futures):
            result = future.result()
            if result.get('Duplicate_Api_Call', {}).get('status', False):
                logger.info(f"Duplicate API Call")
                return {
                    "status": f"Already {result['Duplicate_Api_Call']['response']}",
                    "message": "Duplicate Api Call"
                }
            if result.get('Duplicate_Lead', False):
                logger.info(f"Duplicate Lead")
                return {
                    "status": "REJECTED",
                    "code": "12_DUPLICATE",
                    "message": "This is a duplicate lead"
                }
            if "fetch_oem_data" in result:
                fetched_oem_data = result['fetch_oem_data']
    logger.info(f"Duplicate check took: {calculate_time(t1)} ms")
    if fetched_oem_data == {}:
        logger.info(f"OEM data not found")
        return {
            "status": "REJECTED",
            "code": "20_OEM_DATA_NOT_FOUND",
            "message": "OEM data not found"
        }
    if 'threshold' not in fetched_oem_data:
        logger.info(f"Threshold not set for {make}")
        return {
            "status": "REJECTED",
            "code": "20_OEM_DATA_NOT_FOUND",
            "message": "OEM data not found"
        }
    oem_threshold = float(fetched_oem_data['threshold'])

    # if dealer is not available then find nearest dealer
    if not dealer_available:
        lat, lon = get_customer_coordinate(obj['adf']['prospect']['customer']['contact']['address']['postalcode'])
        nearest_vendor = db_helper_session.fetch_nearest_dealer(oem=make,
                                                                lat=lat,
                                                                lon=lon)
        obj['adf']['prospect']['vendor'] = nearest_vendor
        dealer_available = True if nearest_vendor != {} else False
        logger.info(f"Finding nearest dealer took: {calculate_time(t1)} ms")

    # enrich the lead
    model_input = get_enriched_lead_json(obj)
    logger.info(model_input)
    logger.info(f"Enriching lead took: {calculate_time(t1)} ms")

    # convert the enriched lead to ML input format
    ml_input = conversion_to_ml_input(model_input, make, dealer_available)
    logger.info(ml_input, len(ml_input))
    logger.info(f"Converting to ML input took: {calculate_time(t1)} ms")

    # score the lead
    result = score_ml_input(ml_input, make, dealer_available)
    logger.info(f"ml score: {result}")
    logger.info(f"Scoring lead took: {calculate_time(t1)} ms")

    # create the response
    response_body = {}
    if result >= oem_threshold:
        response_body["status"] = "ACCEPTED"
        response_body["code"] = "0_ACCEPTED"
    else:
        response_body["status"] = "REJECTED"
        response_body["code"] = "16_LOW_SCORE"

    # verify the customer
    if response_body['status'] == 'ACCEPTED':
        contact_verified = await new_verify_phone_and_email(email, phone)
        if not contact_verified:
            response_body['status'] = 'REJECTED'
            response_body['code'] = '17_FAILED_CONTACT_VALIDATION'

    logger.info(f"Validating customer took: {calculate_time(t1)} ms")
    item, path = create_quicksight_data(obj['adf']['prospect'], lead_hash, response_body['status'],
                                        response_body['code'], model_input)

    # insert the lead into ddb with oem & customer details
    # delegate inserts to sqs queue
    if response_body['status'] == 'ACCEPTED':
        lead_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, email + phone + last_name + make + model))
        make_model_filter = db_helper_session.get_make_model_filter_status(make)
        logger.info(f"make_model_filter took: {calculate_time(t1)} ms")
        message = {
            'put_file': {
                'item': item,
                'path': path
            },
            'insert_lead': {
                'lead_hash': lead_hash,
                'service': obj['adf']['prospect']['provider']['service'],
                'response': response_body['status']
            },
            'insert_oem_lead': {
                'lead_uuid': lead_uuid,
                'make': make,
                'model': model,
                'date': datetime.today().strftime('%Y-%m-%d'),
                'email': email,
                'phone': phone,
                'last_name': last_name,
                'timestamp': datetime.today().strftime('%Y-%m-%d-%H:%M:%S'),
                'make_model_filter': make_model_filter,
                'lead_hash': lead_hash,
                'vendor': obj['adf']['prospect']['vendor'].get('vendorname', 'unknown'),
                'service': obj['adf']['prospect']['provider']['service'],
                'postalcode': obj['adf']['prospect']['customer']['contact']['address']['postalcode']
            },
            'insert_customer_lead': {
                'lead_uuid': lead_uuid,
                'email': email,
                'phone': phone,
                'last_name': last_name,
                'make': make,
                'model': model
            }
        }
        logger.info(f"Message to be sent to queue: {message}")
        res = sqs_helper_session.send_message(message)
        logger.info(f"Sending message to sqs queue took: {calculate_time(t1)} ms")

    else:
        message = {
            'put_file': {
                'item': item,
                'path': path
            },
            'insert_lead': {
                'lead_hash': lead_hash,
                'service': obj['adf']['prospect']['provider']['service'],
                'response': response_body['status']
            }
        }
        res = sqs_helper_session.send_message(message)
        logger.info(f"Storing lead parallely took: {calculate_time(t1)} ms")
    time_taken = (int(time.time() * 1000.0) - start)

    response_body["message"] = f"{result} Response Time : {time_taken} ms"
    logger.info(
        f"Lead {response_body['status']} with code: {response_body['code']} and message: {response_body['message']}")
    return response_body
