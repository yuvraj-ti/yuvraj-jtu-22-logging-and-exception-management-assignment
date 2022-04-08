from math import sin, cos, sqrt, atan2, radians

from fast_api_als.services.enrich.demographic_data import get_customer_coordinate


def is_nan(x):
    return x != x


def get_distance_to_vendor(dealer_postal_code, customer_postal_code):
    # distance in km
    if not dealer_postal_code:
        return 5000
    # approximate radius of earth in km
    R = 6373.0

    lat1, lon1 = get_customer_coordinate(dealer_postal_code)
    lat2, lon2 = get_customer_coordinate(customer_postal_code)

    if lat1 == 0 or lat2 == 0 or lon1 == 0 or lon2 == 0:
        return 5000

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance
