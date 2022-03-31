import time
from fastapi import APIRouter
import logging

from starlette.status import HTTP_403_FORBIDDEN

from fast_api_als.constants import (
    HYU_DEALER_ENDPOINT_NAME, SUPPORTED_OEMS,
)
from fast_api_als.database.db_helper import db_helper_session
from fast_api_als.services.alternate_verify_phone_and_email import alternate_verify_phone_and_email
from fast_api_als.services.enrich.customer_info import get_contact_details
from fast_api_als.services.enrich_lead import get_enriched_lead_json
from fast_api_als.services.ml_helper import conversion_to_ml_input, score_ml_input, check_threshold
from fast_api_als.services.predict_score import ml_predict_score
from fast_api_als.utils.adf import parse_xml, check_validation
from fast_api_als.ml_init_data.HYU.ml_init_data import dummy_data
from fast_api_als.services.authenticate import get_api_key

from fastapi import Request, HTTPException, Depends
from fastapi.security.api_key import APIKey

router = APIRouter()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


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
