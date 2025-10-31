# Cat Image Validator

A Streamlit-based web application that validates whether an uploaded image contains a cat while ensuring content safety. The application uses AWS services including Amazon Bedrock and S3 for image processing and storage.

## Overview

This repository contains two versions of the Cat Image Validator:

1. `cat_validator.py` - Full version with dual content moderation (Rekognition + Claude)
2. `cat_validator_nova_only.py` - Simplified version using only Nova with Bedrock Guardrails

## Features

- Image upload support (JPG, JPEG, PNG)
- File size validation (max 1MB)
- Content moderation and safety checks
- Cat detection using AWS Bedrock Nova
- Automatic S3 storage for validated cat images

## Requirements

- Python 3.x
- AWS account with access to:
  - Amazon Bedrock
  - Amazon Rekognition (full version only)
  - Amazon S3

### Installation

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

The requirements.txt file includes:
- streamlit>=1.28.0,<1.29.0 - for the web interface (Python 3.9+ compatible)
- boto3>=1.29.2 - for AWS services integration
- python-dotenv==1.0.0 - for environment variables
- Pillow==10.4.0 - for image processing (updated for security)
- urllib3==2.5.0 - HTTP library (updated for security)
- cfn-lint==1.40.3 - for CloudFormation template validation

## Version Differences

### Full Version (`cat_validator.py`)
- Uses a multi-layered approach for content moderation:
  1. Amazon Rekognition for initial content screening
  2. Claude 3.5 Sonnet as a backup content validator
  3. Nova Lite for cat detection
- More robust content filtering
- Higher accuracy in inappropriate content detection

### Nova-Only Version (`cat_validator_nova_only.py`)
- Streamlined implementation using only Nova with Bedrock Guardrails
- Simpler architecture with fewer API calls
- Relies entirely on Bedrock Guardrails for content moderation

## How It Works

1. **Image Upload**
   - User uploads an image through the Streamlit interface
   - System validates file size (must be under 1MB)

2. **Content Moderation**
   - **Full Version**: 
     - Checks image using Rekognition's moderation labels
     - If needed, performs backup check with Claude 3.5
   - **Nova Version**: 
     - Uses Bedrock Guardrails for content filtering

3. **Cat Detection**
   - Uses Amazon Bedrock Nova Lite model
   - Analyzes image to determine if a cat is present
   - Returns simple yes/no response

4. **Storage**
   - If image passes all checks and contains a cat:
     - Uploads to S3 bucket with timestamp
     - Returns success message with S3 key
   - If validation fails:
     - Returns appropriate error message

## Error Handling

- Inappropriate content detection
- File size limits
- Invalid file types
- API failures
- Content moderation failures

## Infrastructure Setup

The application uses AWS SAM (Serverless Application Model) for infrastructure deployment. The following resources are created:

### AWS Resources Used

- **Amazon Bedrock**
  - Nova Lite model for cat detection
  - Claude 3.5 Sonnet for backup content moderation (full version)
  - Bedrock Guardrails for content filtering

- **Amazon Rekognition** (full version only)
  - Content moderation labels
  - Inappropriate content detection

- **Amazon S3**
  - Storage for validated cat images
  - Organized with timestamp-based keys

### Infrastructure Deployment

1. Install AWS SAM CLI:
```bash
pip install aws-sam-cli
```

2. Configure AWS credentials:
```bash
aws configure
```

3. Deploy the infrastructure:
```bash
chmod +x deploy.sh
bash deploy.sh [environment]  # environment can be 'dev' or 'prod', defaults to 'dev'
```

4. The deployment script automatically creates a .env file with the correct values from SAM outputs

### Environment Configuration

The application uses environment variables for configuration:
- `ENVIRONMENT` - Deployment environment (dev/prod)
- `BUCKET_NAME` - S3 bucket name for storing cat images
- `AWS_REGION` - AWS region for services
- `MAX_FILE_SIZE` - Maximum file size in bytes (default: 1MB)
- `MODERATION_CONFIDENCE_THRESHOLD` - Content moderation sensitivity

### Cleaning Up Resources

When you're done using the application, you can clean up all AWS resources to avoid incurring charges:

1. Delete all images from the S3 bucket:
```bash
aws s3 rm s3://thisisacatforsureyouknowit-[environment] --recursive
```

2. Delete the AWS CloudFormation stack:
```bash
aws cloudformation delete-stack --stack-name cat-validator-[environment]
```

Replace `[environment]` with either 'dev' or 'prod' depending on your deployment.

### Infrastructure Files

- `template.yaml` - AWS SAM template defining all required resources
- `deploy.sh` - Deployment script for the infrastructure
- `.env.template` - Template for application environment variables

## Security Features

- Content moderation filters for:
  - Inappropriate content
  - Hate symbols
  - Violence
  - Adult content
  - Misconduct
- File size restrictions
- Supported file type validation
- S3 buckets with:
  - Public access blocked
  - Versioning enabled
  - Access logging enabled
  - 30-day lifecycle policy for old images
  - Separate logging bucket for audit trails

## Usage

1. Run the desired version of the application:
   ```bash
   streamlit run cat_validator.py
   # or
   streamlit run cat_validator_nova_only.py
   ```

2. Access the web interface through your browser

3. Upload an image using the file upload widget

4. Wait for validation results

5. If successful, receive S3 storage confirmation

## Troubleshooting

### Common Issues

1. **Bucket name conflicts**: If deployment fails due to existing bucket names, the buckets may already exist from a previous deployment. Clean up existing resources first.

2. **Python version compatibility**: Ensure you're using Python 3.9+ for compatibility with all dependencies.

3. **AWS credentials**: Verify AWS credentials are configured with sufficient permissions for Bedrock, S3, and Rekognition.

4. **Import errors**: If `dotenv` import fails, the application will fall back to system environment variables.

### Testing Deployment

To test the deployment process:
```bash
# Deploy
bash deploy.sh dev

# Test the application
streamlit run cat_validator.py

# Clean up
aws cloudformation delete-stack --stack-name cat-validator-dev
```