import os
import json
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

AZURE_CONNECTION_STRING = os.environ.get("AZURE_CONNECTION_STRING")

def test_inference():
    print("Testing Azure AI Project Inference (Stateless)...")
    try:
        client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=AZURE_CONNECTION_STRING,
        )
        
        inference_client = client.inference.get_chat_completions_client()
        
        response = inference_client.complete(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a specialized router. Respond with only one word: LEAVE, ROOM, IT, HR, VISITOR, SHUTTLE, TRAINING, WELLNESS, or UNKNOWN."},
                {"role": "user", "content": "I want to join yoga"}
            ]
        )
        print(f"Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"Inference failed: {e}")
        if 'inference_client' in locals():
            print(f"Available attributes on inference_client: {dir(inference_client)}")
        return False

if __name__ == "__main__":
    test_inference()
