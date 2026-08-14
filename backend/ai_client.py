import os
from openai import OpenAI

import sys
from pathlib import Path
from typing import Optional

repo_root = Path(__file__).parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import helper.auth_utils as auth_utils

env_path = repo_root / '.env'
settings = auth_utils.get_auth_settings(str(env_path))

auth_utils.ensure_credentials_if_needed(settings)

default_headers = auth_utils.build_default_headers(settings)
http_client = auth_utils.build_http_client(settings)

base_url = os.environ.get("BASE_URL")
if not base_url:
    raise ValueError(
        "BASE_URL environment variable is required. Set it in your .env file.\n"
        "Examples:\n"
        "  - OpenAI: https://api.openai.com/v1\n"
        "  - Local Ollama: http://localhost:11434/v1\n"
        "  - Azure OpenAI: https://your-resource.openai.azure.com/"
    )

client = OpenAI(
    base_url=base_url,
    http_client=http_client,
    api_key='not-empty',
    default_headers=default_headers
)


# Generic AI Client Configuration

# For OpenAI
# client = OpenAI(
#     api_key=os.environ.get("OPENAI_API_KEY")
# )
 
# For local Ollama
# client = OpenAI(
#     base_url="http://localhost:11434/v1",
#     api_key="not-needed"
# )
 
# For Azure OpenAI
# client = OpenAI(
#     base_url="https://your-resource.openai.azure.com/",
#     api_key=os.environ.get("AZURE_OPENAI_KEY")
# )

MODEL = "gpt-oss-120b"

def chat_completion(messages: list, stream: bool = False):
    """
    Send a chat completion request to the AI model.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        stream: Whether to stream the response
        
    Returns:
        Completion response from the AI model
    """
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=stream
    )

def simple_query(question: str) -> str:
    """
    Send a simple question to the AI and get a text response.
    
    Args:
        question: The question to ask
        
    Returns:
        The AI's response as a string
    """
    messages = [{"role": "user", "content": question}]
    completion = chat_completion(messages, stream=False)
    return completion.choices[0].message.content
