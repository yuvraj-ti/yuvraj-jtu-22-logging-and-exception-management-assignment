import json
from fastapi import APIRouter
import logging

from fastapi import Request, HTTPException, Depends
from starlette import status
from fast_api_als.utils.athena_utils import athena_helper_client
from fast_api_als.services.authenticate import get_token
from fast_api_als.utils.boto3_utils import get_boto3_session
from fast_api_als.utils.cognito_client import get_user_role
from fast_api_als import constants

router = APIRouter()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)

session = get_boto3_session()
cognito_client = session.client('cognito-idp')


@router.post("/reinforcement/")
async def submit(cred: Request, token: str = Depends(get_token)):
    body = await cred.body()
    body = json.loads(body)
    name, role = get_user_role(token, cognito_client)
    if role != "OEM":
        return {
            "status": status.HTTP_401_UNAUTHORIZED,
            "message": "Unauthorised"
        }
    if 'oem' not in body or 'epoch_timestamp' not in body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing OEM or Epoch Timestamp"
        )
    oem, epoch_timestamp = body['oem'], body['epoch_timestamp']

    query = athena_helper_client.create_query(oem, epoch_timestamp)
    logger.info(f"Query: {query}")

    execution_id = athena_helper_client.query_athena(query)
    logger.info(f"Execution ID: {execution_id}")

    return {
        "execution_id": execution_id,
        "bucket": constants.ATHENA_QUERY_BUCKET,
        "status_code": status.HTTP_202_ACCEPTED
    }
