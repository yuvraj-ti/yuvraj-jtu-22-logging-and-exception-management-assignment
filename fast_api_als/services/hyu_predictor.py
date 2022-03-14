from fast_api_als.services.get_predictor import get_predictor
from fast_api_als.constants import (
    HYU_DEALER_ENDPOINT_NAME,
    HYU_NO_DEALER_ENDPOINT_NAME
)

hyu_dealer_predictor = get_predictor(HYU_DEALER_ENDPOINT_NAME)
hyu_no_dealer_predictor = get_predictor(HYU_NO_DEALER_ENDPOINT_NAME)
