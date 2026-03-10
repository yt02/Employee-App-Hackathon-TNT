"""Test script to verify vector store and retrieval"""
import os
from app.rag import load_vector_store
from app.config import VERTEX_API_KEY

def test_retrieval():
    print("Testing vector store retrieval...")
    print(f"API Key loaded: {VERTEX_API_KEY[:20]}..." if VERTEX_API_KEY else "API Key: None")
    
    # Check if vector store files exist
    vector_store_path = "data/docs_data/vector_store/faiss_index"
    print(f"\nChecking vector store path: {vector_store_path}")
    
    if os.path.exists(vector_store_path):
        print("✅ Vector store directory exists")
        files = os.listdir(vector_store_path)
        print(f"Files in vector store: {files}")
    else:
        print("❌ Vector store directory does NOT exist")
        return
    
    # Try to load vector store
    print("\nLoading vector store...")
    try:
        vector_store = load_vector_store()
        print("✅ Vector store loaded successfully")
        
        # Test retrieval with multiple queries
        queries = [
            "business challenge 5",
            "challenge 5",
            "what are all the business challenges"
        ]

        for query in queries:
            print(f"\n{'='*60}")
            print(f"Testing retrieval with query: '{query}'")
            print('='*60)

            retriever = vector_store.as_retriever(search_kwargs={"k": 5})
            docs = retriever.invoke(query)

            print(f"\n✅ Retrieved {len(docs)} documents")

            for i, doc in enumerate(docs):
                print(f"\n--- Document {i+1} ---")
                print(f"Content: {doc.page_content[:400]}...")
                print(f"Metadata: {doc.metadata}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_retrieval()

