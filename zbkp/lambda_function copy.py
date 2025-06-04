import json
import os
from typing import List, Dict
from layer_db_utils.services.upload_service import UploadDatabaseService
from layer_db_utils.services.db_service import DatabaseService
from utils.doc_processing.pdf_utils import extract_text_from_pdf
from utils.doc_processing.excel_utils import extract_text_from_excel
from utils.doc_processing.word_utils import extract_text_from_word
from utils.doc_processing.txt_utils import extract_text_from_txt
from utils.doc_processing.ppt_utils import extract_text_from_ppt
from utils.txt_processing.chunk_text import chunk_text
from layer_lambda_utils.invoke_lambda import invoke_lambda
from layer_s3_utils.services.s3_utils import get_file_from_s3
#from layer_file_utils.config import Config

# Get environment variables
S3_BUCKET_NAME = "foretaleapplication24783bf682ff4b3dbe61719ba699957de-dev" #Config.S3_BUCKET_NAME

# Initialize services
upload_service = UploadDatabaseService()
db_service = DatabaseService()


def read_any_file(file_name: str, s3_file_path: str) -> Dict:
    """
    Read and extract text content from various file types.
    Supports PDF, Excel, Word, Text, and PowerPoint files.
    
    Args:
        file_name (str): Name of the file
        s3_file_path (str): S3 path to the file (s3://bucket/key) or regular path
    
    Returns:
        Dict: Dictionary containing extracted text and metadata
    
    Raises:
        ValueError: If file type is not supported
        Exception: If there's an error processing the file
    """
    # Get file extension
    _, file_extension = os.path.splitext(file_name)
    file_extension = file_extension.lower()
    
    # Map file extensions to their processors
    processors = {
        '.xlsx': extract_text_from_excel,
        '.xls': extract_text_from_excel,
        '.docx': extract_text_from_word,
        '.doc': extract_text_from_word,
        '.txt': extract_text_from_txt,
        '.ppt': extract_text_from_ppt,
        '.pptx': extract_text_from_ppt,
        '.pdf': extract_text_from_pdf
    }
    
    # Check if file type is supported
    if file_extension not in processors:
        raise ValueError(f"Unsupported file type: {file_extension}")
    
    try:
        # Handle S3 path format
        if s3_file_path.startswith('s3://'):
            # Format: s3://bucket/key
            key = '/'.join(s3_file_path.split('/')[3:])
        else:
            # Format: file_path/file_name
            key = f"{s3_file_path}/{file_name}"

        # Get file content from S3
        file_content = get_file_from_s3(S3_BUCKET_NAME, key)
        
        # Extract text using appropriate processor with the file-like object
        text_content = processors[file_extension](file_content)
        
        return {
            "file_name": file_name,
            "file_type": file_extension,
            "content": text_content,
            "status": "success"
        }
        
    except Exception as e:
        raise Exception(f"Error processing file {file_name}: {str(e)}")


def delete_chunks_from_db(response_id: int, attachment_id: int) -> dict:
    """
    Delete chunks from the database.
    """
    try:
        db_service.execute_stored_procedure(
                        procedure_name="sproc_delete_response_chunks",
                        params={
                            "response_id": response_id,
                            "attachment_id": attachment_id,
                        }
                    )
    except Exception as e:
        raise Exception(f"Error deleting chunks from database: {str(e)}")


