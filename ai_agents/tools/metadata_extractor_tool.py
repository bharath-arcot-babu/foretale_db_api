import json
from layer_lambda_utils.invoke_lambda import invoke_lambda

class MetadataExtractor:
    def __init__(self):
        pass

    def get_schema_tables(self, project_id=None, key_tables=None):
        """
        Extract table information using sproc_get_schema_tables stored procedure.
        
        Args:
            project_id (str, optional): Name of the schema to get tables for. If None, returns tables for all schemas.
            key_tables (list, optional): List of specific tables to get information for.
            
        Returns:
            dict: Response containing table information and status code
        """
        try:
            event = {
                'httpMethod': 'GET',
                'path': '/read_record',
                'queryStringParameters': {
                    'procedure_name': 'sproc_get_schema_tables',
                    'project_id': project_id,
                    'table_list': key_tables
                }
            }

            result = invoke_lambda('calling-sql-procedure', event)

            if result.get('statusCode') != 200 or 'body' not in result:
                raise Exception(f"Error fetching schema tables: {result.get('body')}")
            
            if 'data' in json.loads(result['body']):
                return json.loads(result['body'])['data']
            else:
                raise Exception(f"Error fetching schema tables: {result.get('body')}")

        except Exception as e:
            raise Exception(f"Error fetching schema tables: {str(e)}")
        
    def get_table_columns(self, project_id, target_table_list):
        """
        Extract column information for specified tables.
        
        Args:
            project_id (str): Name of the project
            target_table_list (list): List of table names to get columns for
        
        Returns:
            dict: Response containing column information and status code
        """
        try:
            event = {
                'httpMethod': 'GET',
                'path': '/read_record',
                'queryStringParameters': {
                    'procedure_name': 'sproc_get_schema_table_columns',
                    'project_id': project_id,
                    'target_table_list': target_table_list
                }
            }

            result = invoke_lambda('calling-sql-procedure', event)

            if result.get('statusCode') != 200 or 'body' not in result:
                raise Exception(f"Error fetching table columns: {result.get('body')}")
            
            if 'data' in json.loads(result['body']):
                return json.loads(result['body'])['data']
            else:
                raise Exception(f"Error fetching table columns: {result.get('body')}")

        except Exception as e:
            raise Exception(f"Error fetching table columns: {str(e)}")
        
    def get_join_hints(self, table_list):
        """
        Extract join hints for specified tables.
        
        Args:
            table_list (list): List of table names to get join hints for
        
        Returns:
            dict: Response containing join hints information and status code
        """
        try:
            event = {
                'httpMethod': 'GET',
                'path': '/read_record',
                'queryStringParameters': {
                    'procedure_name': 'sproc_get_schema_join_paths',
                    'table_names': table_list
                }
            }

            result = invoke_lambda('calling-sql-procedure', event)

            if result.get('statusCode') != 200 or 'body' not in result:
                raise Exception(f"Error fetching join hints: {result.get('body')}")
            
            if 'data' in json.loads(result['body']):
                return json.loads(result['body'])['data']
            else:
                raise Exception(f"Error fetching join hints: {result.get('body')}")

        except Exception as e:
            raise Exception(f"Error fetching join hints: {str(e)}")
    
