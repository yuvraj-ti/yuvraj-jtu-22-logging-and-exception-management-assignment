import logging
import boto3
from fast_api_als.constants import ALS_AWS_REGION, ALS_AWS_ACCESS_KEY, ALS_AWS_SECRET_KEY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


def get_boto3_session():
    """
    Create boto3 session for AWS operations
    Returns:
        Returns boto3 session with given credentials
    """
    logger.info(f'Get boto3 session from credentials')
    aws_region_name = ALS_AWS_REGION
    aws_access_key_id = ALS_AWS_ACCESS_KEY
    aws_secret_access_key = ALS_AWS_SECRET_KEY

    session = boto3.Session(region_name=aws_region_name, aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key)

    return session


def get_boto3_client(service):
    """
    Create boto3 client for the provided service
    Returns:
        Returns boto3 client with given credentials
    """
    aws_region_name = ALS_AWS_REGION
    aws_access_key_id = ALS_AWS_ACCESS_KEY
    aws_secret_access_key = ALS_AWS_SECRET_KEY

    client = boto3.client(service,
                          region_name=aws_region_name,
                          aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key,
                          )

    return client
