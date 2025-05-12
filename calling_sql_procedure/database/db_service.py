import pyodbc
import json
from database.config import Config

class DatabaseService:
    def __init__(self):
        self.connection_string = (
            f"DRIVER={Config.DRIVER};"
            f"SERVER={Config.SERVER};"
            f"DATABASE={Config.DATABASE};"
            f"UID={Config.USERNAME};"
            f"PWD={Config.PASSWORD};"
            f"Encrypt=yes;TrustServerCertificate=yes;autocommit=True"
        )

    def execute_stored_procedure(self, procedure_name, params=None, isCommit=False, isJsonOutput=False):
        if not procedure_name:
            return {"error": "Procedure name is required."}, 400

        param_tuple = tuple(params.values()) if params else ()

        try:
            with pyodbc.connect(self.connection_string, timeout=30) as conn:
                with conn.cursor() as cursor:
                    # Build the query string
                    if param_tuple:
                        placeholders = ','.join(['?'] * len(param_tuple))
                        query = f"{{CALL {procedure_name}({placeholders})}}"
                        cursor.execute(query, *param_tuple)
                    else:
                        query = f"{{CALL {procedure_name}}}"
                        cursor.execute(query)

                    # Fetch result
                    if isJsonOutput:
                        row = cursor.fetchone()
                        json_string = row[0] if row else None
                        data = json.loads(json_string) if json_string else []
                    elif cursor.description:
                        rows = cursor.fetchall()
                        columns = [col[0] for col in cursor.description]
                        data = [dict(zip(columns, row)) for row in rows]  # Remove the serialization step
                    else:
                        data = []

                    if isCommit:
                        conn.commit()

                    return {"data": data, "message": "Procedure executed successfully"}, 200

        except pyodbc.Error as db_err:
            return {"error": f"Database error: {str(db_err)}"}, 500
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}, 500
