import pyodbc
import json
from lambda_database.database.config import Config 

class DatabaseService:
    def __init__(self):
        self.connection_string = f"DRIVER={Config.DRIVER};SERVER={Config.SERVER};DATABASE={Config.DATABASE};UID={Config.USERNAME};PWD={Config.PASSWORD};Encrypt=yes;TrustServerCertificate=yes;autocommit=True"

    def execute_stored_procedure(self, procedure_name, params, isCommit=False, isJsonOutput=False):
        try:
            param_tuple = tuple(params.values())

            with pyodbc.connect(self.connection_string, timeout=30) as conn:
                with conn.cursor() as cursor:
                    param_placeholders = ','.join(['?'] * len(param_tuple))
                    query = f"{{CALL {procedure_name}({param_placeholders})}}"
                    cursor.execute(query, *param_tuple)

                    if isJsonOutput:
                        row = cursor.fetchone()
                        json_string = row[0] if row else None
                        data = json.loads(json_string) if json_string else []
                    elif cursor.description:
                        rows = cursor.fetchall()
                        columns = [column[0] for column in cursor.description]
                        data = [dict(zip(columns, row)) for row in rows]
                    else:
                        data = []

                    if isCommit:
                        conn.commit()

                    return {"data": data, "message": "Procedure executed successfully"} 

        except Exception as e:
            return {"error": str(e)}
