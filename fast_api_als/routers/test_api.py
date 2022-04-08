import asyncio
import time
import uuid

from fastapi import APIRouter, BackgroundTasks
import logging
from datetime import datetime
import concurrent.futures
from multiprocessing.dummy import Pool
from concurrent.futures import ThreadPoolExecutor, as_completed

# pool = Pool(10)

from starlette.status import HTTP_403_FORBIDDEN

from fast_api_als.constants import (
    HYU_DEALER_ENDPOINT_NAME, SUPPORTED_OEMS,
)
from fast_api_als.database.db_helper import db_helper_session
from fast_api_als.quicksight.s3_helper import s3_helper_client
from fast_api_als.services.alternate_verify_phone_and_email import alternate_verify_phone_and_email
from fast_api_als.services.enrich.customer_info import get_contact_details
from fast_api_als.services.enrich.demographic_data import get_customer_coordinate
from fast_api_als.services.enrich_lead import get_enriched_lead_json
from fast_api_als.services.ml_helper import conversion_to_ml_input, score_ml_input, check_threshold
from fast_api_als.services.predict_score import ml_predict_score
from fast_api_als.utils.adf import parse_xml, check_validation
from fast_api_als.ml_init_data.HYU.ml_init_data import dummy_data
from fast_api_als.services.authenticate import get_api_key

from fastapi import Request, HTTPException, Depends
from fastapi.security.api_key import APIKey

from fast_api_als.utils.calculate_lead_hash import calculate_lead_hash
from fast_api_als.utils.quicksight_utils import create_quicksight_data

router = APIRouter()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


def calculate_time(t1):
    elapsed_time = int(time.time()*1000.0) - t1[0]
    t1[0] = int(time.time()*1000.0)
    return elapsed_time


@router.post("/parse/")
async def predict(file: Request):
    start = time.process_time()
    body = await file.body()
    body = str(body, 'utf-8')

    obj = parse_xml(body)

    if not obj:
        return {
            "status": "REJECTED",
            "code": "1_INVALID_XML",
            "message": "Error occured while parsing XML"
        }

    validation_check, validation_message = check_validation(obj)

    logger.info(f"validation message: {validation_message}")

    if not validation_check:
        return {
            "status": "REJECTED",
            "code": "6_MISSING_FIELD",
            "message": validation_message
        }

    model_input = get_enriched_lead_json(obj)
    logger.info(model_input)
    return model_input


@router.post("/predict/")
def predict():
    start = time.process_time()
    result = ml_predict_score(dummy_data, HYU_DEALER_ENDPOINT_NAME)
    time_taken = (time.process_time() - start) * 1000
    response_body = {}
    if result > 0.033:
        response_body["status"] = "ACCEPTED"
        response_body["code"] = "0_ACCEPTED"
    else:
        response_body["status"] = "REJECTED"
        response_body["code"] = "16_LOW_SCORE"
    response_body["message"] = f" Response Time : {time_taken} ms"
    return response_body


# submit lead without inserting into DDB
@router.post("/submit-test/")
async def submit_test(file: Request, apikey: APIKey = Depends(get_api_key)):
    start = time.process_time()
    if not db_helper_session.verify_api_key(apikey):
        logger.info(f"Wrong Api Key Received")
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Wrong API Key"
        )
    body = await file.body()
    body = str(body, 'utf-8')

    obj = parse_xml(body)

    if not obj:
        logger.info(f"Error occured while parsing XML")
        return {
            "status": "REJECTED",
            "code": "1_INVALID_XML",
            "message": "Error occured while parsing XML"
        }
    logger.info(f"Adf file successfully parsed {obj}")
    validation_check, validation_code, validation_message = check_validation(obj)

    logger.info(f"validation message: {validation_message}")

    if not validation_check:
        return {
            "status": "REJECTED",
            "code": validation_code,
            "message": validation_message
        }
    make = obj['adf']['prospect']['vehicle']['make']
    if make.lower() not in SUPPORTED_OEMS:
        return {
            "status": "REJECTED",
            "code": "19_OEM_NOT_SUPPORTED",
            "message": f"Do not support OEM: {make}"
        }
    model_input = get_enriched_lead_json(obj)
    logger.info(model_input)
    # check if vendor is available here
    dealer_available = True if obj['adf']['prospect'].get('vendor', None) else False
    response_body = {}
    ml_input = conversion_to_ml_input(model_input, make, dealer_available)
    logger.info(ml_input)
    result = score_ml_input(ml_input, make, dealer_available)
    logger.info(f"{make} ml score: {result}")
    if check_threshold(result, make, dealer_available):
        response_body["status"] = "ACCEPTED"
        response_body["code"] = "0_ACCEPTED"
    else:
        response_body["status"] = "REJECTED"
        response_body["code"] = "16_LOW_SCORE"
    email, phone, last_name = get_contact_details(obj)

    if response_body['status'] == 'ACCEPTED':
        # contact_verified = await verify_phone_and_email(email, phone)
        start_time = time.time()
        contact_verified = await alternate_verify_phone_and_email(email['#text'], phone)
        process_time = time.time() - start_time
        logger.info(f"Time Taken for validation {process_time * 1000}")
        if not contact_verified:
            response_body['status'] = 'REJECTED'
            response_body['code'] = '17_FAILED_CONTACT_VALIDATION'

    time_taken = (time.process_time() - start) * 1000
    response_body["message"] = f" {result} Response Time : {time_taken} ms"
    logger.info(
        f"Lead {response_body['status']} with code: {response_body['code']} and message: {response_body['message']}")
    return response_body

