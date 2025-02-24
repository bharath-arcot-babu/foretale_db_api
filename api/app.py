from flask import Flask, request, jsonify
from flask_cors import CORS
from database.db_service import DatabaseService
from waitress import serve

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
CORS(app)

# Initialize Database Service
db_service = DatabaseService()

# CRUD Endpoints
@app.route('/insert_record', methods=['POST'])
def insert_record():
    data = request.json
    procedure_name = data.get('procedure_name')
    params = data.get('params', {})

    if not procedure_name:
        return jsonify({"error": "procedure_name is required"}), 400

    result, status_code = db_service.execute_stored_procedure(procedure_name, params, isCommit=True)
    return jsonify(result), status_code


@app.route('/update_record', methods=['PUT'])
def update_record():
    data = request.json
    procedure_name = data.get('procedure_name')
    params = data.get('params', {})

    if not procedure_name:
        return jsonify({"error": "procedure_name is required"}), 400

    result, status_code = db_service.execute_stored_procedure(procedure_name, params, isCommit=True)
    return jsonify(result), status_code


@app.route('/delete_record', methods=['DELETE'])
def delete_record():
    data = request.json
    procedure_name = data.get('procedure_name')
    params = data.get('params', {})

    if not procedure_name:
        return jsonify({"error": "procedure_name is required"}), 400

    result, status_code = db_service.execute_stored_procedure(procedure_name, params, isCommit=True)
    return jsonify(result), status_code


@app.route('/read_record', methods=['GET'])
def read_record():
    procedure_name = request.args.get('procedure_name')

    if not procedure_name:
        return jsonify({"error": "procedure_name is required"}), 400

    params = {key: value for key, value in request.args.items() if key != 'procedure_name'}
    result, status_code = db_service.execute_stored_procedure(procedure_name, params)
    return jsonify(result), status_code


@app.route('/read_json_record', methods=['GET'])
def read_json_record():
    procedure_name = request.args.get('procedure_name')

    if not procedure_name:
        return jsonify({"error": "procedure_name is required"}), 400

    params = {key: value for key, value in request.args.items() if key != 'procedure_name'}
    result, status_code = db_service.execute_stored_procedure(procedure_name, params, isJsonOutput=True)
    return jsonify(result), status_code


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
