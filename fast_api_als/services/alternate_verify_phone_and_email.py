import time
import asyncio
import logging
from validate_email import validate_email
import phonenumbers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


async def alternate_verify_email(email: str, data: dict) -> None:
    logger.info(f"Alternate Email :{email} Validation started at: {time.process_time()} ")
    if email == '':
        return
    try:
        email_valid = validate_email(
            email_address=email,
            check_format=True,
            check_blacklist=True,
            check_dns=False,
            dns_timeout=1,
            check_smtp=False,
            smtp_timeout=1,
            smtp_debug=True
        )
        data["alternate_email"] = email_valid
        logger.info(f"Alternate Email :{email} Validation finished at: {time.process_time()} ")
    except Exception as e:
        logger.info(f"Exception: {e}")


async def alternate_verify_phone(phone: str, data: dict) -> None:
    logger.info(f"Alternate Phone :{phone} Validation started at: {time.process_time()} ")
    if phone == '':
        return
    try:
        phone_number = phonenumbers.parse(phone, "US")
        is_valid = phonenumbers.is_valid_number(phone_number)
        data["alternate_phone"] = is_valid
        logger.info(f"Alternate Phone :{phone} Validation finished at: {time.process_time()} ")
    except phonenumbers.phonenumberutil.NumberParseException as e:
        logger.info(f"Exception: {e}")


async def alternate_verify_phone_and_email(email: str, phone_number: str) -> bool:
    start = time.process_time()
    logger.info(f"Phone :{phone_number} and Email: {email} Validation started at: {start} ")
    data = {}
    email_valid = False
    phone_valid = False
    await asyncio.gather(
        alternate_verify_phone(phone_number, data),
        alternate_verify_email(email, data),
    )
    if "alternate_email" in data:
        email_valid = data["alternate_email"]
    if "alternate_phone" in data:
        phone_valid = data["alternate_phone"]
    logger.info(
        f"isPhoneVerified :{phone_valid} and idEmailValid: {email_valid} finished at: {(time.process_time() - start) * 1000} ms ")
    return email_valid | phone_valid
