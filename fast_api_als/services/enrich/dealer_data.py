import pgeocode
dist = pgeocode.GeoDistance('US')


def is_nan(x):
    return x != x


def get_distance_to_vendor(dealer_postal_code, customer_postal_code, ):
    # distance in km
    if not dealer_postal_code:
        return 5000
    val = dist.query_postal_code(dealer_postal_code, customer_postal_code)
    if is_nan(val):
        return 5000  # if nan then set to max default
    return val
