import json
import logging

from fastapi import Request
from starlette.status import HTTP_400_BAD_REQUEST

from fastapi import APIRouter, HTTPException, Depends
from fast_api_als.database.db_helper import db_helper_session
from fast_api_als.services.authenticate import get_token
from fast_api_als.utils.cognito_client import get_user_role
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED

router = APIRouter()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


@router.post("/set_oem_setting")
async def set_oem_setting(request: Request, token: str = Depends(get_token)):
    body = await request.body()
    body = json.loads(body)

    if 'oem' not in body or 'make_model' not in body:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Missing oem or make_model"
        )

    oem, make_model = body['oem'], body['make_model']
    name, role = get_user_role(token)
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
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Missing oem"
        )

    oem = body['oem']
    name, role = get_user_role(token)
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
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Missing oem or threshold"
        )
    oem, threshold = body['oem'], body['threshold']
    name, role = get_user_role(token)
    if role != "ADMIN" and (role != "OEM" or name != oem):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Not Authorized")
    res = db_helper_session.set_oem_threshold(oem, threshold)
    return {
        "status_code": HTTP_200_OK,
        "message": res
    }


@router.post("/view_oem_threshold")
async def view_oem_threshold(request: Request, token: str = Depends(get_token)):
    body = await request.body()
    body = json.loads(body)

    if 'oem' not in body:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Missing oem"
        )
    logger.info(f"Oem threshold view by: {body['oem']}")
    oem = body['oem']
    name, role = get_user_role(token)
    if role != "ADMIN" and (role != "OEM"):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Not Authorized")
    oem_data = db_helper_session.fetch_oem_data(oem)
    if oem_data == {}:
        return {
            "status_code": HTTP_200_OK,
            "message": "No data found"
        }
    return {
        "status_code": HTTP_200_OK,
        "message": oem_data['threshold']
    }
