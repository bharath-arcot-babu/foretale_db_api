import json
import boto3
import os

ecs_client = boto3.client('ecs', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

def lambda_handler(event, context):
    try:
        body = event.get('body')
        if isinstance(body, str):
            body = json.loads(body)

        cluster = body.get('cluster_name')
        task_arn = body.get('task_arn')

        if not cluster or not task_arn:
            return response_with_cors(400, {'error': 'Missing required parameters: cluster_name or task_arn'})

        response = ecs_client.describe_tasks(cluster=cluster, tasks=[task_arn])
        tasks = response.get('tasks', [])
        if not tasks:
            return response_with_cors(404, {'error': 'Task not found'})

        status = tasks[0]['lastStatus']
        stopped_reason = tasks[0].get('stoppedReason')

        return response_with_cors(200, {
            'taskArn': task_arn,
            'status': status,
            'stoppedReason': stopped_reason
        })

    except Exception as e:
        return response_with_cors(500, {'error': str(e)})

def response_with_cors(status_code, body_dict):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST',
            'Access-Control-Allow-Headers': '*'
        },
        'body': json.dumps(body_dict)
    }
