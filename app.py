#API Type: RESTful API
#Framework: Flask
#Database: SQL Server
#Library: pyodbc

from flask import Flask, request, jsonify
import pyodbc
from config import Config 
from waitress import serve

app = Flask(__name__)

server = Config.SERVER
database = Config.DATABASE
username = Config.USERNAME
password = Config.PASSWORD
driver = Config.DRIVER

connectionString = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=yes'

# Common function to execute stored procedures
def execute_stored_procedure(procedure_name, params):
    conn = None
    cursor = None
    try:
        # Construct parameter tuple
        param_values = []
        for key, value in params.items():
            if isinstance(value, list):
                param_values.append(','.join(map(str, value)))
            else:
                param_values.append(value)
        param_tuple = tuple(param_values)

        # Build the query dynamically
        param_placeholders = ','.join(['?'] * len(param_tuple))
        query = f"{{CALL {procedure_name}({param_placeholders})}}"

        conn = pyodbc.connect(connectionString)
        cursor = conn.cursor()

        cursor.execute(query, *param_tuple)

        if cursor.description:
            # Fetch rows for SELECT or returning data
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            data = [dict(zip(columns, row)) for row in rows]
            return {"data": data, "message": "Procedure executed successfully"}, 200
        else:
            # Commit for INSERT/UPDATE/DELETE
            conn.commit()
            return {"message": "Procedure executed successfully"}, 201

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

# Route for INSERT
@app.route('/insert_record', methods=['POST'])
def insert_record():
    procedure_name = request.json.get('procedure_name')
    params = request.json.get('params', {})
    if not procedure_name:
        return jsonify({"error": "procedure_name is required"}), 400
    result, status_code = execute_stored_procedure(procedure_name, params)
    return jsonify(result), status_code

# Route for UPDATE
@app.route('/update_record', methods=['PUT'])
def update_record():
    procedure_name = request.json.get('procedure_name')
    params = request.json.get('params', {})
    if not procedure_name:
        return jsonify({"error": "procedure_name is required"}), 400
    result, status_code = execute_stored_procedure(procedure_name, params)
    return jsonify(result), status_code

# Route for DELETE
@app.route('/delete_record', methods=['DELETE'])
def delete_record():
    procedure_name = request.json.get('procedure_name')
    params = request.json.get('params', {})
    if not procedure_name:
        return jsonify({"error": "procedure_name is required"}), 400
    result, status_code = execute_stored_procedure(procedure_name, params)
    return jsonify(result), status_code

# Route for SELECT
@app.route('/read_record', methods=['GET'])
def read_record():
    procedure_name = request.args.get('procedure_name')
    if not procedure_name:
        return jsonify({"error": "procedure_name is required"}), 400

    # Convert query parameters to dictionary
    params = {key: value for key, value in request.args.items() if key != 'procedure_name'}
    result, status_code = execute_stored_procedure(procedure_name, params)
    return jsonify(result), status_code

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
