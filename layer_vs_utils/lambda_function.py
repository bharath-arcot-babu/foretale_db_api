import json
from layer_vs_utils.services.pinecone_service import PineconeService

def lambda_handler(event, context):
    try:
        # Extract user_id from JSON body (assuming application/json request)
        body = event.get("body")

        #if the body is a string, load it as a json object
        if isinstance(body, str):
            body = json.loads(body)
        elif not isinstance(body, dict):
            body = {}

        action = body.get("action")
        if not action:
            raise Exception("action is required")
        
        index_name = body.get('index_name')
        if not index_name:
            raise Exception("index_name is required")

        pinecone_service = PineconeService(
            index_name=index_name
        )

        if action == "insert_embeddings":
            embeddings = body.get('embeddings')
            if not embeddings:
                raise Exception("embeddings are required")
            
            metadata_list = body.get('metadata_list')
            if not metadata_list:
                raise Exception("metadata_list is required")
            
            namespace = body.get('namespace')
            if not namespace:
                raise Exception("namespace is required")

            result = pinecone_service.insert_embeddings(
                embeddings=embeddings,
                metadata_list=metadata_list,
                namespace=namespace
            )

        elif action == "query_embeddings":
            query_vector = body.get('query_vector')
            if not query_vector:
                raise Exception("query_vector is required")
            
            top_k = body.get('top_k')
            if not top_k:
                raise Exception("top_k is required")

            result = pinecone_service.query_embeddings(
                query_vector=query_vector,
                top_k=top_k
            )

        elif action == "delete_embeddings":
            filter = body.get('filter')
            if not filter:
                raise Exception("filter is required")

            result = pinecone_service.delete_vectors(
                filter=filter
            )

        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

"""
if __name__ == "__main__":
    result = lambda_handler({
        "body": {
            "action": "insert_embeddings",
            "index_name": "qa-test-configuration-index",
            "embeddings": [[0.1] * 512, [0.2] * 512],  # Create 512-dimensional vectors
            "metadata_list": [{"response_id": "54"}, {"response_id": "54"}]
        }
    }, {})

    print(result)
"""