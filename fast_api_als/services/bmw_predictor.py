from fast_api_als.services.get_predictor import get_predictor
from fast_api_als.constants import (
    BMW_DEALER_ENDPOINT_NAME
)

bmw_dealer_predictor = get_predictor(BMW_DEALER_ENDPOINT_NAME)
