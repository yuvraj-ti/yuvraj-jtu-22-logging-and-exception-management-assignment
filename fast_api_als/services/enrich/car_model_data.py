def get_color_not_chosen_value(interior, exterior):
    if not interior or not exterior or interior in ('Unknown', 'NoPreference', 'Default', 'undecided', 'Invalid',
                                                    'No Preferences', 'N A', 'N/A', 'No Preference', '-1') \
            or \
            exterior in ('Unknown', 'NoPreference', 'Default', 'undecided', 'Invalid', 'No Preferences', 'N A', 'N/A',
                         'No Preference', '-1'):
        return 1
    return 0


def get_cylinder(trim):
    if 'V8' in trim:
        return 'v8'
    elif 'V6' in trim:
        return 'v6'
    return 'unknown'


def get_transmission(trim):
    if 'Manual' in trim or 'man' in trim:
        return 'manual'
    elif 'Automatic' in trim or 'auto' in trim:
        return 'automatic'
    return 'unknown'


def get_price_start(price_list):
    price = '0'
    for prices in price_list:
        price = max(price, prices['#text'])
    return price


def get_broad_color(color):
    if color in ('Silver', 'Steel', 'Platinum'):
        return 'silver'
    elif color in ('Monaco White'):
        return 'white'
    elif color in ('Green'):
        return 'green'
    return 'unknown'
