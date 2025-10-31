#!/bin/bash

# Check if AWS SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "AWS SAM CLI is not installed. Please install it first:"
    echo "pip install aws-sam-cli"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "AWS credentials not configured. Please configure them first:"
    echo "aws configure"
    exit 1
fi

# Set environment
ENV="${1:-dev}"
STACK_NAME="cat-validator-${ENV}"

echo "Deploying Cat Validator infrastructure to ${ENV} environment..."

# Create S3 bucket for SAM artifacts if it doesn't exist
DEPLOYMENT_BUCKET="cat-validator-sam-${ENV}"
if ! aws s3 ls "s3://${DEPLOYMENT_BUCKET}" 2>&1 > /dev/null; then
    echo "Creating S3 bucket for SAM artifacts..."
    aws s3 mb "s3://${DEPLOYMENT_BUCKET}" --region $(aws configure get region)
fi

# Build and deploy using SAM
sam build
sam deploy \
    --template-file .aws-sam/build/template.yaml \
    --stack-name ${STACK_NAME} \
    --s3-bucket ${DEPLOYMENT_BUCKET} \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides Environment=${ENV} \
    --no-confirm-changeset

# Get outputs and create .env file
echo "Deployment complete. Getting stack outputs..."
BUCKET_OUTPUT=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --query 'Stacks[0].Outputs[?OutputKey==`BucketName`].OutputValue' \
    --output text)

# Create .env file
echo "Creating .env file..."
cat > .env << EOF
# AWS Configuration
AWS_REGION=$(aws configure get region)
AWS_PROFILE=default

# Application Configuration
ENVIRONMENT=${ENV}
BUCKET_NAME=${BUCKET_OUTPUT}

# Optional: Content Moderation Settings
MODERATION_CONFIDENCE_THRESHOLD=50.0
MAX_FILE_SIZE=1048576
EOF

echo "Environment file created: .env"
echo "Bucket name: ${BUCKET_OUTPUT}"

# Display all outputs
aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --query 'Stacks[0].Outputs' \
    --output table