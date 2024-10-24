import boto3
import json
from botocore.exceptions import ClientError

def get_secret():
    secret_name = "service_acc_key"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session(region_name=region_name)
    print(session)
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        print(e)
        raise e

    secret = get_secret_value_response['SecretString']
    print(secret)

    # Your code goes here.

# secrets = boto3.client('secretsmanager' , region_name='us-east-1')
# credentials_json = json.loads(
#     secrets.get_secret_value(
#         SecretId='google_service_account_key'
#     )['SecretString']
# )
# print(credentials_json)
get_secret()