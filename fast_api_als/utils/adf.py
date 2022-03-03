import xmltodict, json
from jsonschema import Draft7Validator, validate, draft7_format_checker
import logging
from .adf_schema import schema

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


def parse_xml(adf_xml):
    try:
        obj = xmltodict.parse(adf_xml)
        return obj
    except Exception as e:
        logger.info(f"error in parsing input xml: {e}")
        return None


def check_validation(input_json):
    try:
        validate(
            instance=input_json,
            schema=schema,
            format_checker=draft7_format_checker,
        )
        logger.info(f"input is validated")
        return True, "input validated"
    except Exception as e:
        logger.error(f"Validation failed: {e.message}")
        return False, e.message