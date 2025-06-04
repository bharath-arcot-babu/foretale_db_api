import boto3
import json

def invoke_lambda(function_name: str, payload: dict, region_name: str = 'us-east-1') -> dict:
    """
    Invoke a Lambda function and return the response.

    Args:
        function_name (str): The name of the Lambda function to invoke
        payload (dict): The payload to pass to the Lambda function
        region_name (str): AWS region where the Lambda function is deployed

    Returns:
        dict: The response from the Lambda function
    """

    lambda_client = boto3.client(
        'lambda', 
        region_name=region_name
        )

    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )

    return json.loads(response['Payload'].read())