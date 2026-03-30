"""
AWS Utilities for SPARTAN
"""

import boto3
import json
from typing import Tuple
import streamlit as st
from config.settings import MODELS_BY_OPTIMIZATION


def test_bedrock_connection(region_name: str) -> Tuple[bool, str]:
    """Test connection with enhanced error reporting"""
    try:
        client = boto3.client('bedrock-runtime', region_name=region_name)
    except Exception as e:
        st.error(f"Failed to create AWS client: {e}")
        return False, None
    
    # Try models in priority order (performance first for testing)
    models_to_try = [
        ("anthropic.claude-3-5-sonnet-20241022-v2:0", "Claude 3.5 Sonnet v2"),
        ("anthropic.claude-3-5-sonnet-20240620-v1:0", "Claude 3.5 Sonnet v1"),
        ("anthropic.claude-3-haiku-20240307-v1:0", "Claude 3 Haiku"),
        ("anthropic.claude-3-sonnet-20240229-v1:0", "Claude 3 Sonnet")
    ]
    
    for model_id, model_name in models_to_try:
        if _test_single_model(client, model_id, model_name):
            return True, model_id
    
    st.error("❌ No Claude models are available in this region")
    return False, None


def _test_single_model(client, model_id: str, model_name: str) -> bool:
    """Test a single model"""
    try:
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Test"}]
        })
        
        response = client.invoke_model(
            modelId=model_id,
            body=body
        )
        
        st.success(f"✅ Connection successful with {model_name}")
        return True
        
    except Exception as e:
        st.warning(f"❌ {model_name} not available: {str(e)}")
        return False


def get_available_models(region_name: str, cost_optimization: str) -> list:
    """Get available models based on cost optimization"""
    return MODELS_BY_OPTIMIZATION.get(cost_optimization, MODELS_BY_OPTIMIZATION["balanced"])


def validate_aws_credentials() -> bool:
    """Validate AWS credentials are configured"""
    try:
        # Try to create a session to check credentials
        session = boto3.Session()
        credentials = session.get_credentials()
        return credentials is not None
    except Exception:
        return False


def get_model_display_name(model_id: str) -> str:
    """Get a clean display name for a model"""
    if not model_id:
        return "Unknown Model"
    
    # Extract the model name from the ID
    model_name = model_id.split('.')[-1]
    model_name = model_name.replace('-', ' ').title()
    model_name = model_name.replace('V1', 'v1').replace('V2', 'v2')
    
    return model_name