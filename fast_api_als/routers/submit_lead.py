import time
import uuid
from fastapi import APIRouter
import logging


from datetime import datetime

from fastapi import Request, HTTPException, Depends
from fastapi.security.api_key import APIKey
from starlette.status import HTTP_403_FORBIDDEN

from fast_api_als.constants import (
    HYU_DEALER_ENDPOINT_NAME,
    HYU_NO_DEALER_ENDPOINT_NAME
)
from fast_api_als.services.authenticate import get_api_key
from fast_api_als.services.enrich.customer_info import get_contact_details
from fast_api_als.services.enrich_lead import get_enriched_lead_json
from fast_api_als.services.predict_score import ml_predict_score
from fast_api_als.services.verify_phone_and_email import verify_phone_and_email
from fast_api_als.utils.adf import parse_xml, check_validation
from fast_api_als.utils.calculate_lead_hash import calculate_lead_hash
from fast_api_als.database.db_helper import db_helper_session
from fast_api_als.services.prep_data import conversion_to_ml_input_hyu_dealer, conversion_to_ml_input_hyu_no_dealer

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

    if not obj:
        logger.info(f"Error occured while parsing XML")
        return {
            "status": "REJECTED",
            "code": "1_INVALID_XML",
            "message": "Error occured while parsing XML"
        }
    logger.info(f"Adf file successfully parsed {obj}")
    lead_hash = calculate_lead_hash(obj)
    logger.info(f"Lead hash calculated: {lead_hash}")
    duplicate_call, response = db_helper_session.check_duplicate_api_call(lead_hash,
                                                                          obj['adf']['prospect']['provider']['service'])
    if duplicate_call:
        logger.info("Duplicate Api Call")
        return {
            "status": f"Already {response}",
            "message": "Duplicate Api Call"
        }
    validation_check, validation_code, validation_message = check_validation(obj)

    logger.info(f"validation message: {validation_message}")

    if not validation_check:
        return {
            "status": "REJECTED",
            "code": validation_code,
            "message": validation_message
        }

    email, phone, last_name = get_contact_details(obj)
    if db_helper_session.check_duplicate_lead(email, phone, last_name, obj['adf']['prospect']['vehicle']['make'],
                                              obj['adf']['prospect']['vehicle']['model']):
        return {
            "status": "REJECTED",
            "code": "12_DUPLICATE",
            "message": "This is a duplicate lead"
        }

    model_input = get_enriched_lead_json(obj)
    logger.info(model_input)
    # check if vendor is available here
    vendor_available = True if obj['adf']['prospect'].get('vendor', None) else False

    response_body = {}
    if vendor_available:
        ml_input = conversion_to_ml_input_hyu_dealer(model_input)
        logger.info(ml_input)
        result = ml_predict_score(ml_input, HYU_DEALER_ENDPOINT_NAME)
        # result = get_prediction(ml_input, hyu_dealer_predictor)
    else:
        ml_input = conversion_to_ml_input_hyu_no_dealer(model_input)
        logger.info(ml_input)
        result = ml_predict_score(ml_input, HYU_NO_DEALER_ENDPOINT_NAME)
        # result = get_prediction(ml_input, hyu_no_dealer_predictor)

    if result > 0.083:
        response_body["status"] = "ACCEPTED"
        response_body["code"] = "0_ACCEPTED"
    else:
        response_body["status"] = "REJECTED"
        response_body["code"] = "16_LOW_SCORE"

    db_helper_session.insert_lead(lead_hash, obj['adf']['prospect']['provider']['service'], response_body['status'])

    if response_body['status'] == 'ACCEPTED':
        contact_verified = await verify_phone_and_email(email, phone)
        if not contact_verified:
            response_body['status'] = 'REJECTED'
            response_body['code'] = '17_FAILED_CONTACT_VALIDATION'

    if response_body['status'] == 'ACCEPTED':
        lead_uuid = uuid.uuid5(uuid.NAMESPACE_URL, email + phone + last_name)
        db_helper_session.insert_oem_lead(uuid=lead_uuid,
                                          make=obj['adf']['prospect']['vehicle']['make'],
                                          model=obj['adf']['prospect']['vehicle']['model'],
                                          date=datetime.today().strftime('%Y-%m-%d'),
                                          email=email,
                                          phone=phone,
                                          last_name=last_name,
                                          timestamp=datetime.today().strftime('%Y-%m-%d-%H:%M:%S'),
                                          make_model_filter_status=db_helper_session.get_make_model_filter_status(
                                      obj['adf']['prospect']['vehicle']['make']),
                                          lead_hash=lead_hash
                                          )
        db_helper_session.insert_customer_lead(uuid=lead_uuid,
                                               email=email,
                                               phone=phone,
                                               last_name=last_name,
                                               oem=obj['adf']['prospect']['vehicle']['make'],
                                               model=obj['adf']['prospect']['vehicle']['model'])
    time_taken = (time.process_time() - start) * 1000
    response_body["message"] = f" {result} Response Time : {time_taken} ms"
    logger.info(f"Lead {response_body['status']} with code: {response_body['code']} and message: {response_body['message']}")
    return response_body
