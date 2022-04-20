from fast_api_als.services.get_predictor import get_predictor
from fast_api_als.constants import (
    GEN_DEALER_ENDPOINT_NAME
)

gen_dealer_predictor = get_predictor(GEN_DEALER_ENDPOINT_NAME)
