import json
import boto3
import re
import sagemaker
import pandas as pd
import io
from io import StringIO

from sagemaker.serializers import CSVSerializer
from sagemaker.deserializers import JSONDeserializer

sagemaker_client = boto3.Session().client('sagemaker')

# runtime = boto3.client('runtime.sagemaker')

container_name = 'xgboost'
endpoint_name = "LS-HYU-2017-als-1-087-a7f1301b-2022-02-21-06-07-55-150"
predictor = sagemaker.predictor.Predictor(
    endpoint_name,
    # sagemaker_session=None,
    #     serializer=CSVSerializer,
    #     deserializer=JSONSerializer
    # accept=None
)
predictor.serializer = CSVSerializer()
predictor.deserializer = JSONDeserializer()

dummy_data = [[5.33023135e+00, 1.00000000e+00, 0.00000000e+00, 3.00000000e+00,
               0.00000000e+00, 3.60890000e+04, 4.61015488e+03, 0.00000000e+00,
               1.00000000e+00, 1.00000000e+00, 2.08950000e+04, 0.00000000e+00,
               4.60000000e+00, 4.90000000e+01, 9.70000000e+01, 5.34849063e+00,
               8.91899306e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               1.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 1.00000000e+00, 1.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               1.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               1.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 1.00000000e+00, 0.00000000e+00,
               1.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               1.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 1.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.00000000e+00,
               0.00000000e+00, 1.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 1.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 1.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
               0.00000000e+00, 1.00000000e+00]]


def lambda_handler(event, context):
    # TODO implement
    result = predictor.predict(dummy_data, initial_args={'ContentType': 'text/csv'})
    # df = pd.DataFrame(dummy_data)
    # csv_file = io.StringIO()
    # # by default sagemaker expects comma seperated
    # df_1_record.to_csv(csv_file, sep=",", header=False, index=False)
    # my_payload_as_csv = csv_file.getvalue()
    # result = runtime.invoke_endpoint(EndpointName=endpoint_name,
    #                                  ContentType='text/csv',
    #                                  Body=my_payload_as_csv)
    if container_name == 'linear-learner':
        print(result['predictions'][0]['score'])
    elif container_name == 'xgboost':
        print(result)

    return {
        'statusCode': 200,
        'body': json.dumps(f'Hello from Lambda! {result}')
    }


from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/predict/")
def read_item():
    result = predictor.predict(dummy_data, initial_args={'ContentType': 'text/csv'})
    # df = pd.DataFrame(dummy_data)
    # csv_file = io.StringIO()
    # # by default sagemaker expects comma seperated
    # df_1_record.to_csv(csv_file, sep=",", header=False, index=False)
    # my_payload_as_csv = csv_file.getvalue()
    # result = runtime.invoke_endpoint(EndpointName=endpoint_name,
    #                                  ContentType='text/csv',
    #                                  Body=my_payload_as_csv)
    if container_name == 'linear-learner':
        print(result['predictions'][0]['score'])
    elif container_name == 'xgboost':
        print(result)

    # return {
    #     'statusCode': 200,
    #     'body': json.dumps(f'Hello from Lambda! {result}')
    # }
    return {f"Done {result}"}
