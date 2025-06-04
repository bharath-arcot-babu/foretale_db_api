import json
import os
import sys
import logging
from typing import List, Dict
from layer_file_utils.utils.doc_processing.pdf_utils import extract_text_from_pdf
from layer_file_utils.utils.doc_processing.excel_utils import extract_text_from_excel
from layer_file_utils.utils.doc_processing.word_utils import extract_text_from_word
from layer_file_utils.utils.doc_processing.txt_utils import extract_text_from_txt
from layer_file_utils.utils.doc_processing.ppt_utils import extract_text_from_ppt
from layer_file_utils.utils.txt_processing.chunk_text import chunk_text
from layer_lambda_utils.invoke_lambda import invoke_lambda
from layer_s3_utils.services.s3_utils import get_file_from_s3

def read_any_file(file_name: str, s3_file_path: str, s3_bucket_name: str) -> Dict:

    logger = logging.getLogger(__name__)
    
    # Get file extension
    _, file_extension = os.path.splitext(file_name)
    file_extension = file_extension.lower()
    
    logger.info(f"Processing file: {file_name} with extension: {file_extension}")
    
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
        logger.error(f"Unsupported file type: {file_extension}")
        raise ValueError(f"Unsupported file type: {file_extension}")
    
    try:
        # Handle S3 path format
        if s3_file_path.startswith('s3://'):
            # Format: s3://bucket/key
            key = '/'.join(s3_file_path.split('/')[3:])
            logger.info(f"Extracted S3 key: {key}")
        else:
            # Format: file_path/file_name
            key = f"{s3_file_path}/{file_name}"
            logger.info(f"Using file path: {key}")

        # Get file content from S3
        logger.info(f"Attempting to retrieve file from S3 bucket: {s3_bucket_name}")
        file_content = get_file_from_s3(s3_bucket_name, key)
        
        if file_content is None:
            logger.error(f"Failed to retrieve file content from S3. Bucket: {s3_bucket_name}, Key: {key}")
            raise Exception(f"Failed to retrieve file content from S3 for file: {file_name}")
            
        logger.info(f"Successfully retrieved file content from S3.")
        
        # Extract text using appropriate processor with the file-like object
        logger.info(f"Extracting text using processor for {file_extension}")
        text_content = processors[file_extension](file_content)
        
        if not text_content:
            logger.warning(f"No text content extracted from file: {file_name}")
        
        return {
            "file_name": file_name,
            "file_type": file_extension,
            "content": text_content,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error processing file {file_name}: {str(e)}", exc_info=True)
        raise Exception(f"Error processing file {file_name}: {str(e)}")

def delete_chunks_from_db(response_id: int, attachment_id: int) -> dict:
    """
    Delete chunks from the database using a stored procedure.
    """
    try:
        event = {
            'httpMethod': 'DELETE',
            'path': '/delete_record',
            'body': json.dumps({
                'procedure_name': 'sproc_delete_response_chunks',
                'params': {
                    'response_id': response_id,
                    'attachment_id': attachment_id
                }
            })
        }

        result = invoke_lambda('calling-sql-procedure', event)

        if result.get('statusCode') != 200:
            raise Exception(f"Error deleting chunks from database: {result.get('body')}")

        return json.loads(result['body'])

    except Exception as e:
        raise Exception(f"Error deleting chunks from database: {str(e)}")


def insert_chunks_to_db(chunks: List[str], question_id: int, test_id: int, response_id: int, 
                       attachment_id: int, created_by: int) -> dict:
    """
    Insert text chunks into the database using a Lambda-backed upload function.
    
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
        
        rows = [
            [
                question_id,
                test_id,
                response_id,
                attachment_id,
                idx,
                chunk,
                created_by
            ]
            for idx, chunk in enumerate(chunks)
        ]

        # Ensure body is JSON string as expected by Lambda
        event = {
            'body': json.dumps({
                'data': rows,
                'columns': columns,
                'target_table': 've_text_attachment_chunks',
                'schema': 'dbo'
            })
        }

        result = invoke_lambda('sql-server-data-upload', event)

        if result.get('statusCode') != 200 or 'body' not in result:
            raise Exception(f"Error inserting chunks to database: {result.get('body')}")

        return json.loads(result['body'])

    except Exception as e:
        raise Exception(f"Error inserting chunks to database: {str(e)}")


def update_indexing_status(response_id: int, stats: dict) -> dict:
    """
    Update the indexing status of the response.
    """
    try:
        result = invoke_lambda('calling-sql-procedure', {
            'httpMethod': 'PUT',
            'path': '/update_record',
            'body': json.dumps({
                'procedure_name': 'sproc_update_response_embedding_status',
                'params': {
                    'response_id': response_id,
                    'is_embedding_complete': 1 if stats.get("error") is None else 0,
                    'is_embedding_indexed': 1 if stats.get("error") is None else 0,
                    'vector_indexing_stats': json.dumps(stats)
                }
            })
        })

        # result['body'] might be str or dict, normalize to dict
        body = result.get('body')

        if result.get('statusCode') != 200:
            raise Exception(f"Error updating indexing status: {body}")
        
        return result

    except Exception as e:
        raise Exception(f"Error updating indexing status: {str(e)}")

    
def fetch_data_by_response(response_id: int) -> Dict:
    """
    Fetch data from stored procedure using response_id.
    Args:
        response_id (int): The response ID to fetch data for
    Returns:
        Dict: Dictionary containing the fetched data
    Raises:
        Exception: If there's an error executing the stored procedure
    """
    try:
        event = {
            'httpMethod': 'GET',
            'path': '/read_json_record',
            'queryStringParameters': {
                'procedure_name': 'sproc_get_responses_with_attachments_by_id',
                'response_id': str(response_id)  # Make sure it's a string
            }
        }

        result = invoke_lambda('calling-sql-procedure', event)

        if result.get('statusCode') != 200 or 'body' not in result:
            raise Exception(f"Error fetching data from stored procedure: {result.get('body')}")
        
        if 'data' in json.loads(result['body']):
            return json.loads(result['body'])['data']
        else:
            raise Exception(f"Error fetching data from stored procedure: {result.get('body')}")

    except Exception as e:
        raise Exception(f"Error fetching data from stored procedure: {str(e)}")


def embed_chunks(chunks: List[str]) -> List[Dict]:
    """
    Embed text chunks using the vector embeddings service.
    
    Args:
        chunks (List[str]): List of text chunks
    
    Returns:
        List[Dict]: List of dictionaries containing embeddings and chunk text
    """
    try:
        # Process each chunk individually
        results = []

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
                    embedding = json.loads(body)
                    results.append({
                        'embedding': embedding,
                        'chunk_text': chunk
                    })
                else:
                    raise Exception(f"Unexpected body format: {body}")
            else:
                raise Exception(f"Error response: {response}")

        return results
    except Exception as e:
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

def insert_vectors_to_pinecone(embeddings: List[Dict], question_id: int, test_id: int, response_id: int, attachment_id: int, file_name: str) -> dict:
    """
    Insert vectors to Pinecone.
    """
    metadata_list = []
    pinecone_embeddings = []
    for embedding in embeddings:
        metadata_list.append({
            'chunk_text': embedding['chunk_text'],
            'question_id': question_id,
            'test_id': test_id,
            'response_id': response_id,
            'attachment_id': attachment_id
        })
        
        pinecone_embeddings.append(embedding['embedding'])
        
    try:

        result = invoke_lambda('pinecone-vector-storage-and-query', {
            'body': {
                'action': 'insert_embeddings',
                'index_name': 'qa-test-configuration-index',
                'embeddings': pinecone_embeddings,
                'metadata_list': metadata_list,
                'namespace': file_name
            }
        })

        if result.get('statusCode') != 200:
            raise Exception(f"Error inserting vectors to Pinecone: {result.get('body')}")
        
        return result

    except Exception as e:
        raise Exception(f"Error inserting vectors to Pinecone: {str(e)}")



def main() -> Dict:
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    try:
        if len(sys.argv) < 2:
            logger.error("Missing required arguments")
            raise Exception("response_id and user_id are required")
        
        # get the response_id and user_id from the command line arguments
        response_id = sys.argv[1]
        user_id = sys.argv[2]

        logger.info(f"Processing response_id: {response_id} for user_id: {user_id}")

        #if the response_id is not present, return an error
        if not response_id:
            logger.error("response_id is missing")
            raise Exception("response_id is required")
        
        # if the user_id is not present, return an error
        if not user_id:
            logger.error("user_id is missing")
            raise Exception("user_id is required")

        # fetch the response data from the database
        logger.info("Fetching response data from database")
        response_data = fetch_data_by_response(response_id)

        if not response_data:
            logger.error(f"No responses found for response_id: {response_id}")
            raise Exception(f"No responses found for the given response_id - {response_id}")
        else:
            response_data = response_data[0]
            response_id = response_data.get("response_id")
            question_id = response_data.get("question_id")
            test_id = response_data.get("test_id")
            response_text = response_data.get("response_text")

            logger.info(f"Processing response for question_id: {question_id}, test_id: {test_id}")

            if response_data["attachments"]:
                attachments = response_data["attachments"]
                logger.info(f"Found {len(attachments)} attachments to process")
                
                # Process each attachment
                for attachment in attachments:
                    attachment_id = attachment["attachment_id"]
                    file_path = attachment["file_path"] # this is S3 path
                    file_name = attachment["file_name"]

                    logger.info(f"Processing attachment: {file_name} (ID: {attachment_id})")

                    # read the file
                    logger.info("Reading file contents")
                    s3_bucket_name = os.environ["S3_BUCKET_NAME"]
                    if not s3_bucket_name:
                        raise Exception("S3_BUCKET_NAME is not set")
                    
                    contents = read_any_file(file_name, file_path, s3_bucket_name)

                    # chunk the file
                    logger.info("Chunking file contents")
                    chunks = chunk_text(
                        contents["content"], 
                        chunk_size=500, 
                        chunk_overlap=100)
                    
                    # if the chunks are empty, return an error
                    if not chunks:
                        logger.error("No chunks generated from file content")
                        raise Exception("No chunks found")
                    
                    logger.info(f"Generated {len(chunks)} chunks")
                    
                    # delete the chunks from the database if they exist
                    logger.info("Deleting existing chunks from database")
                    delete_chunks_from_db(response_id, attachment_id)

                    # insert the chunks to the database
                    logger.info("Inserting chunks to database")
                    insert_chunks_to_db(
                        chunks, 
                        question_id = question_id, 
                        test_id = test_id, 
                        response_id = response_id, 
                        attachment_id = attachment_id, 
                        created_by = user_id,
                    )

                    # embed the chunks   
                    logger.info("Generating embeddings for chunks")
                    embeddings = embed_chunks(chunks)

                    # if the embeddings are not empty, insert the vectors to Pinecone
                    if embeddings:
                        logger.info(f"Generated {len(embeddings)} embeddings")
                        
                        # delete the vectors from Pinecone if they exist
                        logger.info("Deleting existing vectors from Pinecone based on response_id and attachment_id")
                        result = delete_vectors_from_pinecone(response_id, attachment_id)

                        if result.get('statusCode') != 200: 
                            logger.error(f"Failed to delete vectors from Pinecone: {result.get('body')}")
                            raise Exception(f"Error deleting vectors from Pinecone: {result.get('body')}")

                        # insert the vectors to Pinecone
                        logger.info("Inserting vectors to Pinecone")
                        result = insert_vectors_to_pinecone(
                            embeddings, 
                            question_id, 
                            test_id, 
                            response_id, 
                            attachment_id,
                            file_name
                        )
                        
                        if result.get('statusCode') == 200:
                            logger.info("Successfully inserted vectors to Pinecone")
                            # Parse the response body if it's a string
                            if isinstance(result.get('body'), str):
                                body = json.loads(result.get('body'))
                            else:
                                body = result.get('body')
                            
                            # update the indexing status
                            logger.info("Updating indexing status")
                            update_indexing_status(response_id, body)
                            logger.info("Successfully processed attachment")
                        else:
                            logger.error(f"Failed to insert vectors to Pinecone: {result.get('body')}")

                
                               
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        raise Exception(f"Error processing file: {str(e)}")



if __name__ == "__main__":
    main()