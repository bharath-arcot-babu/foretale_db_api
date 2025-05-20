import boto3
import json
from typing import List, Union
from layer_ve_utils.config import Config

def generate_amazon_titan_embeddings(
    input_text: List[str], 
    model_id: str = 'amazon.titan-embed-text-v2:0',
    region_name: str = 'us-east-1'
) -> Union[List[float], List[List[float]]]:
    """
    Generate embeddings for a text or list of texts using Amazon Bedrock.
    
    Args:
        input_text: Single text string or list of text strings to embed
        model_id: Bedrock model ID to use
        region_name: AWS region to use
        
    Returns:
        List of float values (embedding) or list of embeddings if input was a list
    """
    # Initialize Bedrock client
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name=region_name
    )

    try:
        for text in input_text:
            payload = {
                "inputText": text,
                "dimensions": Config.DIMENSIONS,
                "normalize": True
            }
        
            # Generate embeddings
            response = bedrock.invoke_model(
                modelId=model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(payload)
            )
            
            # Parse the response
            result = json.loads(response['body'].read())

            if isinstance(result, dict) and 'embedding' in result:
                return result['embedding']
            else:
                raise Exception(f"Unexpected response format: {result}")
    
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        raise