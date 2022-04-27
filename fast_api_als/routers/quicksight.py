import logging

from starlette.status import HTTP_200_OK
from fastapi import Request
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from fastapi import APIRouter, HTTPException, Depends

from fast_api_als.services.authenticate import get_token
from fast_api_als.utils.cognito_client import get_user_role
from fast_api_als.utils.quicksight_utils import generate_dashboard_url
from fast_api_als import constants

router = APIRouter()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


@router.post("/dashboard", status_code=HTTP_200_OK)
async def get_quicksight_url(request: Request, token: str = Depends(get_token)):
    service_name, user_role = get_user_role(token)

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
