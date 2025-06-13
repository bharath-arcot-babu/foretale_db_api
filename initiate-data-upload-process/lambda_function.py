import json
import boto3
import logging
from config import Config
from layer_db_utils.services.upload_service import UploadDatabaseService
from layer_db_utils.services.db_service import DatabaseService
from layer_s3_utils.services.s3_utils import stream_csv_from_s3

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get environment variables
S3_BUCKET_NAME = Config.S3_BUCKET_NAME
BATCH_SIZE = Config.BATCH_SIZE

upload_service = UploadDatabaseService()
db_service = DatabaseService()

def get_file_upload_list(file_upload_id):
    logger.info(f"Fetching file upload list for file_upload_id: {file_upload_id}")
    params = {
        "file_upload_id": file_upload_id
    }
    
    response, status_code = db_service.execute_stored_procedure(
        procedure_name="dbo.sproc_get_pending_file_upload_by_id",
        params=params,
        isJsonOutput=False
    )
    
    if status_code == 200:
        logger.info(f"Successfully retrieved file upload list for file_upload_id: {file_upload_id}")
        return response["data"]
    else:
        error_msg = response.get("error", "Failed to get file upload list")
        logger.error(f"Error getting file upload list: {error_msg}")
        raise Exception(error_msg)
    
def invoke_data_quality_proc(project_id, table_id):
    logger.info(f"Invoking data quality procedure for project_id: {project_id}, table_id: {table_id}")
    params = {
        "project_id": project_id,
        "table_id": table_id
    }
    
    response, status_code = db_service.execute_stored_procedure(
        procedure_name="dbo.sproc_invoke_data_quality_proc",
        params=params,
        isJsonOutput=False
    )
    
    if status_code == 200:
        logger.info(f"Successfully invoked data quality procedure for project_id: {project_id}, table_id: {table_id}")
        return response["data"]
    else:
        error_msg = response.get("error", "Failed to invoke data quality proc")
        logger.error(f"Error invoking data quality procedure: {error_msg}")
        raise Exception(error_msg)
       
def update_file_upload(file_upload_id, upload_status, error_message, user_id, other_updates_flag):
    logger.info(f"Updating file upload status for file_upload_id: {file_upload_id}, status: {upload_status}")
    params = {
        "file_upload_id": file_upload_id,
        "upload_status": upload_status,
        "error_message": error_message,
        "last_updated_by": user_id,
        "update_row_count": other_updates_flag
    }
    
    response, status_code = db_service.execute_stored_procedure(
        procedure_name="dbo.sproc_update_file_upload_status",
        params=params,
        isJsonOutput=False
    )
    
    if status_code == 200:
        logger.info(f"Successfully updated file upload status for file_upload_id: {file_upload_id}")
        return response["data"]
    else:
        error_msg = response.get("error", "Failed to update file upload status")
        logger.error(f"Error updating file upload status: {error_msg}")
        raise Exception(error_msg)
    
def delete_existing_file_upload_records(file_upload_id, table_name):
    logger.info(f"Deleting existing file upload records for file_upload_id: {file_upload_id}, table: {table_name}")
    params = {
        "file_upload_id": file_upload_id,
        "table_name": table_name,
    }
    
    response, status_code = db_service.execute_stored_procedure(
        procedure_name="dbo.sproc_delete_file_upload_records",
        params=params,
        isJsonOutput=False
    )
    
    if status_code == 200:
        logger.info(f"Successfully deleted file upload records for file_upload_id: {file_upload_id}")
        return response["data"]
    else:
        error_msg = response.get("error", "Failed to delete file upload records")
        logger.error(f"Error deleting file upload records: {error_msg}")
        raise Exception(error_msg)

def upload_data_to_sql_by_batch(rows, columns, target_table_name, target_schema):
    try:
        logger.info(f"Uploading batch of {len(rows)} rows to {target_schema}.{target_table_name}")
        result = upload_service.execute_upload(
            rows=rows,
            columns=columns,
            target_table=target_table_name,
            schema_name=target_schema
        )
        logger.info(f"Successfully uploaded batch to {target_schema}.{target_table_name}")
        return result
    except Exception as e:
        logger.error(f"Failed to upload data to SQL: {str(e)}")
        raise Exception(f"Failed to upload data to SQL: {str(e)}")

def stream_csv(bucket_name, file_path, file_name, column_delimiter, text_qualifier):
    key = f"{file_path}/{file_name}"
    logger.info(f"Streaming CSV file from S3: {bucket_name}/{key}")
    s3 = boto3.client('s3')

    try:
        return stream_csv_from_s3(bucket_name, file_path, file_name, column_delimiter, text_qualifier)
    except Exception as e:
        logger.error(f"Error streaming CSV file: {str(e)}")
        raise e
    