def insert_chunks_to_db(chunks: List[str], question_id: int, test_id: int, response_id: int, 
                       attachment_id: int, created_by: int) -> dict:
    """
    Insert text chunks into the database.
    
    Args:
        chunks (List[str]): List of text chunks
        question_id (int): ID of the question
        test_id (int): ID of the test
        response_id (int): ID of the response
        attachment_id (int): ID of the attachment
        created_by (int): User ID who created the chunks
    
    Returns:
        dict: API response
    """
    try:
        # Prepare the data for insertion
        columns = ['question_id', 'test_id', 'response_id', 'attachment_id', 
                  'chunk_index', 'chunk_text', 'created_by']
        
        rows = []
        for chunk_index, chunk_text in enumerate(chunks):
            row = [
                question_id,
                test_id,
                response_id,
                attachment_id,
                chunk_index,  # chunk_index
                chunk_text,  # chunk_text
                created_by
            ]
            rows.append(row)

        
        
        # Call upload service to insert data
        result = upload_service.execute_upload(
            rows=rows, 
            columns=columns, 
            target_table="ve_text_attachment_chunks", 
            schema_name="dbo",
        )
        
    except Exception as e:
        raise Exception(f"Error inserting chunks to database: {str(e)}")

def fetch_data_by_response(response_id: int) -> Dict:
    """
    Fetch data from stored procedure using response_id.
    
    Args:
        response_id (str): The response ID to fetch data for
    
    Returns:
        Dict: Dictionary containing the fetched data and status message
    
    Raises:
        Exception: If there's an error executing the stored procedure
    """
    try:

        # Execute stored procedure with response_id parameter
        result, status_code = db_service.execute_stored_procedure(
            procedure_name="sproc_get_responses_with_attachments_by_id",
            params={"response_id": response_id},
            isJsonOutput=True
        )

        if status_code != 200:
            raise Exception(f"Error fetching data from stored procedure: {result.get('body')}")

        return result.get('data')
        
    except Exception as e:
        raise Exception(f"Error fetching data from stored procedure: {str(e)}")

def embed_chunks(chunks: List[str]) -> Dict:
    """
    Embed text chunks using the vector embeddings service.
    
    Args:
        chunks (List[str]): List of text chunks
        question_id (int): ID of the question
        test_id (int): ID of the test
        response_id (int): ID of the response
        attachment_id (int): ID of the attachment
        user_id (int): ID of the user
    """
    try:
        # Process each chunk individually
        embeddings = []

        for chunk_index, chunk in enumerate(chunks):
            response = invoke_lambda('bedrock_ve_invoker', {
                'body': {
                    'inputText': chunk  # Send as a string, not an array
                }
            })
            
            # Handle the response properly based on its structure
            if response.get('statusCode') == 200 and 'body' in response:
                body = response['body']
                if isinstance(body, str):
                    # If body is a string (JSON), parse it
                    embeddings.append(json.loads(body))
                else:
                    raise Exception(f"Unexpected body format: {body}")
            else:
                raise Exception(f"Error response: {response}")

        return embeddings
    except Exception as e:
        print(f"Error in embed_chunks: {str(e)}")
        raise Exception(f"Error embedding chunks: {str(e)}")

def delete_vectors_from_pinecone(response_id: int, attachment_id: int) -> dict:
    """
    Delete vectors from Pinecone.
    """
    try:
        result =invoke_lambda('pinecone-vector-storage-and-query', {
            'body': {
                'action': 'delete_embeddings',
                'index_name': 'qa-test-configuration-index',
                'filter': {
                    'response_id': response_id,
                    'attachment_id': attachment_id
                }
            }
        })

        if result.get('statusCode') != 200:
            raise Exception(f"Error deleting vectors from Pinecone: {result.get('body')}")
        
        return result

    except Exception as e:
        raise Exception(f"Error deleting vectors from Pinecone: {str(e)}")

def insert_vectors_to_pinecone(embeddings: List[List[float]], question_id: int, test_id: int, response_id: int, attachment_id: int, file_name: str) -> dict:
    """
    Insert vectors to Pinecone.
    """
    metadata_list = []
    for embedding in embeddings:
        metadata_list.append({
            'question_id': question_id,
            'test_id': test_id,
            'response_id': response_id,
            'attachment_id': attachment_id
        })

    try:
        result = invoke_lambda('pinecone-vector-storage-and-query', {
            'body': {
                'action': 'insert_embeddings',
                'index_name': 'qa-test-configuration-index',
                'embeddings': embeddings,
                'metadata_list': metadata_list,
                'namespace': file_name
            }
        })

        if result.get('statusCode') != 200:
            raise Exception(f"Error inserting vectors to Pinecone: {result.get('body')}")
        
        return result

    except Exception as e:
        raise Exception(f"Error inserting vectors to Pinecone: {str(e)}")

