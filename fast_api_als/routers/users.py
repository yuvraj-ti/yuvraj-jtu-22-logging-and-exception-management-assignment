import json
import logging

from fastapi import Request
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK, HTTP_401_UNAUTHORIZED

from fastapi import APIRouter, HTTPException, Depends
from fast_api_als.constants import DEFAULT_OEM_LIMIT
from fast_api_als.database.db_helper import db_helper_session
from fast_api_als.services.authenticate import get_token
from fast_api_als.utils.cognito_client import get_user_role, register_new_user, fetch_all_users, \
    fetch_all_users_by_role, congito_delete_user


router = APIRouter()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


@router.post("/get_user_role")
async def get_user_info(cred: Request, token: str = Depends(get_token)) -> object:
    body = await cred.body()
    body = json.loads(body)
    name, role = get_user_role(token)
    return {
        "name": name,
        "role": role
    }


@router.post("/register_user")
async def register_user(cred: Request, token: str = Depends(get_token)):
    body = await cred.body()
    body = json.loads(body)
    name, user_role = get_user_role(token)
    if user_role != "ADMIN":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Unauthorised")

    if 'email' not in body or 'role' not in body or 'name' not in body:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Missing email, role or name"
        )

    email, role, name = body['email'], body['role'], body['name']
    if role not in ("OEM", "3PL", "ADMIN"):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST
        )
    try:
        response = register_new_user(email, name, role)
        if response != "SUCCESS":
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=f"Not Authorized")
        if role == "3PL":
            db_helper_session.register_3PL(name)
        if role == 'OEM':
            db_helper_session.create_new_oem(name, "False", DEFAULT_OEM_LIMIT)
        return "SUCCESS"
    except Exception as e:
        logger.info(e)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get the performance dashboard")


@router.post("/view_users")
async def view_all_users(token: str = Depends(get_token)):
    name, role = get_user_role(token)
    logger.info(f"User list requested by {name}, {role}")
    if role != "ADMIN":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Not Authorized")
    users = fetch_all_users()
    return {
        "status_code": HTTP_200_OK,
        "message": users
    }


@router.post("/view_users_by_role")
async def view_all_users_by_role(request: Request, token: str = Depends(get_token)):
    body = await request.body()
    body = json.loads(body)
    if 'role' not in body:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Missing role"
        )
    user_role = body['role']
    name, role = get_user_role(token)
    logger.info(f"User list for {user_role} requested by {name}, {role}")
    if role != "ADMIN":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Not Authorized")
    users = fetch_all_users_by_role(user_role)
    return {
        "status_code": HTTP_200_OK,
        "message": users
    }


@router.post("/delete_user")
async def delete_user(request: Request, token: str = Depends(get_token)):
    body = await request.body()
    body = json.loads(body)
    name, role = get_user_role(token)
    if role != "ADMIN":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Not Authorized")
    if 'username' not in body:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Missing username"
        )
    logger.info(f"Delete user request: {body['username']}")
    username = body['username']
    res, role = congito_delete_user(username)
    if res == "SUCCESS":
        if role == "3PL":
            db_helper_session.delete_3PL(username)
        elif role == "OEM":
            db_helper_session.delete_oem(username)
        logger.info(f"Delete user response: {res}")
        return {
            "status_code": HTTP_200_OK,
            "message": "User deleted successfully"
        }
    raise HTTPException(
        status_code=HTTP_400_BAD_REQUEST,
        detail=f"User deletion failed"
    )
