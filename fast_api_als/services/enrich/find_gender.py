import gender_guesser.detector as gender

g_guesser = gender.Detector(case_sensitive=False)


def find_gender(names):
    first_name = ""
    for part_name in names:
        if part_name['@part'] == 'first':
            first_name = part_name['#text']
            break
    gender = g_guesser.get_gender(first_name)
    if gender == 'male':
        return "m"
    elif gender == 'female':
        return "f"
    elif gender == 'mostly_male':
        return "?m"
    elif gender == 'mostly_female':
        return "?f"
    else:
        return "?"
