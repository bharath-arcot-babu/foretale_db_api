import json
import boto3
import logging
from config import Config

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize ECS client
ecs_client = boto3.client('ecs', region_name=Config.AWS_REGION)

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST,OPTIONS",
    "Access-Control-Allow-Headers": "*"
}

def run_ecs_task(cluster_name, task_definition, container_name, command_args):
    """
    Runs an ECS Fargate task using static subnet and security group config.
    """
    logger.info("Running ECS task with command: %s", command_args)

    response = ecs_client.run_task(
        cluster=cluster_name,
        taskDefinition=task_definition,
        launchType='FARGATE',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': Config.SUBNET_IDS,
                'securityGroups': Config.SECURITY_GROUP_IDS,
                'assignPublicIp': 'ENABLED'
            }
        },
        overrides={
            'containerOverrides': [{
                'name': container_name,
                'command': command_args
            }]
        }
    )

    task_arn = response['tasks'][0]['taskArn']
    task_status = response['tasks'][0]['lastStatus']

    logger.info(f"ECS task started: ARN={task_arn}, Status={task_status}")
    return task_arn, task_status

def lambda_handler(event, context):
    """
    Generic Lambda to invoke ECS tasks for any container command.
    
    Expected event format:
    {
        "action": "run_task",
        "command": ["python3.12", "/opt/python/embed_documents/app.py", "123", "456"],
        "cluster_name": "my-cluster",
        "task_definition": "my-task-def",
        "container_name": "my-container"
    }
    """
    try:
        body = event.get('body')
        if isinstance(body, str):
            body = json.loads(body)
        elif not isinstance(body, dict):
            body = {}

        action = body.get('action')
        command = body.get('command')
        cluster_name = body.get('cluster_name')
        task_definition = body.get('task_definition')
        container_name = body.get('container_name')

        # Validate input
        if action != "run_task":
            raise ValueError("Unsupported or missing action. Use 'run_task'.")
        if not all([command, cluster_name, task_definition, container_name]):
            raise ValueError("Missing one or more required parameters: command, cluster_name, task_definition, container_name.")
        if not isinstance(command, list):
            raise ValueError("'command' must be a list of strings.")

        # Run ECS task
        task_arn, task_status = run_ecs_task(cluster_name, task_definition, container_name, command)

        return {
            'statusCode': 200,
            "headers": CORS_HEADERS,
            'body': json.dumps({
                'message': 'ECS task started successfully',
                'taskArn': task_arn,
                'status': task_status
            })
        }

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return {
            'statusCode': 400,
            "headers": CORS_HEADERS,
            'body': json.dumps({'error': str(ve)})
        }
    except Exception as e:
        logger.error(f"Error invoking ECS task: {str(e)}")
        return {
            'statusCode': 500,
            "headers": CORS_HEADERS,
            'body': json.dumps({'error': f"Failed to start ECS task: {str(e)}"})
        }
