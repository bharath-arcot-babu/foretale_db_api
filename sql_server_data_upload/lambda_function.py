import json
from layer_db_utils.services.upload_service import UploadDatabaseService

db_service = UploadDatabaseService()

def lambda_handler(event, context):
    try:
        # Handle API Gateway proxy integration
        body = json.loads(event["body"]) if isinstance(event.get("body"), str) else event.get("body", {})

        rows = body.get('data', [])
        columns = body.get('columns', [])
        target_table = body.get('target_table')
        schema = body.get('schema')

        if not rows or not columns or not target_table:
            return {
                "statusCode": 400,
                "body": json.dumps({"status": "error", "message": "Missing required parameters"}),
                "headers": {"Content-Type": "application/json"}
            }

        result = db_service.execute_upload(rows, columns, target_table, schema)

        return {
            "statusCode": 200,
            "body": json.dumps(result),
            "headers": {"Content-Type": "application/json"}
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"status": "error", "message": str(e)}),
            "headers": {"Content-Type": "application/json"}
        }
