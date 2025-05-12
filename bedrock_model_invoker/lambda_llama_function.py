import json
import boto3
import botocore.exceptions
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")
def lambda_handler(event, context):
    try:
        # Parse request body
        body = json.loads(event.get("body", "{}"))
        # Extract required parameters, providing defaults where necessary
        prompt = body.get("prompt", "Provide no response.")
        max_gen_len = body.get("max_gen_len", 512)
        temperature = body.get("temperature", 0.5)
        top_p = body.get("top_p", 0.9)
        # Construct request payload
        payload = {
            "prompt": prompt,
            "max_gen_len": max_gen_len,
            "temperature": temperature,
            "top_p": top_p
        }
        # Call Amazon Bedrock
        response = bedrock.invoke_model(
            modelId="meta.llama3-70b-instruct-v1:0",
            body=json.dumps(payload)
        )
        # Read and parse response
        result = json.loads(response["body"].read().decode("utf-8"))
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result)
        }
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON format in request body."})
        }
    
    except botocore.exceptions.BotoCoreError as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Error communicating with Amazon Bedrock.", "details": str(e)})
        }
    
    except ValueError as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "An unexpected error occurred.", "details": str(e)})
        }
