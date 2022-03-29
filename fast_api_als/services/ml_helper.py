from fast_api_als.constants import HYU_DEALER_ENDPOINT_NAME, HYU_NO_DEALER_ENDPOINT_NAME, BMW_DEALER_ENDPOINT_NAME
from fast_api_als.ml_init_data.BMW.ml_init_data import initial_ml_input_bmw_dealer, column_list_bmw_dealer
from fast_api_als.ml_init_data.HYU.ml_init_data import columns_list_hyu_dealer, columns_list_hyu_no_dealer, \
    initial_ml_input_hyu_no_dealer, initial_ml_input_hyu_dealer
from fast_api_als.services.bmw_predictor import bmw_dealer_predictor
from fast_api_als.services.hyu_predictor import hyu_dealer_predictor, hyu_no_dealer_predictor
from fast_api_als.services.predict_score import get_prediction


def load_data():
    data = {
        "hyundai": {
            "dealer": {
                "columns": columns_list_hyu_dealer,
                "initial_ml_input": initial_ml_input_hyu_dealer,
                "predictor": hyu_dealer_predictor,
                "endpoint_name": HYU_DEALER_ENDPOINT_NAME,
                "threshold": 0.083
            },
            "no-dealer": {
                "columns": columns_list_hyu_no_dealer,
                "initial_ml_input": initial_ml_input_hyu_no_dealer,
                "predictor": hyu_no_dealer_predictor,
                "endpoint_name": HYU_NO_DEALER_ENDPOINT_NAME,
                "threshold": 0.083
            }
        },
        "bmw": {
            "dealer": {
                "columns": column_list_bmw_dealer,
                "initial_ml_input": initial_ml_input_bmw_dealer,
                "predictor": bmw_dealer_predictor,
                "endpoint_name": BMW_DEALER_ENDPOINT_NAME,
                "threshold": 0.051
            }
        }
    }
    return data


ml_data = load_data()


def conversion_to_ml_input(data, make, dealer_available):
    dealer_cat = "dealer" if dealer_available else "no-dealer"
    make = make.lower()
    columns_list = ml_data[make][dealer_cat]["columns"]
    ml_data_json = ml_data[make][dealer_cat]["initial_ml_input"]
    ml_input = []
    for key in data:
        if key in columns_list:
            ml_data_json[key] = float(data[key])
        else:
            new_key = f"{key}_{data[key]}"
            if new_key in ml_data_json:
                ml_data_json[new_key] = 1

    for key in ml_data_json:
        ml_input.append(ml_data_json[key])
    return ml_input


def score_ml_input(data, make, dealer_available):
    dealer_cat = "dealer" if dealer_available else "no-dealer"
    make = make.lower()
    return get_prediction(data, ml_data[make][dealer_cat]["predictor"])


def check_threshold(result, make, dealer_available):
    dealer_cat = "dealer" if dealer_available else "no-dealer"
    make = make.lower()
    return True if result > ml_data[make][dealer_cat]["threshold"] else False
