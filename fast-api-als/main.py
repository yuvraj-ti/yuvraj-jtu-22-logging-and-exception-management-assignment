import json
import boto3
import sagemaker
import pandas as pd
import io
import os
import time
import logging

from sagemaker.serializers import CSVSerializer
from sagemaker.deserializers import JSONDeserializer
from fastapi import FastAPI, Request
from boto3 import Session

from utils.adf import parse_xml, check_validation

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)

ALS_AWS_SECRET_KEY = os.getenv("ALS_AWS_SECRET_KEY")
ALS_AWS_ACCESS_KEY = os.getenv("ALS_AWS_ACCESS_KEY")

app = FastAPI()

dummy_data = [[5.33023135e+00, 1.00000000e+00, 0.00000000e+00, 3.00000000e+00,
               0.00000000e+00, 3.60890000e+04, 4.61015488e+03, 0.00000000e+00,
               1.00000000e+00, 1.00000000e+00, 2.08950000e+04, 0.00000000e+00,
               4.60000000e+00, 4.90000000e+01, 9.70000000e+01, 5.34849063e+00,
               8.91899306e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               1.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 1.00000000e+00, 1.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               1.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               1.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 1.00000000e+00, 0.00000000e+00,
               1.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               1.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 1.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.00000000e+00,
               0.00000000e+00, 1.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 1.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 1.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 1.00000000e+00]]

endpoint_name = os.getenv('ENDPOINT_NAME')
container_name = 'xgboost'
endpoint_name = "LS-HYU-2017-als-1-087-a7f1301b-2022-02-21-06-07-55-150"
runtime = boto3.client(
    'runtime.sagemaker',
    aws_access_key_id=os.getenv("ALS_AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("ALS_AWS_SECRET_KEY"),
    region_name='us-east-1'
)


def get_sagemaker_client():
    session = Session(
        aws_access_key_id=os.getenv("ALS_AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("ALS_AWS_SECRET_KEY"),
        region_name='us-east-1'
    )
    return session


def get_predictor(sagemaker_client):
    predictor = sagemaker.predictor.Predictor(
        endpoint_name,
        sagemaker_session=sagemaker.session.Session(sagemaker_client)
    )
    predictor.serializer = CSVSerializer()
    predictor.deserializer = JSONDeserializer()
    return predictor


sagemaker_client = get_sagemaker_client()
predictor = get_predictor(sagemaker_client)


def get_prediction():
    result = predictor.predict(dummy_data, initial_args={'ContentType': 'text/csv'})
    return result


def get_ml_input_json(input):
    return {

    }


@app.get("/ping")
def read_root():
    start = time.process_time()
    time_taken = (time.process_time() - start) * 1000
    return {f"Pong with response time {time_taken} ms"}


@app.post("/predict/")
async def predict(file: Request):
    start = time.process_time()
    body = await file.body()
    body = str(body, 'utf-8')

    obj = parse_xml(body)

    if not obj:
        return {
            "status": "REJECTED",
            "code": "1_INVALID_XML",
            "message": "Error occured while parsing XML"
        }

    validation_check, validation_message = check_validation(obj)

    logger.info(f"validation message: {validation_message}")

    if not validation_check:
        return {
            "status": "REJECTED",
            "code": "6_MISSING_FIELD",
            "message": validation_message
        }

    model_input = get_ml_input_json(json.dumps(obj))

    result = get_prediction()
    time_taken = (time.process_time() - start) * 1000
    if result > 0.033:
        return {f"ACCEPTED: {result} with model response Time : {time_taken} ms"}
    else:
        return {f"REJECTED: {result} with model response Time : {time_taken} ms"}


@app.get("/predict1/")
def predict1():
    csv_file = io.StringIO()
    # by default sagemaker expects comma separated
    df = pd.DataFrame(dummy_data)
    df.to_csv(csv_file, sep=",", header=False, index=False)
    my_payload_as_csv = csv_file.getvalue()
    start = time.process_time()
    response = runtime.invoke_endpoint(EndpointName=endpoint_name,
                                       ContentType='text/csv',
                                       Body=my_payload_as_csv)
    result = json.loads(response['Body'].read().decode())
    time_taken = (time.process_time() - start) * 1000
    if result > 0.033:
        return {f"ACCEPTED: {result} with model response Time : {time_taken} ms"}
    else:
        return {f"REJECTED: {result} with model response Time : {time_taken} ms"}
