import json
import logging

from fastapi import APIRouter, HTTPException, Depends

from fast_api_als.database.db_helper import db_helper_session
from fast_api_als.services.authenticate import get_token
from fast_api_als.utils.cognito_client import get_user_role, register_new_user, fetch_all_users, fetch_all_users_by_role
from fast_api_als.utils.quicksight_utils import generate_dashboard_url
from fast_api_als import constants
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED
from fast_api_als.utils.boto3_utils import get_boto3_session

from fastapi import Request
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_500_INTERNAL_SERVER_ERROR

router = APIRouter()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)

session = get_boto3_session()
cognito_client = session.client('cognito-idp')


@router.post("/get_user_role")
async def get_user_info(cred: Request, token: str = Depends(get_token)) -> object:
    body = await cred.body()
    body = json.loads(body)
    name, role = get_user_role(token, cognito_client)
    return {
        "name": name,
        "role": role
    }


@router.post("/register_3PL")
async def register_3pl(cred: Request, token: str = Depends(get_token)):
    body = await cred.body()
    body = json.loads(body)
    name, role = get_user_role(token, cognito_client)
    if role != "ADMIN":
        return {
            "status": HTTP_401_UNAUTHORIZED,
            "message": "Unauthorised"
        }
    if 'username' not in body or 'password' not in body:
        return {
            "status": HTTP_400_BAD_REQUEST,
            "message": "Missing username or password"
        }

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


@router.post("/dashboard", status_code=HTTP_200_OK)
async def get_quicksight_url(request: Request, token: str = Depends(get_token)):
    # body = await request.body()
    # body = json.loads(body)
    service_name, user_role = get_user_role(token, cognito_client)

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


@router.post("/register_user")
async def register_user(cred: Request, token: str = Depends(get_token)):
    body = await cred.body()
    body = json.loads(body)
    name, user_role = get_user_role(token, cognito_client)
    if user_role != "ADMIN":
        return {
            "status": HTTP_401_UNAUTHORIZED,
            "message": "Unauthorised"
        }
    if 'email' not in body or 'role' not in body or 'name' not in body:
        return {
            "status": HTTP_400_BAD_REQUEST,
            "message": "Missing email, role or name"
        }

    email, role, name = body['email'], body['role'], body['name']
    if role not in ("OEM", "3PL", "ADMIN"):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST
        )
    try:
        response = register_new_user(email, name, role, cognito_client)
        if response != "SUCCESS":
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=f"Not Authorized")
        if role == "3PL":
            db_helper_session.register_3PL(name)
        return "SUCCESS"
    except Exception as e:
        logger.info(e)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get the performance dashboard")


@router.post("/set_oem_setting")
async def set_oem_setting(request: Request, token: str = Depends(get_token)):
    body = await request.body()
    body = json.loads(body)

    if 'oem' not in body or 'make_model' not in body:
        return {
            "status": HTTP_400_BAD_REQUEST,
            "message": "Missing OEM or make_model"
        }

    oem, make_model = body['oem'], body['make_model']
    name, role = get_user_role(token, cognito_client)
    logger.info(f"Oem settings set by: {name}, {role} for {oem} ")
    if role != "ADMIN" and (role != "OEM" or name != oem):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Not Authorized")
    db_helper_session.set_make_model_oem(oem, make_model)
    return {
        "status_code": HTTP_200_OK,
        "message": "settings updated"
    }


@router.post("/view_oem_setting")
async def view_oem_setting(request: Request, token: str = Depends(get_token)):
    body = await request.body()
    body = json.loads(body)

    if 'oem' not in body:
        return {
            "status": HTTP_400_BAD_REQUEST,
            "message": "Missing oem"
        }

    oem = body['oem']
    name, role = get_user_role(token, cognito_client)
    logger.info(f"Oem settings view by: {name}, {role} for {oem} ")
    if role != "ADMIN" and (role != "OEM" or name != oem):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Not Authorized")
    make_model_status = db_helper_session.get_make_model_filter_status(oem)
    return {
        "status_code": HTTP_200_OK,
        "message": make_model_status
    }


