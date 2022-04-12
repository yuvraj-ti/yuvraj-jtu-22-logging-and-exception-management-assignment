import boto3
from boto3 import Session
import botocore

from fast_api_als.constants import ALS_AWS_ACCESS_KEY, ALS_AWS_SECRET_KEY

runtime = boto3.client(
    'runtime.sagemaker',
    aws_access_key_id=ALS_AWS_ACCESS_KEY,
    aws_secret_access_key=ALS_AWS_SECRET_KEY,
    region_name='us-east-1',
    config=botocore.client.Config(max_pool_connections=99)
)


def get_sagemaker_client():
    session = Session(
        aws_access_key_id=ALS_AWS_ACCESS_KEY,
        aws_secret_access_key=ALS_AWS_SECRET_KEY,
        region_name='us-east-1'
    )
    return session
