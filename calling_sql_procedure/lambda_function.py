import json
from database.db_service import DatabaseService

db_service = DatabaseService()

headers = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
}

def lambda_handler(event, context):
    method = event['httpMethod']
    path = event['path']

    if method == 'POST' and path == '/insert_record':
        return process_crud(event, is_commit=True)

    elif method == 'PUT' and path == '/update_record':
        return process_crud(event, is_commit=True)

    elif method == 'DELETE' and path == '/delete_record':
        return process_crud(event, is_commit=True)

    elif method == 'GET' and path == '/read_record':
        return process_read(event)

    elif method == 'GET' and path == '/read_json_record':
        return process_read(event, is_json_output=True)

    return {
        "statusCode": 404,
        "headers": headers,
        "body": json.dumps({"error": "Endpoint not found"})
    }

def process_crud(event, is_commit=False):
    try:
        body = json.loads(event.get('body') or '{}')
        procedure_name = body.get('procedure_name')
        params = body.get('params', None)

        if not procedure_name:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "procedure_name is required"})
            }

        result, status = db_service.execute_stored_procedure(procedure_name, params, isCommit=is_commit)
        status_code = int(status) if isinstance(status, int) and 100 <= status <= 599 else 200

        return {
            "statusCode": status_code,
            "headers": headers,
            "body": json.dumps(result)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)})
        }

def process_read(event, is_json_output=False):
    try:
        query = event.get('queryStringParameters') or {}
        procedure_name = query.get('procedure_name')

        if not procedure_name:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "procedure_name is required"})
            }

        params = {k: v for k, v in query.items() if k not in ['procedure_name', 'isJsonOutput']} or None
        result, status = db_service.execute_stored_procedure(procedure_name, params, isJsonOutput=is_json_output)
        status_code = int(status) if isinstance(status, int) and 100 <= status <= 599 else 200

        return {
            "statusCode": status_code,
            "headers": headers,
            "body": json.dumps(result)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)})
        }
