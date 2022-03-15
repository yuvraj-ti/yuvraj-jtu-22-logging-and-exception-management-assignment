import pgeocode
dist = pgeocode.GeoDistance('US')


def get_dealer_postal_code(dealer_code):
    # TODO: Implement this function
    return "85251"


def is_nan(x):
    return x != x


def get_distance_to_vendor(dealer_code, customer_postal_code):
    dealer_postal_code = get_dealer_postal_code(dealer_code)
    # distance in km
    val = dist.query_postal_code(dealer_postal_code, customer_postal_code)
    if is_nan(val):
        return 5000  # if nan then set to max default
    return val
