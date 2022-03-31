import json
from fastapi import APIRouter
import logging

from fastapi import Request
from starlette import status

from fast_api_als.database.db_helper import db_helper_session

router = APIRouter()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)

# TODO: Handle OEM Authentication
@router.post("/conversion/")
async def submit(file: Request,):
    body = await file.body()
    body = json.loads( str(body, 'utf-8'))


    lead_uuid = body['lead_uuid']
    converted = body['converted']

    #TODO: Find OEM using Authentication
    oem = "Hyundai"

    res = db_helper_session.update_lead_conversion(lead_uuid, oem, converted)
    if res:
        return {
            "status_code": status.HTTP_200_OK,
            "message": "Lead Conversion Status Update"
        }
    else:
        return {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "message": "Wrong UUID, Lead Doesn't exist"
        }