import os

def check_api_key():
    """Check if OpenAI API key is available in environment variables"""
    api_key = os.getenv("OPENAI_API_KEY")
    return api_key is not None and api_key != ""
