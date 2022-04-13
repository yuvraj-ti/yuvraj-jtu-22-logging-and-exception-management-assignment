from fast_api_als.constants import ALS_USER_POOL_ID

from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from fast_api_als.constants import ALS_AWS_ACCESS_KEY, ALS_AWS_REGION, ALS_AWS_SECRET_KEY, ALS_USER_POOL_ID


def get_user_role(token: str, cognito_client):
    """
        Finds the role from the token.
        Args:
            token: The token to find the role from.
            cognito_client: The cognito client to use.
        Returns:
            The role of the user.
    """
    # use cognito api to find user role and name using token

    try:
        response = cognito_client.get_user(
            AccessToken=token
        )
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
        )
    user_attribute = {}
    for attr in response['UserAttributes']:
        user_attribute[attr['Name']] = attr['Value']
    return user_attribute.get('custom:name', ''), user_attribute.get('custom:role', '')


def register_new_user(email: str, name: str, role: str, cognito_client):
    """
        Registers a new user.
    Args:
        email: The email of the user.
        name: The name of the user.
        role:  The role of the user.
        cognito_client: The cognito client to use.

    Returns:
        The success or reject response.
    """
    res = cognito_client.admin_create_user(
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
    if res['ResponseMetadata']['HTTPStatusCode'] == 200:
        return "SUCCESS"
    else:
        return "REJECT"


def fetch_all_users(cognito_client):
    """
        Fetches all the users.
    Args:
        cognito_client: The cognito client to use.

    Returns:
        The users.
    """
    res = cognito_client.list_users(
        UserPoolId=ALS_USER_POOL_ID
    )
    users = []
    for user in res['Users']:
        user_attribute = {}
        for attr in user['Attributes']:
            user_attribute[attr['Name']] = attr['Value']
        users.append(user_attribute)
    return users


def fetch_all_users_by_role(role, cognito_client):
    """
        Fetches all the users by role.
    Args:
        role: The role of the user.
        cognito_client: The cognito client to use.

    Returns:
        The users.
    """
    res = cognito_client.list_users(
        UserPoolId=ALS_USER_POOL_ID,
        Filter="custom:role = {}".format(role)
    )
    users = []
    for user in res['Users']:
        user_attribute = {}
        for attr in user['Attributes']:
            user_attribute[attr['Name']] = attr['Value']
        users.append(user_attribute)
    return users


def delete_user(username, cognito_client):
    """
        Deletes a user.
    Args:
        username: The username of the user.
        cognito_client: The cognito client to use.

    Returns:
        The success or reject response.
    """
    res = cognito_client.admin_delete_user(
        UserPoolId=ALS_USER_POOL_ID,
        Username=username
    )
    if res['ResponseMetadata']['HTTPStatusCode'] == 200:
        return "SUCCESS"
    else:
        return "REJECT"
