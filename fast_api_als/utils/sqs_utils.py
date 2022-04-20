import logging
import json
import boto3
import botocore

from fast_api_als import constants
from fast_api_als.utils.boto3_utils import get_boto3_session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


class SQSHelper:
    def __init__(self, session: boto3.session.Session):
        # logger.info(f"Queue Name: {constants.SQS_QUEUE_NAME}")
        self.sqs_resource = session.resource('sqs', config=botocore.client.Config(max_pool_connections=99))
        self.sqs = self.sqs_resource.get_queue_by_name(QueueName=constants.SQS_QUEUE_NAME)
        self.send_message({"initialize": "Hello World"})

    def send_message(self, message):
        res = self.sqs.send_message(MessageBody=json.dumps(message))
        verify_response(res)


def verify_response(response):
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if not status_code == 200:
        logger.error(f"Failed to add message to queue. {response}")
    else:
        logger.info(f"New message send to sqs successfully. {status_code}")


session = get_boto3_session()
sqs_helper_session = SQSHelper(session)
