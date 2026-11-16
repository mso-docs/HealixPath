#!/usr/bin/env python3
"""Dev-only smoke test: calls the HealixPath model with a token you supply via HF_TOKEN.

The app itself never reads HF_TOKEN; visitors sign in with Hugging Face instead.
"""
import os
from huggingface_hub import InferenceClient

model = os.getenv("HEALIXPATH_MODEL", "openai/gpt-oss-20b")
token = os.getenv("HF_TOKEN")
print(f"Model: {model}")
print(f"HF_TOKEN set: {bool(token)}")

if token:
    try:
        result = InferenceClient(api_key=token).chat_completion(
            model=model,
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=100,
        )
        print("API call successful")
        print(f"Response: {result.choices[0].message.content}")
    except Exception as e:
        print(f"API error: {type(e).__name__}")
        print(f"Message: {e}")
else:
    print("Set HF_TOKEN (needs the 'Make calls to Inference Providers' permission) to run this check.")
