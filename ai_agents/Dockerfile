FROM amazonlinux:2023

# Install Python 3.12, pip, and required build tools
RUN dnf -y install \
    python3.12 \
    python3.12-pip \
    python3.12-devel \
    gcc \
    gcc-c++ \
    zip \
    unixODBC \
    unixODBC-devel \
    libffi-devel \
    openssl-devel \
    && dnf clean all

# Upgrade pip and setuptools
RUN python3.12 -m pip install --upgrade pip setuptools wheel

# Create application directory structure
RUN mkdir -p /opt/python/ai_agents
RUN mkdir -p /opt/python/layer_llm_service
RUN mkdir -p /opt/python/layer_lambda_utils
RUN mkdir -p /opt/python/tools
RUN mkdir -p /opt/python/models
RUN mkdir -p /opt/python/prompts
RUN mkdir -p /opt/python/template

# Create __init__.py files
RUN touch /opt/python/ai_agents/__init__.py
RUN touch /opt/python/layer_llm_service/__init__.py
RUN touch /opt/python/layer_lambda_utils/__init__.py
RUN touch /opt/python/tools/__init__.py
RUN touch /opt/python/models/__init__.py
RUN touch /opt/python/prompts/__init__.py
RUN touch /opt/python/template/__init__.py

# Copy requirements file
COPY requirements.txt /opt/requirements.txt

# Install Python packages into the application folder
RUN python3.12 -m pip install --only-binary=:all: -r /opt/requirements.txt -t /opt/python

# Copy Python code
COPY layer_llm_service/ /opt/python/layer_llm_service/
COPY layer_lambda_utils/ /opt/python/layer_lambda_utils/
COPY tools/ /opt/python/tools/
COPY models/ /opt/python/models/
COPY prompts/ /opt/python/prompts/
COPY template/ /opt/python/template/
COPY agent.py /opt/python/ai_agents/

# Set environment variables
ENV PYTHONPATH=/opt/python
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["python3.12", "/opt/python/ai_agents/agent.py"]

# Build and run instructions:
# docker build -t ai-agents .
# docker run -d --name ai-agents-container ai-agents
# docker stop ai-agents-container
# docker rm ai-agents-container
#
# ECR push instructions:
    #aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 442426872653.dkr.ecr.us-east-1.amazonaws.com
    #docker build -t test-config-repo .
    #docker tag test-config-repo:latest 442426872653.dkr.ecr.us-east-1.amazonaws.com/test-config-repo:latest
    #docker push 442426872653.dkr.ecr.us-east-1.amazonaws.com/test-config-repo:latest


# aws ecr get-login-password --region us-east-1 --profile amplify-policy-442426872653 | docker login --username AWS --password-stdin 442426872653.dkr.ecr.us-east-1.amazonaws.com && docker build -t test-config-repo . && docker tag test-config-repo:latest 442426872653.dkr.ecr.us-east-1.amazonaws.com/test-config-repo:latest && docker push 442426872653.dkr.ecr.us-east-1.amazonaws.com/test-config-repo:latest