# api for load testing ( do not use 3rd party service and do not check for duplicate api calls )
@router.post("/submit_load/")
async def submit1(file: Request, background_tasks: BackgroundTasks, apikey: APIKey = Depends(get_api_key)):
    start = int(time.time()*1000.0)
    t1 = [int(time.time()*1000.0)]
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
        item, path = create_quicksight_data(obj, 'unknown_hash', 'REJECTED', '1_INVALID_XML')
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

    # check if 3PL is making a duplicate call
    # duplicate_call, response = db_helper_session.check_duplicate_api_call(lead_hash,
    #                                                                       obj['adf']['prospect']['provider']['service'])
    # if duplicate_call:
    #     logger.info("Duplicate Api Call")
    #     return {
    #         "status": f"Already {response}",
    #         "message": "Duplicate Api Call"
    #     }

    # check if adf xml is valid
    validation_check, validation_code, validation_message = check_validation(obj)

    logger.info(f"validation message: {validation_message}")
    logger.info(f"ADF Validation took: {calculate_time(t1)} ms")

    if not validation_check:
        item, path = create_quicksight_data(obj['adf']['prospect'], lead_hash, 'REJECTED', validation_code)
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

    # if dealer is not available then find nearest dealer
    if not dealer_available:
        lat, lon = get_customer_coordinate(obj['adf']['prospect']['customer']['contact']['address']['postalcode'])
        nearest_vendor = db_helper_session.fetch_nearest_dealer(oem=make,
                                                                lat=lat,
                                                                lon=lon)
        obj['adf']['prospect']['vendor'] = nearest_vendor
        logger.info(f"Finding nearest dealer took: {calculate_time(t1)} ms")

    # check if the lead is duplicated
    # if db_helper_session.check_duplicate_lead(email, phone, last_name, make,
    #                                           model):
    #     return {
    #         "status": "REJECTED",
    #         "code": "12_DUPLICATE",
    #         "message": "This is a duplicate lead"
    #     }

    # enrich the lead
    model_input = get_enriched_lead_json(obj)
    logger.info(model_input)
    logger.info(f"Enriching lead took: {calculate_time(t1)} ms")

    # convert the enriched lead to ML input format
    ml_input = conversion_to_ml_input(model_input, make, dealer_available)
    logger.info(ml_input)
    logger.info(f"Converting to ML input took: {calculate_time(t1)} ms")

    # score the lead
    result = score_ml_input(ml_input, make, dealer_available)
    logger.info(f"ml score: {result}")
    logger.info(f"Scoring lead took: {calculate_time(t1)} ms")

    # create the response
    response_body = {}
    if check_threshold(result, make, dealer_available):
        response_body["status"] = "ACCEPTED"
        response_body["code"] = "0_ACCEPTED"
    else:
        response_body["status"] = "REJECTED"
        response_body["code"] = "16_LOW_SCORE"

    # verify the customer
    if response_body['status'] == 'ACCEPTED':
        # contact_verified = await verify_phone_and_email(email, phone)
        # if not contact_verified:
        #     response_body['status'] = 'REJECTED'
        #     response_body['code'] = '17_FAILED_CONTACT_VALIDATION'
        time.sleep(.500)

    # Inserting all data parallely
    # create and dump data for quicksight analysis
    logger.info(f"Validating customer took: {calculate_time(t1)} ms")
    item, path = create_quicksight_data(obj['adf']['prospect'], lead_hash, response_body['status'],
                                        response_body['code'])

    # insert the lead into ddb with oem details
    if response_body['status'] == 'ACCEPTED':
        lead_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, email + phone + last_name + make + model))
        make_model_filter = db_helper_session.get_make_model_filter_status(make)
        logger.info(f"make_model_filter took: {calculate_time(t1)} ms")
        background_tasks.add_task(s3_helper_client.put_file, item, path)
        background_tasks.add_task(db_helper_session.insert_lead, lead_hash,
                                  obj['adf']['prospect']['provider']['service'], response_body['status'])
        background_tasks.add_task(db_helper_session.insert_oem_lead, lead_uuid, make, model,
                                  datetime.today().strftime('%Y-%m-%d'), email, phone, last_name,
                                  datetime.today().strftime('%Y-%m-%d-%H:%M:%S'), make_model_filter, lead_hash,
                                  obj['adf']['prospect']['vendor'].get('vendorname', 'unknown'),
                                  obj['adf']['prospect']['provider']['service'],
                                  obj['adf']['prospect']['customer']['contact']['address']['postalcode'])
        background_tasks.add_task(db_helper_session.insert_customer_lead, lead_uuid, email, phone,
                                  last_name, make, model)
        logger.info(f"Storing lead parallely took: {calculate_time(t1)} ms")
    else:
        background_tasks.add_task(s3_helper_client.put_file, item, path)
        background_tasks.add_task(db_helper_session.insert_lead, lead_hash,
                                  obj['adf']['prospect']['provider']['service'], response_body['status'])
        logger.info(f"Storing lead parallely took: {calculate_time(t1)} ms")
    time_taken = (int(time.time() * 1000.0) - start)

    response_body["message"] = f"{result} Response Time : {time_taken} ms"
    logger.info(
        f"Lead {response_body['status']} with code: {response_body['code']} and message: {response_body['message']}")
    return response_body