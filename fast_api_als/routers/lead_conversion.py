import json
from fastapi import APIRouter, Depends
import logging

from fastapi import Request
from starlette import status
from starlette.exceptions import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from fast_api_als.database.db_helper import db_helper_session
from fast_api_als.services.authenticate import get_token
from fast_api_als.utils.cognito_client import get_user_role

router = APIRouter()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


# TODO: Handle OEM Authentication
@router.post("/conversion/")
async def submit(file: Request, token: str = Depends(get_token) ):
    body = await file.body()
    body = json.loads(str(body, 'utf-8'))

    lead_uuid = body['lead_uuid']
    converted = body['converted']

    oem, role = get_user_role(token)
    logger.info(f"Submit Lead conversion status: {oem}, {role} ")
    if role != "OEM":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Not Authorized")
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
