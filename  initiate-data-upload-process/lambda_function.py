import json
import boto3
import csv
import io
import gzip
from api.api_service import ApiService
from api.config import Config

# Get environment variables
API_GATEWAY_READ_URL = Config.API_GATEWAY_READ_URL
API_GATEWAY_PUT_URL = Config.API_GATEWAY_PUT_URL
API_GATEWAY_POST_URL = Config.API_GATEWAY_POST_URL
API_GATEWAY_DELETE_URL = Config.API_GATEWAY_DELETE_URL
API_GATEWAY_POST_UPLOAD_URL = Config.API_GATEWAY_POST_UPLOAD_URL
S3_BUCKET_NAME = Config.S3_BUCKET_NAME
BATCH_SIZE = Config.BATCH_SIZE

api_call = ApiService()

def get_file_upload_list(file_upload_id):
    params = {
        "procedure_name": "dbo.sproc_get_pending_file_upload_by_id",
        "isJsonOutput": "false",
        "file_upload_id":file_upload_id
    }

    return api_call.call_api_with_error_handling(
        method="GET",
        url=API_GATEWAY_READ_URL,
        params=params
    )
       
def update_file_upload(file_upload_id, upload_status, error_message, user_id, other_updates_flag):
    payload = {
        "procedure_name": "dbo.sproc_update_file_upload_status",
        "params": {
            "file_upload_id": file_upload_id,
            "upload_status": upload_status,
            "error_message": error_message,
            "last_updated_by": user_id,
            "update_row_count": other_updates_flag
        }
    }

    return api_call.call_api_with_error_handling(
        method="PUT",
        url=API_GATEWAY_PUT_URL,
        json=payload
    )
    
def delete_existing_file_upload_records(file_upload_id):
    payload = {
        "procedure_name": "dbo.sproc_delete_file_upload_records",
        "params": {
            "file_upload_id": file_upload_id
        }
    }

    return api_call.call_api_with_error_handling(
        method="DELETE",
        url=API_GATEWAY_DELETE_URL,
        json=payload
    )

def upload_data_to_sql_by_batch(rows, columns, target_table_name, target_schema):
    payload = {
        "columns": columns,
        "data": rows,
        "target_table": target_table_name,
        "schema": target_schema
    }

    return api_call.call_api_with_error_handling(
        method="POST",
        url=API_GATEWAY_POST_UPLOAD_URL,
        json=payload
    )

def stream_csv_from_s3(bucket_name, file_path, file_name, column_delimiter, text_qualifier):
    key = f"{file_path}/{file_name}"
    s3 = boto3.client('s3');

    try:
        response = s3.get_object(Bucket = bucket_name, Key = key)
        body = response['Body']
        if 'ContentEncoding' in response and response['ContentEncoding'] == 'gzip': 
            with gzip.GzipFile(fileobj=body) as gz:
                for row in csv.DictReader(io.TextIOWrapper(gz, encoding='utf-8'), delimiter=column_delimiter, quotechar=text_qualifier):
                    yield row
        else:
            for row in csv.DictReader(io.TextIOWrapper(body, encoding='utf-8'), delimiter=column_delimiter, quotechar=text_qualifier):
                yield row
    
    except Exception as e:
        raise e
    
def build_tvp_rows(column_mapping: dict, data_rows: dict, file_upload_id: int) -> list[tuple]:
    tvp_row = []
    #for all columns, get the target column
    for target_col in column_mapping:
        if(target_col == 'file_upload_id'):
            tvp_row.append(file_upload_id)
        else:
            source_col = column_mapping[target_col]
            #get the source value for the target column
            value = data_rows.get(source_col) if source_col else None
            #append the columns
            tvp_row.append(value)
    return tvp_row



def process_csv(event, context, file_upload_id, user_id):
    pending_csv_uploads = get_file_upload_list(file_upload_id)

    for file_upload in pending_csv_uploads:
        try:
            file_upload_id = file_upload['file_upload_id']
            table_name = file_upload['table_name']
            column_mapping = json.loads(file_upload['column_mapping'])
            csv_details = json.loads(file_upload['csv_details'])
            csv_column_seperator = csv_details["column_separator"]
            csv_row_seperator = csv_details["row_separator"]
            csv_text_qualifier = csv_details["text_qualifier"] or '"'
            #insert_proc_name = file_upload['insert_proc_name']           
            #csv_column_metadata = csv_details["column_metadata"]

            #delete_existing_file_upload_records(file_upload_id, user_id)
            delete_existing_file_upload_records(file_upload_id)

            # if column mapping is not completed then update the status accordingly
            if column_mapping == {} or column_mapping is None:
                update_file_upload(
                    file_upload_id,
                    "Pending",
                    "Column mapping not found.",
                    user_id,
                    "0" #other updates flag
                )
            else:
                update_file_upload(
                    file_upload_id,
                    "Uploading",
                    "Data process has been initiated.",
                    user_id,
                    "0" #other updates flag
                )
                
                # stream the file from s3
                file_name = file_upload['file_name']
                file_path = file_upload['file_path']
                physical_table_schema = file_upload['physical_table_name'].split('.', 1)[0]
                physical_table_name = file_upload['physical_table_name'].split('.', 1)[1]
                data_upload_batch = []
                target_columns = list(column_mapping.keys())

                #process batch by batch
                for row in stream_csv_from_s3(bucket_name=S3_BUCKET_NAME, file_path=file_path, file_name=file_name, column_delimiter=csv_column_seperator, text_qualifier=csv_text_qualifier):
                    tvp_rows = build_tvp_rows(column_mapping=column_mapping, data_rows = row, file_upload_id=file_upload_id)
                    data_upload_batch.append(tvp_rows)

                    if len(data_upload_batch) == BATCH_SIZE:
                        upload_data_to_sql_by_batch(rows=data_upload_batch, columns=target_columns, target_table_name=physical_table_name, target_schema=physical_table_schema)
                        data_upload_batch.clear()

                # Insert any remaining rows
                if data_upload_batch:
                    upload_data_to_sql_by_batch(rows=data_upload_batch, columns=target_columns, target_table_name=physical_table_name, target_schema=physical_table_schema)

                #update file upload status
                update_file_upload(
                    file_upload_id,
                    "Completed",
                    "Data has been successfully uploaded.",
                    user_id,
                    "1" #other updates flag
                )
        except Exception as e:
            update_file_upload(
                    file_upload_id,
                    "Pending",
                    str(e),
                    user_id,
                    "1" #other updates flag
                )
            continue

# AWS Lambda Handler
def lambda_handler(event, context):
    try:
        # Extract user_id from JSON body (assuming application/json request)
        body = event.get("body")
        
        if isinstance(body, str):
            body = json.loads(body)
        elif not isinstance(body, dict):
            body = {}

        user_id = body.get("user_id")
        file_upload_id = body.get("file_upload_id")

        if not file_upload_id:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "file_upload_id is required."
                }),
                "headers": {
                    "Content-Type": "application/json"
                }
            }

        if not user_id:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "user_id is required"
                }),
                "headers": {
                    "Content-Type": "application/json"
                }
            }

        result = process_csv(event, context, file_upload_id, user_id)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "CSV processed successfully",
                "result": result
            }),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            }),
            "headers": {
                "Content-Type": "application/json"
            }
        }

