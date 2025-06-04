#!/bin/bash

# Set AWS profile
export AWS_PROFILE=amplify-policy-442426872653

# Set AWS region
export AWS_REGION=us-east-1

# Set ECS configuration
export ECS_CLUSTER_NAME=create-vector-embeddings-v1
export ECS_TASK_DEFINITION=embed-documents-task:1
export SUBNET_IDS=subnet-0e8ee5594a318f699,subnet-0ac5e5f338718b320  # Replace with your subnet IDs
export SECURITY_GROUP_IDS=sg-0d9dc3d6837847754  # Replace with your security group ID

# Set Python path
export PYTHONPATH=$PYTHONPATH:.

# Run the Lambda function
python -m lambda_ecs_invoker.lambda_function 