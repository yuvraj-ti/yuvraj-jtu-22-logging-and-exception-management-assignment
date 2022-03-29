from fast_api_als import constants
from uszipcode import SearchEngine

zipcode_search = SearchEngine()


def find_demographic_data(zipcode):
    z = zipcode_search.by_zipcode(zipcode).to_dict()
    return z.get('median_household_income', constants.HOUSEHOLD_INCOME), z.get('population_density', constants.POPULATION_DENSITY)


def get_customer_coordinate(zipcode):
    z = zipcode_search.by_zipcode(zipcode).to_dict()
    return z.get('lat', 0), z.get('lng', 0)