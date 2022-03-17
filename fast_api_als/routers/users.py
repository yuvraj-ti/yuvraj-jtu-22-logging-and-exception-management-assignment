import json
import logging

from fastapi import APIRouter, HTTPException

from fast_api_als.database.db_helper import db_helper_session
from fast_api_als.utils.cognito_client import get_user_role, register_new_user
from fast_api_als.utils.quicksight_utils import generate_dashboard_url
from fast_api_als import constants
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED

from fastapi import Request
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_500_INTERNAL_SERVER_ERROR

router = APIRouter()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


@router.post("/register3PL")
async def register3pl(cred: Request):
    body = await cred.body()
    body = json.loads(body)
    username, password = body['username'], body['password']
    apikey = db_helper_session.register_3PL(username)

    # check if 3PL is already registered
    if not apikey:
        return {
            "status": HTTP_400_BAD_REQUEST,
            "message": "Already registered"
        }
    return {
        "status": HTTP_201_CREATED,
        "x-api-key": apikey,
        "message": "Include x-api-key in header"
    }


@router.post("/dashboard")
async def get_quicksight_url(request: Request):
    body = await request.body()
    body = json.loads(body)
    service_name, user_role = get_user_role(body['token'])

    dashboard_arn = constants.DASHBOARD_ARN.get(user_role)
    dashboard_id = constants.ADMIN_DASHBOARD_ID

    if user_role == '3PL':
        dashboard_id = constants.PROVIDER_DASHBOARD_ID
    elif user_role == 'OEM':
        dashboard_id = constants.OEM_DASHBOARD_ID

    dashboard_tags = [
        {
            'Key': '3PL',
            'Value': '*' if user_role != '3PL' else service_name
        },
        {
            'Key': 'OEM',
            'Value': '*' if user_role != 'OEM' else service_name
        }
    ]
    logger.info(dashboard_tags)

    try:
        dashboard_url = generate_dashboard_url(dashboard_arn, dashboard_id, dashboard_tags)
        logger.info(f'Received the dashboard url: {dashboard_url}')
        return {
            "status_code": HTTP_200_OK,
            "dashboard_url": dashboard_url
        }
    except Exception as e:
        logger.info(e)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get the performance dashboard")


@router.post("/registerUser")
async def registerUser(cred: Request):
    body = await cred.body()
    body = json.loads(body)
    email, token, role, name = body['email'], body['token'], body['role'], body['name']
    if role not in ("OEM", "3PL", "ADMIN"):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST
        )
    try:
        response = register_new_user(token, email, name, role)
        if response != "SUCCESS":
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=f"Not Authorized")
        return "SUCCESS"
    except Exception as e:
        logger.info(e)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get the performance dashboard")
