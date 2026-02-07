# Cat Image Validator

A production-ready Streamlit web application that validates uploaded images for cat content while enforcing comprehensive content safety policies. Built with AWS Bedrock, Rekognition, and S3.

## Features

- **Multi-format Support**: JPG, JPEG, PNG image uploads
- **Content Safety**: Multi-layered moderation using AWS Rekognition and Claude 3.5 Sonnet
- **AI-Powered Detection**: Cat identification using Amazon Bedrock Nova Lite
- **Automated Storage**: Validated images stored in S3 with timestamp organization
- **Security First**: File size validation, content filtering, and secure S3 configuration

## Quick Start

### Prerequisites

- Python 3.9 or higher
- AWS Account with access to:
  - Amazon Bedrock (Nova Lite, Claude 3.5 Sonnet)
  - Amazon Rekognition
  - Amazon S3
- AWS CLI configured with appropriate credentials

### Installation & Deployment

1. **Clone the repository**
```bash
git clone https://github.com/gregwiedeman/cat_validator_hate_guard.git
cd cat_validator_hate_guard
```

2. **Deploy AWS infrastructure**
```bash
bash deploy.sh dev
```
The deployment script automatically:
- Creates required S3 buckets
- Configures IAM roles
- Generates `.env` file with deployment outputs

3. **Install Python dependencies**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **Run the application**
```bash
streamlit run cat_validator.py
```

The application will open in your default browser at `http://localhost:8501`

## Architecture

### Application Versions

This repository includes two implementation variants:

| Version | File | Use Case |
|---------|------|----------|
| **Full** | `cat_validator.py` | Production deployments requiring maximum accuracy |
| **Simplified** | `cat_validator_nova_only.py` | Development or cost-optimized deployments |

#### Full Version (`cat_validator.py`)
- **Multi-layered Content Moderation**:
  1. Amazon Rekognition for initial screening
  2. Claude 3.5 Sonnet for backup validation
  3. Nova Lite for cat detection
- **Best for**: Production environments requiring highest accuracy
- **Trade-off**: Higher API costs, more robust filtering

#### Simplified Version (`cat_validator_nova_only.py`)
- **Single-layer Moderation**: Nova with Bedrock Guardrails
- **Best for**: Development, testing, or cost-sensitive deployments
- **Trade-off**: Lower costs, simpler architecture

### Processing Flow

```
Image Upload → Size Validation → Content Moderation → Cat Detection → S3 Storage
                    ↓                    ↓                  ↓             ↓
                 Max 1MB            Rekognition/        Nova Lite    Timestamped
                                   Claude/Guardrails                  Storage
```

## AWS Infrastructure

### Resources Created

The deployment automatically provisions:

- **S3 Buckets**
  - `thisisacatforsureyouknowit-{env}` - Cat image storage
  - `thisisacatforsureyouknowit-logs-{env}` - Access logs
  - Features: Versioning, lifecycle policies (30-day retention), public access blocked

- **IAM Role**
  - Scoped permissions for Bedrock, Rekognition, and S3
  - Follows principle of least privilege

- **Bedrock Models**
  - Nova Lite (cat detection)
  - Claude 3.5 Sonnet (content moderation)
  - Bedrock Guardrails (content filtering)

### Deployment Options

```bash
# Development environment
bash deploy.sh dev

# Production environment
bash deploy.sh prod
```

### Environment Variables

Auto-generated in `.env` after deployment:

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_REGION` | AWS region | `us-east-1` |
| `ENVIRONMENT` | Deployment environment | `dev` or `prod` |
| `BUCKET_NAME` | S3 bucket for images | `thisisacatforsureyouknowit-dev` |
| `MAX_FILE_SIZE` | Upload size limit (bytes) | `1048576` (1MB) |
| `MODERATION_CONFIDENCE_THRESHOLD` | Content filter sensitivity | `50.0` |

## Security

### Content Filtering

Multi-layered protection against inappropriate content:
- Hate symbols and extremist content
- Violence and graphic imagery
- Adult/NSFW content
- Harassment and misconduct

### Infrastructure Security

- **S3 Buckets**: Public access blocked, versioning enabled
- **Access Logging**: Comprehensive audit trail
- **IAM**: Least-privilege role-based access
- **Data Lifecycle**: Automatic 30-day retention policy

## Cleanup

To avoid ongoing AWS charges, delete all resources after testing:

```bash
# 1. Empty S3 buckets
aws s3 rm s3://thisisacatforsureyouknowit-dev --recursive
aws s3 rm s3://thisisacatforsureyouknowit-logs-dev --recursive

# 2. Delete CloudFormation stack
aws cloudformation delete-stack --stack-name cat-validator-dev

# 3. Delete SAM deployment bucket (optional)
aws s3 rb s3://cat-validator-sam-dev --force
```

Replace `dev` with `prod` if you deployed to production.

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Bucket already exists** | Run cleanup commands, then redeploy |
| **Python version error** | Use Python 3.9-3.11 (3.14+ has compatibility issues) |
| **AWS credentials not found** | Run `aws configure` with valid credentials |
| **Bedrock access denied** | Request model access in AWS Console → Bedrock → Model access |
| **Import errors** | Ensure virtual environment is activated and dependencies installed |

### Validation Test

```bash
# Quick deployment test
bash deploy.sh dev
streamlit run cat_validator.py

# Verify in browser at http://localhost:8501
# Upload a test cat image

# Cleanup
aws cloudformation delete-stack --stack-name cat-validator-dev
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | >=1.28.0,<1.29.0 | Web interface |
| boto3 | >=1.29.2 | AWS SDK |
| python-dotenv | 1.0.0 | Environment management |
| Pillow | 10.4.0 | Image processing |
| urllib3 | 2.5.0 | HTTP client |
| cfn-lint | 1.40.3 | CloudFormation validation |

## Project Structure

```
cat_validator_hate_guard/
├── cat_validator.py              # Full version (Rekognition + Claude + Nova)
├── cat_validator_nova_only.py    # Simplified version (Nova + Guardrails)
├── template.yaml                 # AWS SAM infrastructure template
├── deploy.sh                     # Automated deployment script
├── requirements.txt              # Python dependencies
├── .env.template                 # Environment variable template
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## Contributing

This is a demonstration project. For production use:
1. Add comprehensive error handling
2. Implement rate limiting
3. Add user authentication
4. Configure CloudWatch monitoring
5. Set up CI/CD pipeline

## License

This project is provided as-is for educational and demonstration purposes.