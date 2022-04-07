import time
import uuid
from fastapi import APIRouter
import logging

from datetime import datetime

from fastapi import Request, HTTPException, Depends
from fastapi.security.api_key import APIKey
from starlette.status import HTTP_403_FORBIDDEN

from fast_api_als.constants import SUPPORTED_OEMS

from fast_api_als.services.authenticate import get_api_key
from fast_api_als.services.enrich.customer_info import get_contact_details
from fast_api_als.services.enrich.demographic_data import get_customer_coordinate
from fast_api_als.services.enrich_lead import get_enriched_lead_json
from fast_api_als.services.verify_phone_and_email import verify_phone_and_email
from fast_api_als.utils.adf import parse_xml, check_validation
from fast_api_als.utils.calculate_lead_hash import calculate_lead_hash
from fast_api_als.database.db_helper import db_helper_session
from fast_api_als.services.ml_helper import conversion_to_ml_input, score_ml_input, check_threshold
from fast_api_als.utils.quicksight_utils import create_quicksight_data
from fast_api_als.quicksight.s3_helper import s3_helper_client

router = APIRouter()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


@router.post("/submit/")
async def submit(file: Request, apikey: APIKey = Depends(get_api_key)):
    start = time.process_time()
    if not db_helper_session.verify_api_key(apikey):
        logger.info(f"Wrong Api Key Received")
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Wrong API Key"
        )
    body = await file.body()
    body = str(body, 'utf-8')

    obj = parse_xml(body)

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

    # check if 3PL is making a duplicate call
    duplicate_call, response = db_helper_session.check_duplicate_api_call(lead_hash,
                                                                          obj['adf']['prospect']['provider']['service'])
    if duplicate_call:
        logger.info("Duplicate Api Call")
        return {
            "status": f"Already {response}",
            "message": "Duplicate Api Call"
        }

    # check if adf xml is valid
    validation_check, validation_code, validation_message = check_validation(obj)

    logger.info(f"validation message: {validation_message}")

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

    # check if the lead is duplicated
    if db_helper_session.check_duplicate_lead(email, phone, last_name, make,
                                              model):
        return {
            "status": "REJECTED",
            "code": "12_DUPLICATE",
            "message": "This is a duplicate lead"
        }

    # enrich the lead
    model_input = get_enriched_lead_json(obj, db_helper_session)
    logger.info(model_input)

    # convert the enriched lead to ML input format
    ml_input = conversion_to_ml_input(model_input, make, dealer_available)
    logger.info(ml_input)

    # score the lead
    result = score_ml_input(ml_input, make, dealer_available)
    logger.info(f"ml score: {result}")

    # create the response
    response_body = {}
    if check_threshold(result, make, dealer_available):
        response_body["status"] = "ACCEPTED"
        response_body["code"] = "0_ACCEPTED"
    else:
        response_body["status"] = "REJECTED"
        response_body["code"] = "16_LOW_SCORE"

    # create and dump data for quicksight analysis
    item, path = create_quicksight_data(obj['adf']['prospect'], lead_hash, response_body['status'],
                                        response_body['code'])
    s3_helper_client.put_file(item=item, path=path)

    # store the lead response in ddb
    db_helper_session.insert_lead(lead_hash, obj['adf']['prospect']['provider']['service'], response_body['status'])

    # verify the customer
    if response_body['status'] == 'ACCEPTED':
        contact_verified = await verify_phone_and_email(email, phone)
        if not contact_verified:
            response_body['status'] = 'REJECTED'
            response_body['code'] = '17_FAILED_CONTACT_VALIDATION'

    # insert the lead into ddb with oem details
    if response_body['status'] == 'ACCEPTED':
        lead_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, email + phone + last_name+make+model))
        db_helper_session.insert_oem_lead(uuid=lead_uuid,
                                          make=make,
                                          model=model,
                                          date=datetime.today().strftime('%Y-%m-%d'),
                                          email=email,
                                          phone=phone,
                                          last_name=last_name,
                                          timestamp=datetime.today().strftime('%Y-%m-%d-%H:%M:%S'),
                                          make_model_filter_status=db_helper_session.get_make_model_filter_status(make),
                                          lead_hash=lead_hash,
                                          dealer=obj['adf']['prospect']['vendor'].get('vendorname', 'unknown'),
                                          provider=obj['adf']['prospect']['provider']['service'],
                                          postalcode=obj['adf']['prospect']['customer']['contact']['address']['postalcode']
                                          )
        db_helper_session.insert_customer_lead(uuid=lead_uuid,
                                               email=email,
                                               phone=phone,
                                               last_name=last_name,
                                               make=make,
                                               model=model)
    time_taken = (time.process_time() - start) * 1000

    response_body["message"] = f" {result} Response Time : {time_taken} ms"
    logger.info(
        f"Lead {response_body['status']} with code: {response_body['code']} and message: {response_body['message']}")
    return response_body


