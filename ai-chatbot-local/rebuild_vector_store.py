"""
Script to rebuild the vector store from PDF documents.
Run this script whenever you add new PDF files to the data/docs_data folder.
"""

from app.rag import build_vector_store

if __name__ == "__main__":
    print("Starting to rebuild vector store from PDF documents...")
    print("This may take a few minutes depending on the number and size of PDFs...")
    
    try:
        vector_store = build_vector_store()
        print("\n✅ Vector store rebuilt successfully!")
        print("Your chatbot can now answer questions based on your PDF documents.")
        print("\nYou can now start the server with:")
        print("  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"\n❌ Error rebuilding vector store: {e}")
        print("\nPlease make sure:")
        print("1. PDF files are in the 'data/docs_data' folder")
        print("2. Your VERTEX_API_KEY is set correctly in the .env file")

