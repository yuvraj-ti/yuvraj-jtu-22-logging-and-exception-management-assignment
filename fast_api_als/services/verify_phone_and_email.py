import time

import requests
import logging
from fast_api_als.constants import (
    ALS_DATA_TOOL_EMAIL_VERIFY_METHOD,
    ALS_DATA_TOOL_PHONE_VERIFY_METHOD,
    ALS_DATA_TOOL_SERVICE_URL,
    ALS_DATA_TOOL_REQUEST_KEY)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


async def call_service(url):
    r = requests.get(url)
    if r.status_code >= 300:
        return {}
    return r.json()


async def verify_phone_and_email(email, phone_number):
    start = time.process_time()
    logger.info(f"Phone :{phone_number} and Email: {email} Validation started at: {start} ")
    email_valid = False
    phone_valid = False
    if email != '':
        email_validation_url = '{}?Method={}&RequestKey={}&EmailAddress={}&OutputFormat=json'.format(
            ALS_DATA_TOOL_SERVICE_URL,
            ALS_DATA_TOOL_EMAIL_VERIFY_METHOD,
            ALS_DATA_TOOL_REQUEST_KEY,
            email)
        r = await call_service(email_validation_url)
        if r["DtResponse"]["Result"][0]["StatusCode"] in ("0", "1"):
            email_valid = True
    if phone_number != '':
        phone_validation_url = '{}?Method={}&RequestKey={}&PhoneNumber={}&OutputFormat=json'.format(
            ALS_DATA_TOOL_SERVICE_URL,
            ALS_DATA_TOOL_PHONE_VERIFY_METHOD,
            ALS_DATA_TOOL_REQUEST_KEY,
            phone_number)
        r = await call_service(phone_validation_url)
        if r["DtResponse"]["Result"][0]["IsValid"] == "True":
            phone_valid = True
    logger.info(
        f"isPhoneVerified :{phone_valid} and idEmailValid: {email_valid} finished at: {(time.process_time() - start) * 1000} ms ")
    return email_valid | phone_valid
