from layer_ve_utils.utils.amazon_titan_embeddings import generate_amazon_titan_embeddings
from layer_ve_utils.config import Config
import json

def lambda_handler(event, context): 
    try:
        # Extract input text from event
        event_body = event.get('body')
        if isinstance(event_body, str):
            event_body = json.loads(event_body)
        elif not isinstance(event_body, dict):
            event_body = {}

        input_text = event_body.get('inputText')

        model_dict = {
            'amazon.titan-embed-text-v2:0': generate_amazon_titan_embeddings,
        }

        if Config.MODEL_ID not in model_dict:
            raise ValueError(f"Unsupported model: {Config.MODEL_ID}")

        embeddings = model_dict[Config.MODEL_ID](
            [input_text],
            model_id = Config.MODEL_ID,
            region_name = Config.REGION_NAME
        )
        
        # Return embeddings
        return {
            'statusCode': 200,
            'body': json.dumps(embeddings),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
