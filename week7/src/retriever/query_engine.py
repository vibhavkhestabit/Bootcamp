import os
import sys

# --- PATH SETUP ---
# Add project root to path so we can import src.embeddings
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
sys.path.append(project_root)

from langchain_community.vectorstores import FAISS
from src.embeddings.embedder import Embedder
from dotenv import load_dotenv

load_dotenv()

# Path to the FAISS index (Same logic as ingest.py)
DB_PATH = os.path.join(current_dir, "../vectorstore/db_faiss")

def test_retrieval():
    # 1. Initialize Embedder
    print("Loading Embedder...")
    embedder = Embedder()
    embeddings = embedder.get_embeddings()

    # 2. Load Vector Database
    print(f"Loading Index from: {DB_PATH}")
    try:
        vectorstore = FAISS.load_local(
            DB_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
    except Exception as e:
        print(f"❌ Error loading index: {e}")
        return

    # 3. Interactive Loop
    print("\n🔎 --- PURE RETRIEVAL MODE (No LLM) ---")
    print("This tool shows you exactly what text chunks are being found for your query.")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("Query: ")
        if query.lower() == "exit":
            break
            
        # 4. Perform Similarity Search
        # k=3 means "Get top 5 chunks"
        results = vectorstore.similarity_search_with_score(query, k=5)
        
        print(f"\n--- Top 5 Results for '{query}' ---")
        for i, (doc, score) in enumerate(results):
            # L2 Distance: Lower score = Better match
            # Cosine Similarity: Higher score = Better match
            print(f"\n[Result {i+1}] (Score: {score:.4f})")
            print(f"Source: {doc.metadata.get('source', 'Unknown')} (Page {doc.metadata.get('page', 'N/A')})")
            print(f"Content: \"{doc.page_content[:200]}...\"") # Show first 200 chars
            print("-" * 50)

if __name__ == "__main__":
    test_retrieval()