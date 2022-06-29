import calendar
import time
import logging
from dateutil import parser
from fast_api_als.database.db_helper import db_helper_session

from fast_api_als import constants

"""
what exceptions can be thrown here?
"""


def get_enriched_lead_json(adf_json: dict) -> dict:
    pass
    if not isinstance(adf_json, dict):
        logging.error('services -> get_enriched_lead_jso : adj_json does not matches the required dict datatype')
        raise TypeError

    x={
        'key':'value'
    }
    if not isinstance(x,dict):
        logging.error('services -> get_enriched_lead_jso : x does not matches the required returned dict datatype')
        raise TypeError

    return x

