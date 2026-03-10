import requests
import json
import os
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from typing import List

from app.config import VERTEX_API_KEY

DOCS_PATH = "data/docs_data"
VECTOR_STORE_PATH = "data/docs_data/vector_store/faiss_index"

# Custom embeddings class for Gemini API to convert text into vector representations
class GeminiEmbeddings(Embeddings):
    """Custom embeddings using Gemini API with API key"""

    def __init__(self, api_key: str):
        #Initialize the API key for authentication
        self.api_key = api_key
        # Specify which embedding model to use from Vertex AI
        self.model = "text-embedding-004"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        embeddings = []
        total = len(texts)
        for i, text in enumerate(texts, 1):
            print(f"Generating embedding {i}/{total}...", end='\r')
            embedding = self._get_embedding(text)
            embeddings.append(embedding)
        print(f"\n✅ Generated {total} embeddings")
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        return self._get_embedding(text)

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding from Vertex AI Gemini API"""
        # Use Vertex AI embedding endpoint
        url = f"https://aiplatform.googleapis.com/v1/publishers/google/models/{self.model}:predict?key={self.api_key}"

        headers = {"Content-Type": "application/json"}
        payload = {
            "instances": [
                {
                    "content": text
                }
            ]
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            # Extract embedding from Vertex AI response format
            if 'predictions' in data and len(data['predictions']) > 0:
                return data['predictions'][0]['embeddings']['values']
            else:
                print(f"Unexpected response format: {data}")
                return [0.0] * 768
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return a zero vector as fallback
            return [0.0] * 768

def build_vector_store():
    # Load all PDF files from the directory
    pdf_files = glob.glob(os.path.join(DOCS_PATH, "**/*.pdf"), recursive=True)

    docs = []
    for pdf_file in pdf_files:
        print(f"Loading {pdf_file}...")
        loader = PyPDFLoader(pdf_file)
        docs.extend(loader.load())

    print(f"Loaded {len(docs)} pages from {len(pdf_files)} PDF files")

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    print(f"Split into {len(chunks)} chunks")

    embeddings = GeminiEmbeddings(api_key=VERTEX_API_KEY)
    vector_store = FAISS.from_documents(chunks, embeddings)

    vector_store.save_local(VECTOR_STORE_PATH)
    return vector_store

def load_vector_store():
    embeddings = GeminiEmbeddings(api_key=VERTEX_API_KEY)
    return FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
