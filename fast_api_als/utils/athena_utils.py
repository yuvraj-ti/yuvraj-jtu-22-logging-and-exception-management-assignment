import logging
import json
import time
import botocore

from fast_api_als import constants
from fast_api_als.utils.boto3_utils import get_boto3_session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


class AthenaHelper:
    def __init__(self, athena_client):
        self.ATHENA_BUCKET = constants.ATHENA_QUERY_BUCKET
        self.ATHENA_DATABASE = constants.ATHENA_DATABASE_NAME
        self.athena_client = athena_client

    def create_query(self, oem, epoch_timestamp):
        query = f"""SELECT * FROM auto_lead_scoring_test as B
                        WHERE epoch_timestamp >= {epoch_timestamp} and oem={oem} and status = 'ACCEPTED' and lead_hash in
                        (
                            SELECT lead_hash FROM auto_lead_scoring_test as A
                            where A.oem_responded = 1
                        )
                    """
        return query

    def query_athena(self, query):
        logger.info(f'Running athena query: {query}')
        res = self.athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': self.ATHENA_DATABASE
            },
            ResultConfiguration={
                'OutputLocation': self.ATHENA_BUCKET,
            }
        )
        execution_id = res['QueryExecutionId']
        logger.info(f'waiting for execution of query {execution_id}')
        verify_response(res, query)
        return execution_id


def verify_response(response, data):
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if not status_code == 200:
        logger.error(f"Failed to add {data} to the database.")
    else:
        logger.info(f"New entry {data} added successfully.")


session = get_boto3_session()
client = session.client('athena', config=botocore.client.Config(max_pool_connections=99))
athena_helper_client = AthenaHelper(client)
