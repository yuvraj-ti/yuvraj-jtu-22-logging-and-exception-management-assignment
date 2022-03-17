import time
import logging

from fast_api_als.utils.boto3_utils import get_boto3_session
from fast_api_als import constants

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


def create_quicksight_data(obj, lead_hash, status, code):
    item = {
        "lead_hash": lead_hash,
        "status": status,
        "epoch_timestamp": int(time.time()),
        "code": code,
        "make": obj.get('vehicle', {}).get('make', 'unknown'),
        "model": obj.get('vehicle', {}).get('model', 'unknown'),
        "conversion": 0,
        "postalcode": obj.get('customer', {}).get('contact', {}).get('address', {}).get('postalcode', 'unknown'),
        "email_provided": 1 if obj.get('customer', {}).get('contact', {}).get('email', None) else 0,
        "phone_provided": 1 if obj.get('customer', {}).get('contact', {}).get('phone', None) else 0,
        "3pl": obj.get('provider', {}).get('service', 'unknown'),
        "dealer": obj.get('vendor', {}).get('id', {}).get('#text', 'unknown') + "_" + obj.get('vendor', {}).get(
            'vendorname', 'unknown')
    }
    return item, f"{obj.get('vehicle', {}).get('make', 'unknown')}/{item['epoch_timestamp']}_0_{lead_hash}"


def generate_dashboard_url(dashboard_arn, dashboard_id, session_tags):
    """
    Generates the URL for a single QuickSight dashboard.
    Args:
        dashboard_arn: Quicksight dashboard ARN
        dashboard_id: Quicksight dashboard ID
    Returns:
        Quicksight URL
    """
    logger.info(f'Starting generate_dashboard_url() for the dashboard: {dashboard_arn}')

    session = get_boto3_session()
    quicksight = session.client('quicksight')
    account_id = constants.ALS_AWS_ACCOUNT

    response = quicksight.generate_embed_url_for_anonymous_user(
        AwsAccountId=account_id,
        SessionLifetimeInMinutes=constants.SESSION_LIFETIME,
        Namespace='default',
        SessionTags=session_tags,
        AuthorizedResourceArns=[
            dashboard_arn
        ],
        ExperienceConfiguration={
            'Dashboard': {
                'InitialDashboardId': dashboard_id
            }
        }
    )

    dashboard_url = response['EmbedUrl']
    logger.info(f'Generated the dashboard URL')

    return dashboard_url
