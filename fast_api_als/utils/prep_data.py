project_name = 'Lead-Scoring-HYU-2017'
target_variable = 'LeadConverted'

useable_columns = [  # Continuous
    'DistanctToVendor', 'Income', 'ZipPopulationDensity', 'PriceStart', 'Recommended', 'Rating',
    'LifeTimeReviews', 'SCR', 'OCR',

    # Binary
    'FirstLastPropCase', 'NameEmailCheck', 'ColoursNotChosen', 'ZipPopulationDensity_AverageUsed',
    'AddressContainsNumericAndText', 'AddressProvided', 'Hybrid',
    'LeadConverted',

    # Categorical
    'SingleHour', 'SingleWeekday', 'lead_TimeFrameCont', 'EmailDomainCat', 'Vehicle_FinanceMethod',
    'BroadColour', 'Gender', 'CountryOfOrigin', 'TelephonePreference', 'Segment_Description',
    'Cylinders', 'Transmission', 'Displacement', 'lead_ProviderService', 'Period', 'Model',
    'Lead_Source']

# wrongly processed columns + IDs + columns with missing data, single value  etc
always_omit_columns = ['UID', 'HourOfRequestBestWorst', 'WeekDayMonTues', 'Income_AverageUsed', 'S_O',
                       'DLCode', 'DMSIntegration', 'Sale_UID', 'Lead_Type', 'receivedate', 'Sold',
                       'ProviderGrade', 'Lead_Program']

omit_columns = always_omit_columns + ['Vehicle_Make']

data_experiment_name = 'even-split-model-binned'

default_categoricals_to_one_hot_encoding = True

if default_categoricals_to_one_hot_encoding:
    categorical_to_float_columns = []
    type_of_data = 'One-Hot'
else:
    categorical_to_one_hot_columns = []
    type_of_data = 'Float-Ratio'

s3_bucket = 'cn-lead-scoring-copy'
s3_prefix = 'data/HYU'

train_ratio = 75  # percentage of total_data to be taken as train + validation
validation_ratio = 17  # percentage of training_set to be taken as validation