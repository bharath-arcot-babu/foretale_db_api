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
RUN mkdir -p /opt/python/embed_documents
RUN mkdir -p /opt/python/layer_file_utils/utils/doc_processing
RUN mkdir -p /opt/python/layer_file_utils/utils/txt_processing
RUN mkdir -p /opt/python/layer_lambda_utils
RUN mkdir -p /opt/python/layer_s3_utils/services

# Create __init__.py files
RUN touch /opt/python/embed_documents/__init__.py
RUN touch /opt/python/layer_file_utils/__init__.py
RUN touch /opt/python/layer_file_utils/utils/__init__.py
RUN touch /opt/python/layer_file_utils/utils/doc_processing/__init__.py
RUN touch /opt/python/layer_file_utils/utils/txt_processing/__init__.py
RUN touch /opt/python/layer_lambda_utils/__init__.py
RUN touch /opt/python/layer_s3_utils/__init__.py
RUN touch /opt/python/layer_s3_utils/services/__init__.py

# Copy requirements file
COPY requirements.txt /opt/requirements.txt

# Install Python packages into the application folder
RUN python3.12 -m pip install --only-binary=:all: -r /opt/requirements.txt -t /opt/python

# Copy Python code
COPY layer_file_utils/ /opt/python/layer_file_utils/
COPY layer_file_utils/utils/doc_processing/ /opt/python/layer_file_utils/utils/doc_processing/
COPY layer_file_utils/utils/txt_processing/ /opt/python/layer_file_utils/utils/txt_processing/
COPY layer_lambda_utils/ /opt/python/layer_lambda_utils/
COPY layer_s3_utils/ /opt/python/layer_s3_utils/
COPY config.py /opt/python/embed_documents/
COPY app.py /opt/python/embed_documents/

# Set environment variables
ENV PYTHONPATH=/opt/python
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["python3.12", "/opt/python/embed_documents/app.py"]

# cp -r ../layer_s3_utils .
# cp -r ../layer_lambda_utils .
# cp -r ../layer_file_utils .
# docker build -t embed-documents .
# docker run -d --name embed-container embed-documents
# docker stop embed-container
# docker rm embed-container
#
# aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 442426872653.dkr.ecr.us-east-1.amazonaws.com && \
# docker build -t embed-documents . && \
# docker tag embed-documents:latest 442426872653.dkr.ecr.us-east-1.amazonaws.com/embed-documents:latest && \
# docker push 442426872653.dkr.ecr.us-east-1.amazonaws.com/embed-documents:latest