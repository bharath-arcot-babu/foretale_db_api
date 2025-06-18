from layer_lambda_utils.invoke_lambda import invoke_lambda
import json

class UpdateConfigToDatabaseTool:
    def __init__(self):
        pass

    def update_status_to_database(self, 
                                  project_id, 
                                  test_id, 
                                  status,
                                  last_updated_by):
        """
        Update status to database using sproc_update_status stored procedure.

        Args:
            project_id (int): Id of the project
            test_id (int): Id of the test
            status (str): Status to update
            last_updated_by (str): Last updated by
        Returns:
            dict: Response containing table information and status code
        """
        params = {
            "project_id": project_id,
            "test_id": test_id,
            "test_config_update_status": status,
            "last_updated_by": last_updated_by
        }

        event = {
            'httpMethod': 'PUT',
            'path': '/update_record',
            'body': json.dumps({
                'procedure_name': 'dbo.sproc_update_project_test_config_status',
                'params': params
            })
        }

        response = invoke_lambda('calling-sql-procedure', event)
        
        if response.get('statusCode') == 200:
            return json.loads(response['body'])['data']
        else:
            raise Exception(response.get('body', 'Failed to update status to database'))
        
        
    def update_config_to_database(self, 
                                  project_id, 
                                  test_id, 
                                  ai_summary,
                                  ai_key_tables,
                                  ai_key_columns,
                                  ai_key_criteria,
                                  ai_key_join_hints,
                                  ai_ambiguities,
                                  ai_full_state,
                                  config,
                                  last_updated_by,
                                  status,
                                  message):
        """
        Update config to database using sproc_update_config_to_database stored procedure.
        
        Args:
            project_id (int): Id of the project
            test_id (int): Id of the test
            config (str): Config to update
            last_updated_by (str): Last updated by
        Returns:
            dict: Response containing table information and status code
        """
        params = {
            "project_id": project_id,
            "test_id": test_id,
            "ai_summary": ai_summary,
            "ai_key_tables": ai_key_tables,
            "ai_key_columns": ai_key_columns,
            "ai_key_criteria": ai_key_criteria,
            "ai_join_hints": ai_key_join_hints,
            "ai_ambiguities": ai_ambiguities,
            "ai_full_state": ai_full_state,
            "config": config,
            "last_updated_by": last_updated_by,
            "test_config_update_status": status,
            "message": message
        }
        
        event = {
            'httpMethod': 'PUT',
            'path': '/update_record',
            'body': json.dumps({
                'procedure_name': 'dbo.sproc_update_project_test_config',
                'params': params
            })
        }

        response = invoke_lambda('calling-sql-procedure', event)
        
        if response.get('statusCode') == 200:
            return json.loads(response['body'])['data']
        else:
            raise Exception(response.get('body', 'Failed to update config to database'))