import boto3
import dynamodbgeo
import uuid
import csv, json

ddb = boto3.client('dynamodb',
                   aws_access_key_id='YOUR_ACCESS_KEY_ID',
                   aws_secret_access_key='YOUR_SECERET_ACCESS_KEY',
                   region_name='us-east-1'
                   )

config = dynamodbgeo.GeoDataManagerConfiguration(ddb, 'als-dealer-table-test')

geoDataManager = dynamodbgeo.GeoDataManager(config)

config.hashKeyLength = 5

table_util = dynamodbgeo.GeoTableUtil(config)
create_table_input = table_util.getCreateTableRequest()
table_util.create_table(create_table_input)

csvf = open('dealer_info.csv', 'r')
r = csv.DictReader(csvf)

for row in r:
    j = json.dumps(row)
    d = json.loads(j)
    if (d['dealerZip'] < '10000') and '-' not in d['dealerZip']:
        d['dealerZip'] = '0' + d['dealerZip']

    if (len(d['dealerZip']) == 5):
        PutItemInput = {
            'Item': {
                'dealerCode': {'S': d['dealerCode']},
                'dealerName': {'S': d['dealerName']},
                'dealerAddress': {'S': d['dealerAddress']},
                'dealerCity': {'S': d['dealerCity']},
                'dealerState': {'S': d['dealerState']},
                'dealerZip': {'S': d['dealerZip']},
                'dealerRadius': {'S': d['dealerRadius']},
                'latitude': {'S': d['latitude']},
                'longitude': {'S': d['longitude']},
                'Rating': {'S': d['Rating']},
                'LifeTimeReviews': {'S': d['LifeTimeReviews']},
                'Recommended': {'S': d['Recommended']},
                'oem': {'S': 'Hyundai'}
            }
        }

        geoDataManager.put_Point(dynamodbgeo.PutPointInput(
            dynamodbgeo.GeoPoint(float(d['latitude']), float(d['longitude'])),  # latitude then latitude longitude
            str(uuid.uuid5(uuid.NAMESPACE_URL, json.dumps(d))),
            # Use this to ensure uniqueness of the hash/range pairs.
            PutItemInput  # pass the dict here
        ))

