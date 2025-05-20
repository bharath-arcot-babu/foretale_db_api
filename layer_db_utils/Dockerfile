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
    openssl-devel

# Upgrade pip and setuptools
RUN python3.12 -m pip install --upgrade pip setuptools wheel

# Create layer directory structure
RUN mkdir -p /opt/python/layer_db_utils/services

# Create __init__.py files
RUN touch /opt/python/layer_db_utils/__init__.py
RUN touch /opt/python/layer_db_utils/services/__init__.py

# Copy requirements file
COPY requirements.txt /opt/requirements.txt

# Install Python packages into the layer folder
RUN python3.12 -m pip install --only-binary=:all: -r /opt/requirements.txt -t /opt/python

# Copy Python code
COPY services/ /opt/python/layer_db_utils/services/
COPY config.py /opt/python/layer_db_utils/

# Package the layer zip
RUN cd /opt && zip -r9 layer_db_utils.zip python

# docker build -t layer-db-utils .
# docker run -d --name layer-container layer-db-utils
# docker cp layer-container:/opt/layer_db_utils.zip .
# docker stop layer-container
# docker rm layer-container