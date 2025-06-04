import json
from typing import Optional
from layer_lambda_utils.invoke_lambda import invoke_lambda


class AmbiguityResolver:
    def __init__(self):
        pass
        
    def resolve_ambiguity(
        self,
        project_id: int,
        response_text: str,
        last_updated_by: str,
        question_type: str,
        test_id: int,
        options: Optional[str] = None
    ):
        """
        Function to resolve ambiguity in the test case using Lambda.
        """
        try:
            # Prepare parameters for the stored procedure
            params = {
                "project_id": project_id,
                "question_id": 0,
                "test_id": test_id,
                "response_text": response_text,
                "last_updated_by": last_updated_by,
                "is_ai_magic_response": 1,
                "role_name": "agent",
                "options": options,
                "question_type": question_type
            }

            # Create event for Lambda invocation
            event = {
                'httpMethod': 'POST',
                'path': '/insert_record',
                'body': json.dumps({
                    'procedure_name': 'sproc_insert_response_by_question_or_test',
                    'params': params
                })
            }

            # Execute the Lambda function
            response = invoke_lambda('calling-sql-procedure', event)

            if response.get('statusCode') != 200:
                raise Exception(response.get('body', 'Failed to insert response'))

            return {
                "status": "success",
                "message": "AI question stored successfully",
                "data": json.loads(response['body']).get('data', [])
            }

        except Exception as e:
            print("123", e)
            raise Exception(str(e))
