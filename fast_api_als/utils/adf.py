import xmltodict, json
from jsonschema import Draft7Validator, validate, draft7_format_checker
import logging
from .adf_schema import schema
import pgeocode
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)

# ISO8601 datetime regex
regex = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$'
match_iso8601 = re.compile(regex).match


def validate_iso8601(requestdate):
    try:
        if match_iso8601(requestdate) is not None:
            return True
    except:
        pass
    return False


def is_nan(x):
    return x!=x


def parse_xml(adf_xml):
    try:
        obj = xmltodict.parse(adf_xml)
        return obj
    except Exception as e:
        logger.info(f"error in parsing input xml: {e}")
        return None


def validate_adf_values(input_json):
    input_json = input_json['adf']['prospect']
    zipcode = input_json['customer']['contact']['address']['postalcode']

    # zipcode validation
    pg = pgeocode.Nominatim('US')
    res = pg.query_postal_code(zipcode)
    if is_nan(res['country_code']):
        return {"status": "REJECTED", "code": "4_INVALID_ZIP", "message": "Invalid Postal Code"}

    # check for TCPA Consent
    tcpa_consent = False
    for id in input_json['id']:
        if id['@source'] == 'TCPA_Consent' and id['#text'].lower()=='yes':
            tcpa_consent = True
    if not tcpa_consent:
        logger.info("TCPA Consent found as NO")
        return {"status": "REJECTED", "code": "7_NO_CONSENT", "message": "Contact Method missing TCPA consent"}
    if not validate_iso8601(input_json['requestdate']):
        logger.info("Datetime is not in ISO8601 format")
        return {"status": "REJECTED", "code": "3_INVALID_FIELD", "message": "Invalid DateTime"}
    return {"status": "OK"}


def check_validation(input_json):
    try:
        validate(
            instance=input_json,
            schema=schema,
            format_checker=draft7_format_checker,
        )
        logger.info(f"input is validated")
        response = validate_adf_values(input_json)
        if response['status'] == "REJECTED":
            return False, response['code'], response['message']
        return True, "input validated", "validation_ok"
    except Exception as e:
        logger.error(f"Validation failed: {e.message}")
        return False, "6_MISSING_FIELD", e.message