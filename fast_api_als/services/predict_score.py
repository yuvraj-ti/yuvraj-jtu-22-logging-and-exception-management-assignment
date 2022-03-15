import pandas as pd
import io
from fast_api_als.utils.aws_sagemaker import get_sagemaker_client, runtime

sagemaker_client = get_sagemaker_client()
csv_file = io.StringIO()


def get_prediction(ml_input, predictor):
    result = predictor.predict(ml_input, initial_args={'ContentType': 'text/csv'})
    return result


def ml_predict_score(ml_input, endpoint_name):
    # by default sagemaker expects comma separated
    ml_input = [ml_input]
    df = pd.DataFrame(ml_input)
    df.to_csv(csv_file, sep=",", header=False, index=False)
    my_payload_as_csv = csv_file.getvalue()
    # print(my_payload_as_csv)
    response = runtime.invoke_endpoint(EndpointName=endpoint_name,
                                       ContentType='text/csv',
                                       Body=my_payload_as_csv)
    return float(response['Body'].read().decode().split(',')[0])