def update_indexing_status(response_id: int, stats: dict) -> dict:
    """
    Update the indexing status of the response.
    """
    try:
        result =db_service.execute_stored_procedure(
                        procedure_name="sproc_update_response_embedding_status",
                        params={
                            "response_id": response_id,
                            "is_embedding_complete": None,
                            "is_embedding_indexed": 1 if stats["error"] is None else 0,
                            "vector_indexing_stats": json.dumps(stats)
                        }
                    )
        
        return result
    except Exception as e:
        raise Exception(f"Error updating indexing status: {str(e)}")

def lambda_handler(event, context) -> Dict:
    try:
        # Extract user_id from JSON body (assuming application/json request)
        body = event.get("body")

        #if the body is a string, load it as a json object
        if isinstance(body, str):
            body = json.loads(body)
        elif not isinstance(body, dict):
            body = {}
            
        response_id = body.get('response_id')
        user_id = body.get('user_id')

        #if the response_id is not present, return an error
        if not response_id:
            raise Exception("response_id is required")
        
        # if the user_id is not present, return an error
        if not user_id:
            raise Exception("user_id is required")

        # fetch the response data from the database
        response_data = fetch_data_by_response(response_id)

        if not response_data:
            raise Exception("No responses found")
        else:
            response_data = response_data[0]
            response_id = response_data.get("response_id")
            question_id = response_data.get("question_id")
            test_id = response_data.get("test_id")
            response_text = response_data.get("response_text")

            if response_data["attachments"]:
                attachments = response_data["attachments"]
                # Process each attachment
                for attachment in attachments:
                    attachment_id = attachment["attachment_id"]
                    file_path = attachment["file_path"] # this is S3 path
                    file_name = attachment["file_name"]

                    # read the file
                    contents = read_any_file(file_name, file_path)

                    # chunk the file
                    chunks = chunk_text(
                        contents["content"], 
                        chunk_size=500, 
                        chunk_overlap=100)
                    
                    # if the chunks are empty, return an error
                    if not chunks:
                        raise Exception("No chunks found")
                    
                    # delete the chunks from the database if they exist
                    
                    delete_chunks_from_db(response_id, attachment_id)

                    # insert the chunks to the database
                    insert_chunks_to_db(
                        chunks, 
                        question_id = question_id, 
                        test_id = test_id, 
                        response_id = response_id, 
                        attachment_id = attachment_id, 
                        created_by = user_id,
                    )

                    # embed the chunks   
                    embeddings = embed_chunks(chunks)

                    # if the embeddings are not empty, insert the vectors to Pinecone
                    if embeddings:
                        # delete the vectors from Pinecone if they exist
                        result = delete_vectors_from_pinecone(response_id, attachment_id)

                        if result.get('statusCode') != 200: 
                            raise Exception(f"Error deleting vectors from Pinecone: {result.get('body')}")

                        # insert the vectors to Pinecone
                        
                        result = insert_vectors_to_pinecone(
                            embeddings, 
                            question_id, 
                            test_id, 
                            response_id, 
                            attachment_id,
                            file_name
                        )
                        
                        if result.get('statusCode') == 200:
                            # Parse the response body if it's a string
                            if isinstance(result.get('body'), str):
                                body = json.loads(result.get('body'))
                            else:
                                body = result.get('body')
                            
                            # update the indexing status
                            update_indexing_status(response_id, body)
                        
                               
    except Exception as e:
        raise Exception(f"Error processing file: {str(e)}")


lambda_handler({
    "body": {
        "response_id": 55,
        "user_id": 1
    }
}, {})