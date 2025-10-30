import streamlit as st
import boto3
import base64
import json
from datetime import datetime

# Initialize AWS clients
bedrock_runtime = boto3.client('bedrock-runtime')
bedrock = boto3.client('bedrock')
s3 = boto3.client('s3')

BUCKET_NAME = 'thisisacatforsureyouknowit'
MAX_FILE_SIZE = 1024 * 1024  # 1MB

def get_or_create_guardrail():
    """Get existing guardrail or create new one"""
    try:
        guardrails = bedrock.list_guardrails()
        for guardrail in guardrails['guardrails']:
            if guardrail['name'] == 'cat-validator-nova':
                return guardrail['id']
        
        response = bedrock.create_guardrail(
            name='cat-validator-nova',
            description='Content filter for Nova cat validator',
            contentPolicyConfig={
                'filtersConfig': [
                    {'type': 'SEXUAL', 'inputStrength': 'HIGH', 'outputStrength': 'HIGH'},
                    {'type': 'VIOLENCE', 'inputStrength': 'HIGH', 'outputStrength': 'HIGH'},
                    {'type': 'HATE', 'inputStrength': 'HIGH', 'outputStrength': 'HIGH'},
                    {'type': 'MISCONDUCT', 'inputStrength': 'MEDIUM', 'outputStrength': 'MEDIUM'}
                ]
            },
            blockedInputMessaging='Image blocked due to inappropriate content.',
            blockedOutputsMessaging='Response blocked by content policy.'
        )
        return response['guardrailId']
    except Exception as e:
        st.error(f"Guardrail error: {e}")
        return None

def validate_cat_with_nova_guardrails(image_bytes):
    """Use Nova + Guardrails for content filtering and cat detection"""
    guardrail_id = get_or_create_guardrail()
    if not guardrail_id:
        raise Exception("Could not create or find guardrail")
    
    image_b64 = base64.b64encode(image_bytes).decode()
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": "jpeg",
                            "source": {"bytes": image_b64}
                        }
                    },
                    {
                        "text": "Is there a cat in this image? Answer only 'yes' or 'no'."
                    }
                ]
            }
        ],
        "inferenceConfig": {
            "maxTokens": 10
        }
    }
    
    response = bedrock_runtime.invoke_model(
        modelId='amazon.nova-lite-v1:0',
        body=json.dumps(payload),
        guardrailIdentifier=guardrail_id,
        guardrailVersion='DRAFT'
    )
    
    result = json.loads(response['body'].read())
    return result['output']['message']['content'][0]['text'].strip().lower() == 'yes'

def upload_to_s3(image_bytes, filename):
    """Upload validated cat image to S3"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    s3_key = f"cats/{timestamp}_{filename}"
    
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=image_bytes,
        ContentType='image/jpeg'
    )
    return s3_key

# Streamlit UI
st.title("Cat Validator - Nova + Guardrails Only")
st.write("Content filtering handled entirely by Bedrock Guardrails with Nova")

uploaded_file = st.file_uploader("Upload a cat image", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    if len(uploaded_file.getvalue()) > MAX_FILE_SIZE:
        st.error("File size exceeds 1MB limit!")
    else:
        st.image(uploaded_file, caption="Uploaded Image", width=300)
        
        with st.spinner("Processing with Nova + Guardrails..."):
            try:
                is_cat = validate_cat_with_nova_guardrails(uploaded_file.getvalue())
                
                if is_cat:
                    s3_key = upload_to_s3(uploaded_file.getvalue(), uploaded_file.name)
                    st.success(f"Cat validated and saved to S3: {s3_key}")
                else:
                    st.error("No cat detected in this image.")
                    
            except Exception as e:
                if 'guardrail' in str(e).lower() or 'blocked' in str(e).lower():
                    st.error("Image blocked by content filters.")
                else:
                    st.error(f"Error: {str(e)}")
