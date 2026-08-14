import os
import sys
from aia_auth import auth
import jwt

# Allow the script to find the `helper` package at the repo root
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import helper.auth_utils as auth_utils

settings = auth_utils.get_auth_settings(os.path.join(repo_root, '.env'))
print(auth_utils.describe_auth(settings))

# Optional validation when not using SSO
auth_utils.ensure_credentials_if_needed(settings)

import json


from openai import OpenAI
from helper.auth_utils import build_default_headers, build_http_client

import helper.auth_utils as auth_utils




default_headers = build_default_headers(settings)
http_client= build_http_client(settings)

base_url = os.environ.get("BASE_URL")

    
client = OpenAI(
    base_url=base_url,
    http_client=http_client,
    api_key='not-empty',  # This is replaced with the token generation based on the authentication provider, but cannot be left blank due to a check in the OpenAI client
    default_headers=default_headers
)

streaming = False # To enable streaming, set streaming to True
available_models = ["gpt-oss-120b", "gpt-oss-20b", "llama-3-3-70b-instruct"]
selected_model = available_models[0]
print(f"Model: {selected_model}")

completion = client.chat.completions.create(
    model=selected_model,
    messages = [
            {"role": "user", "content": "What is your favourite condiment?"},
            {"role": "assistant", "content": "Well, I'm quite partial to a good squeeze of fresh lemon juice. It adds just the right amount of zesty flavour to whatever I'm cooking up in the kitchen!"},
            {"role": "user", "content": "Do you have mayonnaise recipes?"}
        ],
    stream=streaming
)

if streaming:
    for chunk in completion:
        if chunk.id:
            if chunk.choices[0].delta.content == None and chunk.choices[0].delta.role != None:
                print(chunk.choices[0].delta.role+': ', end='')
            elif chunk.choices[0].delta.content != None:
                print(chunk.choices[0].delta.content, end='')
else:
    print(completion.choices[0].message.role + ': ' + completion.choices[0].message.content)