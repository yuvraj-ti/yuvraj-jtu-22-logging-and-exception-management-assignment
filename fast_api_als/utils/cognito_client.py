import boto3
from fast_api_als.constants import ALS_AWS_ACCESS_KEY, ALS_AWS_REGION, ALS_AWS_SECRET_KEY

client = boto3.client(
    'cognito-idp',
    aws_access_key_id=ALS_AWS_ACCESS_KEY,
    aws_secret_access_key=ALS_AWS_SECRET_KEY,
    region_name=ALS_AWS_REGION
)


def get_user_role(token: str):
    # use cognito api to find user role and name using token
    response = client.get_user(
        AccessToken=token
    )
    return response['custom:name'], response['custom:role']
