# Use the AWS Lambda Python 3.12 image
FROM public.ecr.aws/lambda/python:3.12

# Install the necessary tools (like zip) and libraries
RUN dnf install -y zip

# Copy the requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all Lambda function code and necessary files
COPY . ${LAMBDA_TASK_ROOT}

# Zip everything into /tmp/lambda_function.zip
RUN zip -r /tmp/lambda_function.zip ${LAMBDA_TASK_ROOT}/*

# Set the Lambda handler. This is the entry point Lambda will use.
# 'lambda_function.handler' refers to the handler method in lambda_function.py
CMD ["lambda_function.handler"]

# run below commands to build the docker image
# docker build -t lambda-zip .
# docker run --rm -v $(pwd):/mnt lambda-zip
# docker cp 5259deffa0fe:/tmp/lambda_function.zip ./lambda_function.zip


