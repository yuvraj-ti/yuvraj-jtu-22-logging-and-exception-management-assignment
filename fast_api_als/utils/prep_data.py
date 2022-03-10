from .ml_init_data import initial_ml_input, columns_list
from .ml_init_data import initial_ml_input_no_dealer, columns_list_no_dealer


def conversion_to_ml_input(data):
    ml_input = []
    ml_data_json = initial_ml_input
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


def conversion_to_ml_input_no_dealer(data):
    ml_input = []
    ml_data_json = initial_ml_input_no_dealer
    for key in data:
        if key in columns_list_no_dealer:
            ml_data_json[key] = float(data[key])
        else:
            new_key = f"{key}_{data[key]}"
            if new_key in ml_data_json:
                ml_data_json[new_key] = 1

    for key in ml_data_json:
        ml_input.append(ml_data_json[key])
    return ml_input
