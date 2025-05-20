import os

class Config:
    # S3 and batch processing
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 1000))
