import streamlit as st
import boto3
import base64
import json
import os
from datetime import datetime
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError:
    pass  # dotenv not available, use system environment variables

# Initialize AWS clients
bedrock_runtime = boto3.client('bedrock-runtime')
bedrock = boto3.client('bedrock')
rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')

# Configuration from environment variables
ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')
BUCKET_NAME = os.getenv('BUCKET_NAME', f'thisisacatforsureyouknowit-{ENVIRONMENT}')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '1048576'))  # 1MB

def create_guardrail():
    """Create Bedrock Guardrail for content filtering"""
    try:
        # First try to find existing guardrail
        guardrails = bedrock.list_guardrails()
        for guardrail in guardrails['guardrails']:
            if guardrail['name'] == 'cat-validator-guardrail':
                return guardrail['id']
        
        # If not found, create new one
        response = bedrock.create_guardrail(
            name='cat-validator-guardrail',
            description='Content filter for cat image validator',
            contentPolicyConfig={
                'filtersConfig': [
                    {'type': 'SEXUAL', 'inputStrength': 'HIGH', 'outputStrength': 'HIGH'},
                    {'type': 'VIOLENCE', 'inputStrength': 'HIGH', 'outputStrength': 'HIGH'},
                    {'type': 'HATE', 'inputStrength': 'HIGH', 'outputStrength': 'HIGH'},
                    {'type': 'INSULTS', 'inputStrength': 'MEDIUM', 'outputStrength': 'MEDIUM'},
                    {'type': 'MISCONDUCT', 'inputStrength': 'MEDIUM', 'outputStrength': 'MEDIUM'}
                ]
            },
            blockedInputMessaging='This image contains inappropriate content and cannot be processed.',
            blockedOutputsMessaging='Response blocked due to content policy.'
        )
        return response['guardrailId']
    except Exception:
        # If still fails, try with a unique name
        import time
        unique_name = f'cat-validator-guardrail-{int(time.time())}'
        response = bedrock.create_guardrail(
            name=unique_name,
            description='Content filter for cat image validator',
            contentPolicyConfig={
                'filtersConfig': [
                    {'type': 'SEXUAL', 'inputStrength': 'HIGH', 'outputStrength': 'HIGH'},
                    {'type': 'VIOLENCE', 'inputStrength': 'HIGH', 'outputStrength': 'HIGH'},
                    {'type': 'HATE', 'inputStrength': 'HIGH', 'outputStrength': 'HIGH'},
                    {'type': 'INSULTS', 'inputStrength': 'MEDIUM', 'outputStrength': 'MEDIUM'},
                    {'type': 'MISCONDUCT', 'inputStrength': 'MEDIUM', 'outputStrength': 'MEDIUM'}
                ]
            },
            blockedInputMessaging='This image contains inappropriate content and cannot be processed.',
            blockedOutputsMessaging='Response blocked due to content policy.'
        )
        return response['guardrailId']

def validate_cat_image(image_bytes, mime_type="image/jpeg"):
    """Use Amazon Rekognition and Bedrock Nova Lite to validate content and cats"""
    
    # First use Amazon Rekognition for content moderation
    try:
        moderation_response = rekognition.detect_moderation_labels(
            Image={'Bytes': image_bytes},
            MinConfidence=50.0
        )
        
        # Check for inappropriate content
        for label in moderation_response['ModerationLabels']:
            if label['Confidence'] > 50.0:
                label_name = label['Name'].lower()
                if any(term in label_name for term in ['hate', 'nazi', 'explicit', 'suggestive', 'violence', 'graphic']):
                    raise ValueError(f"Image contains inappropriate content: {label['Name']} (confidence: {label['Confidence']:.1f}%)")
    
    except Exception as e:
        if 'inappropriate content' in str(e):
            raise e
        # If Rekognition fails, continue with backup check
        pass
    
    # Backup content check using Claude 3.5 Sonnet
    try:
        image_b64 = base64.b64encode(image_bytes).decode()
        content_check_payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 50,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_b64
                            }
                        },
                        {
                            "type": "text",
                            "text": "IMPORTANT: Does this image contain Nazi symbols, swastikas, hate symbols, pornography, or violence? Be very strict. Answer only 'YES' if inappropriate or 'NO' if safe."
                        }
                    ]
                }
            ]
        }
        
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            body=json.dumps(content_check_payload)
        )
        
        result = json.loads(response['body'].read())
        content_response = result['content'][0]['text'].strip().upper()
        
        if content_response == 'YES':
            raise ValueError("Image contains inappropriate content and was blocked by content filters.")
            
    except Exception as e:
        if 'inappropriate content' in str(e):
            raise e
    
    # If content checks pass, proceed with cat validation using Nova Lite
    # Determine image format from MIME type
    img_format = "jpeg"
    if mime_type == "image/png":
        img_format = "png"
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": img_format,
                            "source": {
                                "bytes": image_b64
                            }
                        }
                    },
                    {
                        "text": "Is there a cat in this image? Answer only 'yes' or 'no'."
                    }
                ]
            }
        ],
        "inferenceConfig": {
            "maxTokens": 10,
            "temperature": 0.0,
            "topP": 1
        }
    }
    
    response = bedrock_runtime.invoke_model(
        modelId='amazon.nova-lite-v1:0',
        body=json.dumps(payload)
    )
    
    result = json.loads(response['body'].read())
    return result['output']['message']['content'][0]['text'].strip().lower() == 'yes'

def upload_to_s3(image_bytes, filename):
    """Upload validated cat image to S3"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    s3_key = f"cats/{timestamp}_{filename}"
    
    # Determine content type based on file extension
    content_type = 'image/jpeg'  # default
    if filename.lower().endswith('.png'):
        content_type = 'image/png'
    
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=image_bytes,
        ContentType=content_type
    )
    return s3_key

# Streamlit UI
st.title("Cat Image Validator")

uploaded_file = st.file_uploader("Upload a cat image", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    # Check file size
    if len(uploaded_file.getvalue()) > MAX_FILE_SIZE:
        st.error("File size exceeds 1MB limit!")
    else:
        try:
            # Display uploaded image
            st.image(uploaded_file, caption="Uploaded Image", width=300)
            
            # Validate with Bedrock
            with st.spinner("Validating if this is a cat..."):
                try:
                    # Determine MIME type
                    content_type = 'image/jpeg'  # default
                    if uploaded_file.name.lower().endswith('.png'):
                        content_type = 'image/png'
                    
                    is_cat = validate_cat_image(uploaded_file.getvalue(), content_type)
                except ValueError as e:
                    st.error(str(e))
                    st.stop()
            
            if is_cat:
                # Upload to S3
                s3_key = upload_to_s3(uploaded_file.getvalue(), uploaded_file.name)
                st.success(f"Cat validated and saved to S3: {s3_key}")
            else:
                st.error("This image does not contain a cat. Please upload a cat image.")
                
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
