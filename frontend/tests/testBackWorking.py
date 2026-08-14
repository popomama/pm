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


# if not settings.use_sso:
#     token = auth.client_credentials(settings.client_id, settings.client_secret).token
#     required_scopes = ['aia-gateway.genai.dev', 'aia-gateway.genai.prod']

#     try:
#         # Decode without verifying signature
#         decoded = jwt.decode(token, options={"verify_signature": False})

#         # If the token contains scopes/roles/permissions
#         scopes = decoded.get("scope") or decoded.get("scopes") or decoded.get("roles") or decoded.get("permissions")
#         if scopes:
#             print("\n=== TOKEN SCOPES ===")

#             if isinstance(scopes, str):
#                 scopes = scopes.split()

#             for s in scopes:
#                 print(s)

#             has_required = any(rs in scopes for rs in required_scopes)
#             if not has_required:
#                 print(
#                     "\nWARNING -- The Client ID does not contain the required scope to run the GenAI models."
#                     "\nPlease, request at least one of: 'aia-gateway.genai.dev', 'aia-gateway.genai.prod' through the Gateway form."
#                     "\nRefer to https://confluence.dell.com/spaces/AIA/pages/1147207952/Request+the+Dev+GenAI+Offering"
#                 )

#     except Exception as e:
#         print("Error decoding token:", str(e))

# import helper.cert_utils as cert_utils
# # Optional: only run if your environment needs Dell PKI roots appended to certifi.
# # This keeps the notebook lightweight by delegating the logic to a reusable module.
# cert_utils.update_dell_certificates()

# print("Dell certificate utilities loaded (no certificates appended by default)." )

import json
#import jwt

from openai import OpenAI
from helper.auth_utils import build_default_headers, build_http_client

import helper.auth_utils as auth_utils

# settings = auth_utils.get_auth_settings('.env')
# print(auth_utils.describe_auth(settings))

# # Optional validation when not using SSO
# auth_utils.ensure_credentials_if_needed(settings)


default_headers = build_default_headers(settings)
http_client= build_http_client(settings)

base_url = os.environ.get("BASE_URL")
base_url='https://aia.gateway.dell.com/genai/dev/v1'
    
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