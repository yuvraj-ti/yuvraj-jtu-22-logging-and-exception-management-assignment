from fastapi import Security, HTTPException
from starlette.status import HTTP_403_FORBIDDEN
from fastapi.security.api_key import APIKeyHeader, APIKey

API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME)


async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )
