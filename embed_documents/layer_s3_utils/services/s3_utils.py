import gzip
import boto3
import io
import csv

# Initialize S3 client
s3_client = boto3.client('s3')

def get_file_from_s3(bucket_name: str, key_name: str) -> io.BytesIO:
    """
    Get file from S3 bucket.
    
    Args:
        s3_path (str): S3 path in format s3://bucket/key
    
    Returns:
        io.BytesIO: File content in memory
    """
    response = s3_client.get_object(Bucket=bucket_name, Key=key_name)
    
    return io.BytesIO(response['Body'].read()) 

def stream_csv_from_s3(bucket_name, file_path, file_name, column_delimiter, text_qualifier):
    """
    Stream CSV from S3 bucket.
    
    Args:
        bucket_name (str): Name of the S3 bucket
        file_path (str): Path to the file in the bucket
        file_name (str): Name of the file
        column_delimiter (str): Delimiter for the CSV file
        text_qualifier (str): Qualifier for the CSV file
    
    Returns:
        Generator: Generator of rows from the CSV file
    """
    key = f"{file_path}/{file_name}"
    s3 = boto3.client('s3');

    try:
        # Get the file from S3
        response = s3.get_object(Bucket = bucket_name, Key = key)
        body = response['Body']
        # Check if the file is compressed
        if 'ContentEncoding' in response and response['ContentEncoding'] == 'gzip': 
            # If the file is compressed, decompress it
            with gzip.GzipFile(fileobj=body) as gz:
                # Read the decompressed file
                for row in csv.DictReader(io.TextIOWrapper(gz, encoding='utf-8'), delimiter=column_delimiter, quotechar=text_qualifier):
                    yield row
        else:
            # If the file is not compressed, read it directly
            for row in csv.DictReader(io.TextIOWrapper(body, encoding='utf-8'), delimiter=column_delimiter, quotechar=text_qualifier):
                yield row
    
    except Exception as e:
        raise e