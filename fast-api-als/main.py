import json
import boto3
import sagemaker
import pandas as pd
import io
import os
import time
import logging
import pgeocode
from dateutil import parser
import calendar

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

def get_dealer_postal_code(dealer_code):
    # TODO: Implement this function
    return "85251"

def get_distance_to_vendor(dealer_code, customer_postal_code):
    dealer_postal_code = get_dealer_postal_code(dealer_code)
    dist = pgeocode.GeoDistance('US')
    # distance in km
    return dist.query_postal_code(dealer_postal_code, customer_postal_code)

def get_ml_input_json(input):
    """
    TODO: Determine FirstLastPropCase, lead_TimeFrameCont, EmailDomainCat, Vehicle_FinanceMethod, BroadColour,
    """
    request_datetime = parser.parse(input['adf']['prospect']['requestdate'])
    return {
        "DistanctToVendor": get_distance_to_vendor(input['adf']['prospect']['vendor']['id']['#text'],
                                                   input['adf']['prospect']['customer']['contact']['address']['postalcode']),
        "FirstLastPropCase": 0,
        "NameEmailCheck": 1,
        "SingleHour": request_datetime.hour,
        "SingleWeekday": calendar.day_name[request_datetime.weekday()],
        "Transmission": input['adf']['prospect']['vehicle']['transmission'],
        "Model": input['adf']['prospect']['vehicle']['model'],
        "lead_TimeFrameCont": "Codenation",
        "EmailDomainCat": "high",
        "BroadColour": input['adf']['prospect']['vehicle']['colorcombination']['exteriorcolor'],
        "PriceStart": input['adf']['prospect']['vehicle']['price'][0]['#text']
    }
"""
DistanctToVendor                      0.424685
FirstLastPropCase                            0
NameEmailCheck                               1
SingleHour                                   3
SingleWeekday                         saturday
lead_TimeFrameCont                  Codenation
EmailDomainCat                            high
Vehicle_FinanceMethod                  unknown
BroadColour                         Codenation
ColoursNotChosen                             0
Gender                                       m
Income                                   83687
ZipPopulationDensity                   4556.36
ZipPopulationDensity_AverageUsed             0
CountryOfOrigin                          asian
AddressProvided                              1
TelephonePreference                 Codenation
AddressContainsNumericAndText                1
Segment_Description                 midsizecar
PriceStart                               20895
Cylinders                              unknown
Hybrid                                       0
Transmission                           unknown
Displacement                           under3l
lead_ProviderService                Codenation
LeadConverted                                0
Period                                  201702
Model                               Codenation
Lead_Source                         Codenation
Rating                                     4.6
LifeTimeReviews                             79
Recommended                                 93
SCR                                    5.34849
OCR                                    8.91899
"""


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

    model_input = get_ml_input_json(obj)

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
