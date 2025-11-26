#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
api_key = os.getenv('ANTHROPIC_API_KEY')
model = os.getenv('ANTHROPIC_MODEL', 'claude-3-haiku-20240307')

print(f'API Key found: {bool(api_key)}')
print(f'API Key (first 20 chars): {api_key[:20] if api_key else "None"}')
print(f'Model: {model}')

if api_key:
    try:
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=100,
            messages=[{'role': 'user', 'content': 'Say hello'}]
        )
        print(f'✅ API call successful!')
        print(f'Response: {response.content[0].text}')
    except Exception as e:
        print(f'❌ API Error: {type(e).__name__}')
        print(f'Message: {str(e)}')
else:
    print('❌ No API key found')