@router.post("/set_oem_threshold")
async def set_oem_threshold(request: Request, token: str = Depends(get_token)):
    body = await request.body()
    body = json.loads(body)

    if 'oem' not in body or 'threshold' not in body:
        return {
            "status": HTTP_400_BAD_REQUEST,
            "message": "Missing oem or threshold"
        }
    oem, threshold = body['oem'], body['threshold']
    name, role = get_user_role(token, cognito_client)
    if role != "ADMIN" and (role != "OEM" or name != oem):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Not Authorized")
    db_helper_session.set_oem_threshold(oem, threshold)
    return {
        "status_code": HTTP_200_OK,
        "message": "settings updated"
    }


@router.post("/view_oem_threshold")
async def view_oem_threshold(request: Request, token: str = Depends(get_token)):
    body = await request.body()
    body = json.loads(body)

    if 'oem' not in body:
        return {
            "status": HTTP_400_BAD_REQUEST,
            "message": "Missing oem"
        }
    logger.info(f"Oem threshold view by: {body['oem']}")
    oem = body['oem']
    name, role = get_user_role(token, cognito_client)
    if role != "ADMIN" and (role != "OEM"):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Not Authorized")
    oem_data = db_helper_session.fetch_oem_data(oem)
    return {
        "status_code": HTTP_200_OK,
        "message": oem_data['threshold']
    }


@router.post("/reset_authkey")
async def reset_authkey(request: Request, token: str = Depends(get_token)):
    body = await request.body()
    body = json.loads(body)
    provider, role = get_user_role(token, cognito_client)
    logger.info(f"Reset authkey by: {provider}, {role}")
    logger.info(f"Api key reset requested by {provider}: {role}")
    if role != "ADMIN" and (role != "3PL"):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Not Authorized")
    if role == "ADMIN":
        provider = body['3pl']
    apikey = db_helper_session.set_auth_key(username=provider)
    return {
        "status_code": HTTP_200_OK,
        "x-api-key": apikey
    }


@router.post("/view_authkey")
async def view_authkey(request: Request, token: str = Depends(get_token)):
    body = await request.body()
    body = json.loads(body)
    logger.info(f"Api key view requested by {body['3pl']}: {body['role']}")
    provider, role = get_user_role(token, cognito_client)
    if role != "ADMIN" and role != "3PL":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Not Authorized")
    if role == "ADMIN":
        provider = body['3pl']
    apikey = db_helper_session.get_auth_key(username=provider)
    return {
        "status_code": HTTP_200_OK,
        "x-api-key": apikey
    }


@router.post("/view_users")
async def view_all_users(token: str = Depends(get_token)):
    name, role = get_user_role(token, cognito_client)
    logger.info(f"User list requested by {name}, {role}")
    if role != "ADMIN":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Not Authorized")
    users = fetch_all_users(cognito_client)
    return {
        "status_code": HTTP_200_OK,
        "message": users
    }


@router.post("/view_users_by_role")
async def view_all_users_by_role(request: Request, token: str = Depends(get_token)):
    body = await request.body()
    body = json.loads(body)
    if 'role' not in body:
        return {
            "status": HTTP_400_BAD_REQUEST,
            "message": "Missing role"
        }
    user_role = body['role']
    name, role = get_user_role(token, cognito_client)
    logger.info(f"User list for {user_role} requested by {name}, {role}")
    if role != "ADMIN":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Not Authorized")
    users = fetch_all_users_by_role(user_role, cognito_client)
    return {
        "status_code": HTTP_200_OK,
        "message": users
    }


@router.post("/delete_user")
async def delete_user(request: Request, token: str = Depends(get_token)):
    body = await request.body()
    body = json.loads(body)
    name, role = get_user_role(token, cognito_client)
    if role != "ADMIN":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Not Authorized")
    if 'username' not in body:
        return {
            "status": HTTP_400_BAD_REQUEST,
            "message": "Missing username"
        }
    logger.info(f"Delete user request: {body['username']}")
    username = body['username']
    res = delete_user(username, cognito_client)
    logger.info(f"Delete user response: {res}")
    return {
        "status_code": HTTP_200_OK,
        "message": res
    }
