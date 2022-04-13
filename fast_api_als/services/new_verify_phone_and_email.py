import time
import httpx
import asyncio
import logging
from fast_api_als.constants import (
 NUM_VERIFY_ACCESS_KEY, NUM_VERIFY_URL, TOWER_DATA_URL, TOWER_DATA_API_KEY
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


async def call_validation_service(url: str, topic: str, value: str, data: dict) -> None:  # 2
    t1 = int(time.time()*1000.0)
    logger.info(f"{topic} :{value} validation started at: {t1} ")
    if value == '':
        return
    async with httpx.AsyncClient() as client:  # 3
        try:
            response = await client.get(url, timeout=1)
        except Exception as e:
            logger.info(f"{topic} :{value} validation failed at: {int(time.time()*1000.0)-t1} ms due to {e}")
    try:
        data[topic] = response.json()
    except:
        data[topic] = {}
    logger.info(f"{topic} :{value} validation finished at {int(time.time()*1000.0)} and took : {int(time.time()*1000.0)-t1} ms ")


async def new_verify_phone_and_email(email: str, phone_number: str) -> bool:
    start = int(time.time()*1000.0)
    logger.info(f"Phone :{phone_number} and Email: {email} Validation started at: {start} ")
    email_validation_url = '{}?email={}&api_key={}'.format(
        TOWER_DATA_URL,
        email,
        TOWER_DATA_API_KEY)

    phone_validation_url = '{}?access_key={}&number={}&country_code=US&format=1'.format(
        NUM_VERIFY_URL,
        NUM_VERIFY_ACCESS_KEY,
        phone_number
    )
    email_valid = False
    phone_valid = False
    data = {}

    await asyncio.gather(
        call_validation_service(email_validation_url, "email", email, data),
        call_validation_service(phone_validation_url, "phone", phone_number, data),
    )
    if "email" in data:
        if data["email"].get("email_validation",{}).get("status","unknown") not in ("invalid", "risky"):
            email_valid = True
    if "phone" in data:
        if data["phone"].get("valid", False):
            phone_valid = True
    logger.info(
        f"isPhoneVerified :{phone_valid} and idEmailValid: {email_valid} finished in: {int(time.time()*1000.0)-start} ms ")
    return email_valid | phone_valid