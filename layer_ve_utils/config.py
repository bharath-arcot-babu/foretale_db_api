import os

class Config:
    # Amazon Titan Embeddings model configuration
    MODEL_ID = 'amazon.titan-embed-text-v2:0'
    REGION_NAME = 'us-east-1'

    # MODEL_ID = os.environ.get('MODEL_ID')
    # REGION_NAME = os.environ.get('REGION_NAME')
