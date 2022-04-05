from fast_api_als.constants import ALS_USER_POOL_ID


def get_user_role(token: str, cognito_client):
    # use cognito api to find user role and name using token
    response = cognito_client.get_user(
        AccessToken=token
    )
    user_attribute = {}
    for attr in response['UserAttributes']:
        user_attribute[attr['Name']] = attr['Value']
    return user_attribute.get('custom:name', ''), user_attribute.get('custom:role', '')


def register_new_user(email: str, name: str, role: str, cognito_client):
    cognito_client.admin_create_user(
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
