from uszipcode import SearchEngine

zipcode_search = SearchEngine()


def find_demographic_data(zipcode):
    z = zipcode_search.by_zipcode(zipcode).to_dict()
    return z.get('median_household_income', 55319.39), z.get('population_density', 3585.81)


def get_customer_coordinate(zipcode):
    z = zipcode_search.by_zipcode(zipcode).to_dict()
    return z.get('lat', 0), z.get('lng', 0)