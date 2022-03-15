def get_contact_details(obj):
    email = obj['adf']['prospect']['customer']['contact'].get('email', '')
    phone = obj['adf']['prospect']['customer']['contact'].get('phone', {}).get('#text', '')
    last_name = ''
    for part_name in obj['adf']['prospect']['customer']['contact']['name']:
        if part_name['@part'] == 'last':
            last_name = part_name['#text']
            break
    return email, phone, last_name


def check_telephone_preference(preference):
    if preference == '':
        return 'unknown'
    return preference


def check_alpha_and_numeric_address(address):
    numeric = any(map(str.isdigit, address))
    alpha = False
    for c in address:
        if ('a' <= c <= 'z') or ('A' <= c <= 'Z'):
            alpha = True
    if numeric and alpha:
        return 1
    return 0


def get_country_of_origin(country):
    if not country:
        return 'unknown'
    if country == 'US':
        return 'usa'
    if country in ('IN', 'IL', 'TR', 'AE'):
        return 'asian'
    return 'unknown'
