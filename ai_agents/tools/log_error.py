import json
from layer_lambda_utils.invoke_lambda import invoke_lambda

class LogError:
    def __init__(self):
        pass

    def log_error(self, error_message, error_stack_trace, error_source, severity_level, user_machine_id, request_path):
        """
        Logs an error to the database.

        Args:
            error_message (str): The error message to log.
            error_stack_trace (str): The stack trace of the error.
            error_source (str): The source of the error.
            severity_level (str): The severity level of the error.
            user_machine_id (str): The user machine id.
            request_path (str): The request path.
        """

        try:
            payload = {
                "error_message": error_message,
                "error_stack_trace": error_stack_trace,
                "error_source": error_source,
                "severity_level": severity_level,
                "user_machine_id": user_machine_id,
                "request_path": request_path
            }

            invoke_lambda('calling-sql-procedure', payload)

        except Exception as e:
            print(f"Error logging error: {e}")
