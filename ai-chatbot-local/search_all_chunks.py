"""Search all chunks in the vector store for specific text"""
from app.rag import load_vector_store

def search_all_chunks(search_term):
    print(f"Searching all chunks for: '{search_term}'")
    
    vector_store = load_vector_store()
    
    # Get all documents from the vector store
    # Access the internal docstore
    all_docs = list(vector_store.docstore._dict.values())
    
    print(f"\nTotal chunks in vector store: {len(all_docs)}")
    
    # Search for the term
    matches = []
    for i, doc in enumerate(all_docs):
        if search_term.lower() in doc.page_content.lower():
            matches.append((i, doc))
    
    print(f"\nFound {len(matches)} chunks containing '{search_term}'")
    
    for i, (chunk_id, doc) in enumerate(matches):
        print(f"\n{'='*60}")
        print(f"Match {i+1} (Chunk ID: {chunk_id})")
        print('='*60)
        print(doc.page_content)
        print(f"\nMetadata: {doc.metadata}")

if __name__ == "__main__":
    # Search for Business Challenge 5
    search_all_chunks("business challenge 5")
    
    print("\n\n" + "="*60)
    print("Searching for all business challenges...")
    print("="*60)
    
    # Also search for just "challenge" to see all challenges
    vector_store = load_vector_store()
    all_docs = list(vector_store.docstore._dict.values())
    
    challenge_numbers = set()
    for doc in all_docs:
        import re
        matches = re.findall(r'business challenge (\d+)', doc.page_content.lower())
        challenge_numbers.update(matches)
    
    print(f"\nAll Business Challenges found in PDF: {sorted(challenge_numbers)}")

