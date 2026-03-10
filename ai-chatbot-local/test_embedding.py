"""Test script to verify embedding API"""
import requests
import json
from app.config import VERTEX_API_KEY

def test_embedding():
    text = "Hello world"
    model = "text-embedding-004"
    
    # Try Vertex AI format
    url = f"https://aiplatform.googleapis.com/v1/publishers/google/models/{model}:predict?key={VERTEX_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "instances": [
            {
                "content": text
            }
        ]
    }
    
    print(f"Testing Vertex AI embedding API...")
    print(f"URL: {url[:80]}...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nSuccess! Response keys: {data.keys()}")
            print(f"Full response: {json.dumps(data, indent=2)[:1000]}")
        else:
            response.raise_for_status()
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    test_embedding()

