import os
class Config:
    SERVER = os.environ["Server"]
    DATABASE = os.environ["Database"]
    USERNAME = os.environ["Username"]
    PASSWORD = os.environ["Password"]
    DRIVER = os.environ["Driver"]

    #SERVER = 'hexango.clqoi2aemq8p.ap-south-1.rds.amazonaws.com'
    #DATABASE = "foretale"
    #USERNAME = "admin"
    #PASSWORD = "foreHEX!2025"
    #DRIVER = "{ODBC Driver 18 for SQL Server}"

    # API Gateway URLs
    API_GATEWAY_READ_WITH_JSON_URL = os.getenv("API_GATEWAY_READ_WITH_JSON_URL")
    API_GATEWAY_READ_URL = os.getenv("API_GATEWAY_READ_URL")
    API_GATEWAY_PUT_URL = os.getenv("API_GATEWAY_PUT_URL")
    API_GATEWAY_POST_URL = os.getenv("API_GATEWAY_POST_URL")
    API_GATEWAY_DELETE_URL = os.getenv("API_GATEWAY_DELETE_URL")
    API_GATEWAY_POST_UPLOAD_URL = os.getenv("API_GATEWAY_POST_UPLOAD_URL")

    # S3 and batch processing
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 1000))