import os
import requests

# Test OpenRouter API
def test_openrouter():
    api_key = "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"
    model = "qwen/qwen3-235b-a22b-2507"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Hello! Can you tell me about career development?"}
        ],
        "max_tokens": 100
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("API Test Successful!")
            print(f"Response: {result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')}")
        else:
            print(f"API Error: {response.text}")
            
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_openrouter()