def build_tvp_rows(column_mapping: dict, data_rows: dict, file_upload_id: int) -> list[tuple]:
    try:
        tvp_row = []
        for target_col in column_mapping:
            if(target_col == 'file_upload_id'):
                tvp_row.append(file_upload_id)
            else:
                source_col = column_mapping[target_col]
                value = data_rows.get(source_col) if source_col else None
                tvp_row.append(value)
        return tvp_row
    except Exception as e:
        logger.error(f"Failed to build TVP rows: {str(e)}")
        raise Exception(f"Failed to build TVP rows: {str(e)}")

def process_csv(event, context, file_upload_id, user_id):
    logger.info(f"Starting CSV processing for file_upload_id: {file_upload_id}")
    pending_csv_uploads = get_file_upload_list(file_upload_id)

    for file_upload in pending_csv_uploads:
        try:
            file_upload_id = file_upload['file_upload_id']
            project_id = file_upload['project_id']
            table_id = file_upload['table_id']
            column_mapping = json.loads(file_upload['column_mapping'])
            csv_details = json.loads(file_upload['csv_details'])
            csv_column_seperator = csv_details["column_separator"]
            csv_text_qualifier = csv_details["text_qualifier"] or '"'

            logger.info(f"Processing file upload: {file_upload_id} for project: {project_id}, table: {table_id}")

            if column_mapping == {} or column_mapping is None:
                logger.warning(f"Column mapping not found for file_upload_id: {file_upload_id}")
                update_file_upload(
                    file_upload_id,
                    "Pending",
                    "Column mapping not found.",
                    user_id,
                    "0"
                )
            else:
                update_file_upload(
                    file_upload_id,
                    "Uploading",
                    "Data process has been initiated.",
                    user_id,
                    "0"
                )
                
                file_name = file_upload['file_name']
                file_path = file_upload['file_path']
                full_table_name = file_upload['physical_table_name']
                physical_table_schema = full_table_name.split('.', 1)[0]
                physical_table_name = full_table_name.split('.', 1)[1]
                data_upload_batch = []
                target_columns = list(column_mapping.keys())

                logger.info(f"Deleting existing records for file_upload_id: {file_upload_id}")
                delete_existing_file_upload_records(file_upload_id, full_table_name)

                logger.info(f"Starting to process CSV file: {file_name}")
                for row in stream_csv(bucket_name=S3_BUCKET_NAME, file_path=file_path, file_name=file_name, column_delimiter=csv_column_seperator, text_qualifier=csv_text_qualifier):
                    tvp_rows = build_tvp_rows(column_mapping=column_mapping, data_rows=row, file_upload_id=file_upload_id)
                    data_upload_batch.append(tvp_rows)

                    if len(data_upload_batch) == BATCH_SIZE:
                        upload_data_to_sql_by_batch(rows=data_upload_batch, columns=target_columns, target_table_name=physical_table_name, target_schema=physical_table_schema)
                        data_upload_batch.clear()

                if data_upload_batch:
                    logger.info(f"Uploading remaining {len(data_upload_batch)} rows")
                    upload_data_to_sql_by_batch(rows=data_upload_batch, columns=target_columns, target_table_name=physical_table_name, target_schema=physical_table_schema)

                update_file_upload(
                    file_upload_id,
                    "Completed",
                    "Data has been successfully uploaded.",
                    user_id,
                    "1"
                )

                logger.info(f"Invoking data quality procedure for project_id: {project_id}, table_id: {table_id}")
                invoke_data_quality_proc(project_id, table_id)
        except Exception as e:
            logger.error(f"Error processing file upload {file_upload_id}: {str(e)}")
            update_file_upload(
                file_upload_id,
                "Pending",
                str(e),
                user_id,
                "1"
            )
            continue

def lambda_handler(event, context):
    logger.info("Lambda function started")
    try:
        body = event.get("body")
        
        if isinstance(body, str):
            body = json.loads(body)
        elif not isinstance(body, dict):
            body = {}

        user_id = body.get("user_id")
        file_upload_id = body.get("file_upload_id")
        
        if not file_upload_id:
            logger.error("file_upload_id is required")
            return response_with_cors(400, {
                "body": json.dumps({
                    "error": "file_upload_id is required."
                })
            })

        if not user_id:
            logger.error("user_id is required")
            return response_with_cors(400, {
                "body": json.dumps({
                    "error": "user_id is required"
                })
            })

        logger.info(f"Processing request for file_upload_id: {file_upload_id}, user_id: {user_id}")
        result = process_csv(event, context, file_upload_id, user_id)

        logger.info("CSV processing completed successfully")
        return response_with_cors(200, {
            "body": json.dumps({
                "message": "CSV processed successfully",
                "result": result
            })
        })
         
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return response_with_cors(500, {'error': str(e)})

def response_with_cors(status_code, body_dict):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST',
            'Access-Control-Allow-Headers': '*'
        },
        'body': json.dumps(body_dict)
    } 