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
import gender_guesser.detector as gender
from uszipcode import SearchEngine

from sagemaker.serializers import CSVSerializer
from sagemaker.deserializers import JSONDeserializer
from fastapi import FastAPI, Request
from boto3 import Session

from fast_api_als.utils.adf import parse_xml, check_validation
from fast_api_als.utils.prep_data import conversion_to_ml_input
from fast_api_als.utils.ml_init_data import dummy_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)

ALS_AWS_SECRET_KEY = os.getenv("ALS_AWS_SECRET_KEY")
ALS_AWS_ACCESS_KEY = os.getenv("ALS_AWS_ACCESS_KEY")
endpoint_name = os.getenv('ENDPOINT_NAME')

dist = pgeocode.GeoDistance('US')
g_guesser = gender.Detector(case_sensitive=False)
zipcode_search = SearchEngine()

app = FastAPI()

container_name = 'xgboost'
runtime = boto3.client(
    'runtime.sagemaker',
    aws_access_key_id=ALS_AWS_ACCESS_KEY,
    aws_secret_access_key=ALS_AWS_SECRET_KEY,
    region_name='us-east-1'
)


def get_sagemaker_client():
    session = Session(
        aws_access_key_id=ALS_AWS_ACCESS_KEY,
        aws_secret_access_key=ALS_AWS_SECRET_KEY,
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


def get_prediction(ml_input):
    result = predictor.predict(ml_input, initial_args={'ContentType': 'text/csv'})
    return result


def get_dealer_postal_code(dealer_code):
    # TODO: Implement this function
    return "85251"


def get_broad_color(color):
    if color in ('Silver', 'Steel', 'Platinum'):
        return 'silver'
    elif color in ('Monaco White'):
        return 'white'
    elif color in ('Green'):
        return 'green'
    return 'unknown'


def get_country_of_origin(country):
    if not country:
        return 'unknown'
    if country == 'US':
        return 'usa'
    if country in ('IN', 'IL', 'TR', 'AE'):
        return 'asian'
    return 'unknown'


def get_color_not_chosen_value(interior, exterior):
    if not interior or not exterior or interior in ('Unknown', 'NoPreference', 'Default', 'undecided', 'Invalid',
                                                    'No Preferences', 'N A', 'N/A', 'No Preference', '-1') \
            or \
            exterior in ('Unknown', 'NoPreference', 'Default', 'undecided', 'Invalid', 'No Preferences', 'N A', 'N/A',
                         'No Preference', '-1'):
        return 1
    return 0


def check_telephone_preference(preference):
    if preference == '':
        return 'unknown'
    return preference


def check_alpha_and_numeric_address(address):
    numeric = any(map(str.isdigit, address))
    alpha = False
    for c in address:
        if ('a' <= c <= 'z') or ('A' <= c <= 'Z'):
            alpha = True
    if numeric and alpha:
        return 1
    return 0


def get_cylinder(trim):
    if 'V8' in trim:
        return 'v8'
    elif 'V6' in trim:
        return 'v6'
    return 'unknown'


def get_transmission(trim):
    if 'Manual' in trim or 'man' in trim:
        return 'manual'
    elif 'Automatic' in trim or 'auto' in trim:
        return 'automatic'
    return 'unknown'


def get_price_start(price_list):
    price = '0'
    for prices in price_list:
        price = max(price, prices['#text'])
    return price


def is_nan(x):
    return x != x


def get_distance_to_vendor(dealer_code, customer_postal_code):
    dealer_postal_code = get_dealer_postal_code(dealer_code)
    # distance in km
    val = dist.query_postal_code(dealer_postal_code, customer_postal_code)
    if is_nan(val):
        return 5000  # if nan then set to max default
    return val


def find_demographic_data(zipcode):
    z = zipcode_search.by_zipcode(zipcode).to_dict()
    return z.get('median_household_income', 55319.39), z.get('population_density', 3585.81)


def find_gender(names):
    first_name = ""
    for part_name in names:
        if part_name['@part'] == 'first':
            first_name = part_name['#text']
            break
    gender = g_guesser.get_gender(first_name)
    if gender == 'male':
        return "m"
    elif gender == 'female':
        return "f"
    elif gender == 'mostly_male':
        return "?m"
    elif gender == 'mostly_female':
        return "?f"
    else:
        return "?"


def get_ml_input_json(adf_json):
    distance_to_vendor = get_distance_to_vendor(adf_json['adf']['prospect']['vendor'].get('id', {}).get('#text', None),
                                                adf_json['adf']['prospect']['customer']['contact']['address'][
                                                    'postalcode'])
    gender_classification = find_gender(adf_json['adf']['prospect']['customer']['contact']['name'])
    request_datetime = parser.parse(adf_json['adf']['prospect']['requestdate'])
    broad_color = get_broad_color(
        adf_json['adf']['prospect']['vehicle'].get('colorcombination', {}).get('exteriorcolor', None))
    color_not_chosen = get_color_not_chosen_value(
        adf_json['adf']['prospect']['vehicle'].get('colorcombination', {}).get('interiorcolor', None),
        adf_json['adf']['prospect']['vehicle'].get('colorcombination', {}).get('exteriorcolor', None))
    country_of_origin = get_country_of_origin(
        adf_json['adf']['prospect']['customer']['contact']['address'].get('country', None))
    telephone_preference = check_telephone_preference(
        adf_json['adf']['prospect']['customer']['contact'].get('phone', {}).get('@time', ''))
    street_address = adf_json['adf']['prospect']['customer']['contact']['address'].get('street', {}).get('#text', None)
    address_check = check_alpha_and_numeric_address(street_address)
    trim = adf_json['adf']['prospect']['vehicle'].get('trim', '')
    cylinders = get_cylinder(trim)
    transmission = get_transmission(trim)
    price_start = get_price_start(adf_json['adf']['prospect']['vehicle'].get('price', []))
    income, population_density = find_demographic_data(adf_json['adf']['prospect']['customer']['contact']['address'][
                                                    'postalcode'])
    return {
        "DistanctToVendor": distance_to_vendor,
        "FirstLastPropCase": 0,
        "NameEmailCheck": 1,
        "SingleHour": request_datetime.hour,
        "SingleWeekday": calendar.day_name[request_datetime.weekday()],
        "lead_TimeFrameCont": adf_json['adf']['prospect']['customer'].get('timeframe', {}).get('description',
                                                                                               'unknown'),
        "EmailDomainCat": "normal",
        "Vehicle_FinanceMethod": adf_json['adf']['prospect']['vehicle'].get("finance", {}).get("method", "unknown"),
        "BroadColour": broad_color,
        "ColoursNotChosen": color_not_chosen,
        "Gender": gender_classification,
        "Income": income,
        "ZipPopulationDensity": population_density,
        "ZipPopulationDensity_AverageUsed": "0",
        "CountryOfOrigin": country_of_origin,
        "AddressProvided": 1 if street_address else 0,
        "TelephonePreference": telephone_preference,
        "AddressContainsNumericAndText": address_check,
        "Segment_Description": "unknown",
        "PriceStart": price_start,
        "Cylinders": cylinders,
        "Hybrid": 1 if 'Hybrid' in trim else 0,
        "Transmission": transmission,
        "Displacement": "under3l",
        "lead_ProviderService": adf_json['adf']['prospect'].get('provider', {}).get('service',
                                                                                    'autobytel  - trilogy smartleads'),
        'LeadConverted': 0,
        'Period': str(request_datetime.year) + '-' + str(request_datetime.month),
        "Model": adf_json['adf']['prospect']['vehicle']['model'],
        "Lead_Source": "hyundaiusa",
        "Rating": "4.678555302965422",
        "LifeTimeReviews": "228.7548938307518",
        "Recommended": "95.71456599706488",
        "SCR": "5.348490632243166",
        "OCR": "8.918993057558286"
    }


@app.get("/ping")
def read_root():
    start = time.process_time()
    time_taken = (time.process_time() - start) * 1000
    return {f"Pong with response time {time_taken} ms"}


@app.post("/submit/")
async def submit(file: Request):
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

    validation_check, validation_code, validation_message = check_validation(obj)

    logger.info(f"validation message: {validation_message}")

    if not validation_check:
        return {
            "status": "REJECTED",
            "code": validation_code,
            "message": validation_message
        }

    model_input = get_ml_input_json(obj)
    logger.info(model_input)
    ml_input = conversion_to_ml_input(model_input)
    logger.info(ml_input)
    result = get_prediction(ml_input)
    time_taken = (time.process_time() - start) * 1000
    response_body = {}
    if result > 0.083:
        response_body["status"] = "ACCEPTED"
        response_body["code"] = "0_ACCEPTED"
    else:
        response_body["status"] = "REJECTED"
        response_body["code"] = "16_LOW_SCORE"
    response_body["message"] = f" {result} Response Time : {time_taken} ms"
    return response_body


@app.post("/parse/")
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
    logger.info(model_input)
    return model_input


@app.post("/predict/")
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
    response_body = {}
    if result > 0.033:
        response_body["status"] = "ACCEPTED"
        response_body["code"] = "0_ACCEPTED"
    else:
        response_body["status"] = "REJECTED"
        response_body["code"] = "16_LOW_SCORE"
    response_body["message"] = f" Response Time : {time_taken} ms"
    return response_body
