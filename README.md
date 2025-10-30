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
- Required Python packages:
  - streamlit
  - boto3

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

## AWS Resources Used

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

## Security Features

- Content moderation filters for:
  - Inappropriate content
  - Hate symbols
  - Violence
  - Adult content
  - Misconduct
- File size restrictions
- Supported file type validation

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