# ECS Task Invoker Lambda Function

This Lambda function invokes an ECS task for document embedding processing.

## Setup

1. Create a ZIP package:
```bash
pip install -r requirements.txt -t ./package
cp lambda_function.py ./package/
cd package
zip -r ../lambda_function.zip .
```

2. Deploy to AWS Lambda:
   - Runtime: Python 3.12
   - Handler: lambda_function.lambda_handler
   - Memory: 128 MB
   - Timeout: 30 seconds

3. Configure Environment Variables:
   - `ECS_CLUSTER_NAME`: Your ECS cluster name
   - `ECS_TASK_DEFINITION`: Your task definition ARN
   - `SUBNET_IDS`: Comma-separated subnet IDs
   - `SECURITY_GROUP_IDS`: Comma-separated security group IDs

4. IAM Role Permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecs:RunTask",
                "ecs:DescribeTasks"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:PassRole"
            ],
            "Resource": [
                "arn:aws:iam::442426872653:role/ecsTaskExecutionRole",
                "arn:aws:iam::442426872653:role/iam-role-ecs-tasks"
            ]
        }
    ]
}
```

## Usage

Invoke the Lambda function with:
```json
{
    "response_id": "123",
    "user_id": "456"
}
```

## Response Format

Success:
```json
{
    "statusCode": 200,
    "body": {
        "message": "ECS task started successfully",
        "taskArn": "arn:aws:ecs:...",
        "status": "RUNNING"
    }
}
```

Error:
```json
{
    "statusCode": 400/500,
    "body": {
        "error": "Error message"
    }
}
``` 