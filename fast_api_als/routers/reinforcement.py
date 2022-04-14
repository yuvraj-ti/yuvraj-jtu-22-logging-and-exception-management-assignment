import time
import uuid
from fastapi import APIRouter, BackgroundTasks
import logging

from datetime import datetime

from fastapi import Request, HTTPException, Depends
from fastapi.security.api_key import APIKey
from starlette import status
from concurrent.futures import ThreadPoolExecutor, as_completed

from fast_api_als.constants import SUPPORTED_OEMS
from fast_api_als.services.authenticate import get_api_key
from fast_api_als.database.db_helper import db_helper_session
from fast_api_als.utils.athena_utils import athena_helper_client

router = APIRouter()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


@router.post("/reinforcement/")
async def submit(file: Request, apikey: APIKey = Depends(get_api_key)):
    if not db_helper_session.verify_api_key(apikey):
        logger.info(f"Wrong Api Key Received")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Wrong API Key"
        )
    body = await file.body()
    body = str(body, 'utf-8')
    if 'oem' not in body or 'epoch_timestamp' not in body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing OEM or Epoch Timestamp"
        )
    oem, epoch_timestamp = body['oem'], body['epoch_timestamp']

    query = athena_helper_client.create_query(oem, epoch_timestamp)
    logger.info(f"Query: {query}")

    execution_id = athena_helper_client.execute_query(query)
    logger.info(f"Execution ID: {execution_id}")

    return {
        "execution_id": execution_id,
        "status_code": status.HTTP_202_ACCEPTED
    }
