import logging
import json
from fast_api_als import constants
from fast_api_als.utils.boto3_utils import get_boto3_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


class S3Helper:
    def __init__(self, s3_client):
        self.bucket_name = constants.S3_BUCKET_NAME
        self.client = s3_client

    def put_file(self, item, path):
        res = self.client.put_object(
            Body=json.dumps(item),
            Bucket=self.bucket_name,
            Key=path
        )
        verify_response(res, path)


def verify_response(response, data):
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if not status_code == 200:
        logger.error(f"Failed to add {data} to the database.")
    else:
        logger.info(f"New entry {data} added successfully.")


client = get_boto3_client('s3')
s3_helper = S3Helper(client)