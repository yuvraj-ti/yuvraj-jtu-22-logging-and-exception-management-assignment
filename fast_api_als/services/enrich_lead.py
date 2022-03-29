import calendar
from dateutil import parser

from fast_api_als.services.enrich.car_model_data import get_broad_color, get_color_not_chosen_value, get_cylinder, \
    get_transmission, get_price_start
from fast_api_als.services.enrich.customer_info import get_country_of_origin, check_telephone_preference, \
    check_alpha_and_numeric_address
from fast_api_als.services.enrich.dealer_data import get_distance_to_vendor
from fast_api_als.services.enrich.demographic_data import find_demographic_data
from fast_api_als.services.enrich.find_gender import find_gender


def get_enriched_lead_json(adf_json: dict, db_helper_session) -> dict:
    dealer_data = db_helper_session.get_dealer_data(
        adf_json['adf']['prospect'].get('vendor', {}).get('id', {}).get('#text', None),
        adf_json['adf']['prospect']['vehicle']['make'])

    distance_to_vendor = get_distance_to_vendor(dealer_data.get('postalcode', None),
        adf_json['adf']['prospect']['customer']['contact']['address']['postalcode'])

    gender_classification = find_gender(adf_json['adf']['prospect']['customer']['contact']['name'])
    gender_cat = "unknown"
    if gender_classification in ("m","?m"):
        gender_cat = "male"
    elif gender_classification in ("f","?f"):
        gender_cat = "female"
    request_datetime = parser.parse(adf_json['adf']['prospect']['requestdate'])
    broad_color = get_broad_color(
        adf_json['adf']['prospect']['vehicle'].get('colorcombination', {}).get('exteriorcolor', None))
    color_not_chosen = get_color_not_chosen_value(
        adf_json['adf']['prospect']['vehicle'].get('colorcombination', {}).get('interiorcolor', None),
        adf_json['adf']['prospect']['vehicle'].get('colorcombination', {}).get('exteriorcolor', None))
    country_of_origin = get_country_of_origin(
        adf_json['adf']['prospect']['customer']['contact']['address'].get('country', None))
    telephone_preference = check_telephone_preference(
        adf_json['adf']['prospect']['customer']['contact'].get('phone', {}).get('@time', ''))
    street_address = adf_json['adf']['prospect']['customer']['contact']['address'].get('street', {}).get('#text', None)
    address_check = check_alpha_and_numeric_address(street_address)
    trim = adf_json['adf']['prospect']['vehicle'].get('trim', '')
    cylinders = get_cylinder(trim)
    transmission = get_transmission(trim)
    price_start = get_price_start(adf_json['adf']['prospect']['vehicle'].get('price', []))
    income, population_density = find_demographic_data(adf_json['adf']['prospect']['customer']['contact']['address'][
                                                           'postalcode'])
    first_last_prop_case = 0
    name_email_check = 1
    return {
        "DistanctToVendor": distance_to_vendor,
        "FirstLastPropCase": first_last_prop_case,
        "NameEmailCheck": name_email_check,
        "SingleHour": request_datetime.hour,
        "SingleWeekday": calendar.day_name[request_datetime.weekday()],
        "lead_TimeFrameCont": adf_json['adf']['prospect']['customer'].get('timeframe', {}).get('description',
                                                                                               'unknown'),
        "EmailDomainCat": "normal",
        "Vehicle_FinanceMethod": adf_json['adf']['prospect']['vehicle'].get("finance", {}).get("method", "unknown"),
        "BroadColour": broad_color,
        "ColoursNotChosen": color_not_chosen,
        "Gender": gender_classification,
        "Income": income,
        "ZipPopulationDensity": population_density,
        "ZipPopulationDensity_AverageUsed": "0",
        "CountryOfOrigin": country_of_origin,
        "AddressProvided": 1 if street_address else 0,
        "TelephonePreference": telephone_preference,
        "AddressContainsNumericAndText": address_check,
        "Segment_Description": "unknown",
        "PriceStart": price_start,
        "Cylinders": cylinders,
        "Hybrid": 1 if 'Hybrid' in trim else 0,
        "Transmission": transmission,
        "Displacement": "under3l",
        "lead_ProviderService": adf_json['adf']['prospect'].get('provider', {}).get('service',
                                                                                    'autobytel  - trilogy smartleads'),
        'LeadConverted': 0,
        'Period': str(request_datetime.year) + '-' + str(request_datetime.month),
        "Model": adf_json['adf']['prospect']['vehicle']['model'],
        "Lead_Source": "hyundaiusa",
        "Rating": dealer_data.get('rating',"4.678555302965422"),
        "LifeTimeReviews":  dealer_data.get('reviews', "228.7548938307518"),
        "Recommended": dealer_data.get('recommended', "95.71456599706488"),
        "SCR": "5.348490632243166",
        "OCR": "8.918993057558286",
        "SCR_cat": "normal",  # BMW additional enrichment
        "OCR_cat": "normal",
        "Gender_cat": gender_cat,
        "NamenMail_Proper": first_last_prop_case and name_email_check,
        "Color_Selected": 0 if (broad_color is "unknown" and color_not_chosen == 0) else 1,
        "ProperAddress": 1 if (address_check == 1 and street_address) else 0,
        "EmailDomainCat_Ratio": "0.04438530340664647",
        "lead_ProviderService_Ratio": "0.044290802250891076",
    }
