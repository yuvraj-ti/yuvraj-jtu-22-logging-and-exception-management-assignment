from fastapi import APIRouter

from fast_api_als.database.db_helper import db_helper_session

router = APIRouter()
import json

from fastapi import Request
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED


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
