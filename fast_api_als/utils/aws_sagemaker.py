import boto3
import sagemaker
import os

from sagemaker.serializers import CSVSerializer
from sagemaker.deserializers import JSONDeserializer

endpoint_name = os.getenv('ENDPOINT_NAME')
container_name = 'xgboost'
endpoint_name = "LS-HYU-2017-als-1-087-a7f1301b-2022-02-21-06-07-55-150"


def get_sagemaker_client():
    return boto3.client(
        "sagemaker",
        aws_access_key_id=os.getenv("ALS_AWS_SECRET_KEY"),
        aws_secret_access_key=os.getenv("ALS_AWS_ACCESS_KEY"),
        region_name='us-east-1'
    )


def get_predictor(sagemaker_client):
    predictor = sagemaker.predictor.Predictor(
        endpoint_name,
        sagemaker_session=sagemaker_client
    )
    predictor.serializer = CSVSerializer()
    predictor.deserializer = JSONDeserializer()
    return predictor


def get_prediction(dummy_data):
    sagemaker_client = get_sagemaker_client()
    predictor = get_predictor(sagemaker_client)
    result = predictor.predict(dummy_data, initial_args={'ContentType': 'text/csv'})
    return result
