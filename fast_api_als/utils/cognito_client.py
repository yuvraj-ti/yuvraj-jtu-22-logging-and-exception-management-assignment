
import boto3
from fastapi import HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from fast_api_als.constants import ALS_AWS_ACCESS_KEY, ALS_AWS_REGION, ALS_AWS_SECRET_KEY, ALS_USER_POOL_ID

client = boto3.client(
    'cognito-idp',
    aws_access_key_id=ALS_AWS_ACCESS_KEY,
    aws_secret_access_key=ALS_AWS_SECRET_KEY,
    region_name=ALS_AWS_REGION
)


def get_user_role(token: str):
    # use cognito api to find user role and name using token
    try:
        response = client.get_user(
            AccessToken=token
        )
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )
    user_attribute = {}
    for attr in response['UserAttributes']:
        user_attribute[attr['Name']] = attr['Value']
    return user_attribute.get('custom:name', ''), user_attribute.get('custom:role', '')


def register_new_user(email: str, name: str, role: str):
    client.admin_create_user(
        UserPoolId=ALS_USER_POOL_ID,
        Username=email,
        UserAttributes=[
            {
                'Name': 'custom:name',
                'Value': name
            },
            {
                'Name': 'custom:role',
                'Value': role
            },
        ]
    )
    return "SUCCESS"
