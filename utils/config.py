import os
import streamlit as st

def check_api_key():
    """Check if OpenAI API key is set and valid."""
    api_key = os.getenv("OPENAI_API_KEY", "") or st.session_state.get('openai_api_key', "")
    return bool(api_key.strip())
