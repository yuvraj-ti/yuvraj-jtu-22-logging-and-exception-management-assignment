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


async def verify_email(email: str, data: dict) -> None:
    if email == '':
        return
    is_valid = validate_email(
        email_address=email,
        check_format=True,
        check_blacklist=True,
        check_dns=False,
        dns_timeout=1,
        check_smtp=False,
        smtp_timeout=10,
        smtp_debug=True
    )
    data["email"] = is_valid


async def verify_phone(phone: str, data: dict) -> None:
    if phone == '':
        return
    x = phonenumbers.parse(phone, "US")
    data["phone"] = phonenumbers.is_valid_number(x)


async def alternate_verify_phone_and_email(email: str, phone_number: str) -> bool:
    start = time.process_time()
    logger.info(f"Phone :{phone_number} and Email: {email} Validation started at: {start} ")
    data = {}
    email_valid = False
    phone_valid = False
    await asyncio.gather(
        verify_phone(phone_number, data),
        verify_email(email, data),
    )
    if "email" in data:
        email_valid = data["email"]
    if "phone" in data:
        phone_valid = data["phone"]
    logger.info(
        f"isPhoneVerified :{phone_valid} and idEmailValid: {email_valid} finished at: {(time.process_time() - start) * 1000} ms ")
    return email_valid | phone_valid
