import os

class Config:
    # SQL Server connection
    SERVER = os.environ["Server"]
    DATABASE = os.environ["Database"]
    USERNAME = os.environ["Username"]
    PASSWORD = os.environ["Password"]
    DRIVER = os.environ["Driver"]

    # API Gateway URLs
    API_GATEWAY_READ_URL = os.getenv("API_GATEWAY_READ_URL")
    API_GATEWAY_PUT_URL = os.getenv("API_GATEWAY_PUT_URL")
    API_GATEWAY_POST_URL = os.getenv("API_GATEWAY_POST_URL")
    API_GATEWAY_DELETE_URL = os.getenv("API_GATEWAY_DELETE_URL")
    API_GATEWAY_POST_UPLOAD_URL = os.getenv("API_GATEWAY_POST_UPLOAD_URL")

    # S3 and batch processing
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 1000))
