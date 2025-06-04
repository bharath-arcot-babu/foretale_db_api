import os

class Config:
    # ECS Configuration
    CLUSTER_NAME = os.getenv('CLUSTER_NAME')
    TASK_DEFINITION = os.getenv('TASK_DEFINITION')
    CONTAINER_NAME = os.getenv('CONTAINER_NAME')
    SUBNET_IDS = os.getenv('SUBNET_IDS', 'subnet-0e8ee5594a318f699,subnet-0ac5e5f338718b320').split(',')
    SECURITY_GROUP_IDS = os.getenv('SECURITY_GROUP_IDS', 'sg-0d9dc3d6837847754').split(',')
    
    # AWS Configuration
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
