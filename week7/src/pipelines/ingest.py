import os
import sys
import glob
import json
from datetime import datetime
from dotenv import load_dotenv

# --- PATH SETUP ---
# Ensures the project root is in the system path so we can import src.embeddings
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
sys.path.append(project_root)

from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

# Import our custom modules
from src.embeddings.embedder import Embedder

load_dotenv()

# --- CONFIGURATION PATHS ---
# Based on your structure: data is inside src/
DATA_PATH = os.path.join(current_dir, "../data/raw")
CHUNKS_EXPORT_PATH = os.path.join(current_dir, "../data/chunks")
DB_PATH = os.path.join(current_dir, "../vectorstore/db_faiss")

def load_documents():
    """Loads PDFs, TXT, and CSVs from the data directory."""
    documents = []
    abs_data_path = os.path.abspath(DATA_PATH)
    print(f"Searching for documents in: {abs_data_path}")

    # Process PDFs
    pdf_files = [f for f in glob.glob(f"{DATA_PATH}/*") if f.lower().endswith('.pdf')]
    for file in pdf_files:
        print(f"Loading {file}...")
        try:
            loader = PyPDFLoader(file)
            documents.extend(loader.load())
        except Exception as e:
            print(f"Error loading {file}: {e}")

    # Process TXT
    txt_files = [f for f in glob.glob(f"{DATA_PATH}/*") if f.lower().endswith('.txt')]
    for file in txt_files:
        print(f"Loading {file}...")
        try:
            loader = TextLoader(file)
            documents.extend(loader.load())
        except Exception as e:
            print(f"Error loading {file}: {e}")

    # Process CSV
    csv_files = [f for f in glob.glob(f"{DATA_PATH}/*") if f.lower().endswith('.csv')]
    for file in csv_files:
        print(f"Loading {file}...")
        try:
            loader = CSVLoader(file)
            documents.extend(loader.load())
        except Exception as e:
            print(f"Error loading {file}: {e}")
        
    return documents

def save_chunks_to_disk(chunks):
    """Saves chunks as a JSON file for inspection/debugging as per Day 1 requirements."""
    if not os.path.exists(CHUNKS_EXPORT_PATH):
        os.makedirs(CHUNKS_EXPORT_PATH)
    
    chunk_data = [
        {
            "page_content": chunk.page_content,
            "metadata": chunk.metadata
        }
        for chunk in chunks
    ]
    
    file_path = os.path.join(CHUNKS_EXPORT_PATH, "processed_chunks.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(chunk_data, f, indent=4)
    
    print(f"✅ Exported {len(chunks)} chunks to {file_path}")

def ingest():
    print(f"\n--- Starting Ingestion Process ---")
    
    # 1. Load Data
    raw_docs = load_documents()
    if not raw_docs:
        print("❌ No documents found! Please check the path and file permissions.")
        return

    print(f"✅ Loaded {len(raw_docs)} document pages.")

    # 2. Chunking
    chunk_size = int(os.getenv("CHUNK_SIZE", 500))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 50))
    
    print(f"Splitting text (Size: {chunk_size}, Overlap: {chunk_overlap})...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(raw_docs)

    # 3. Metadata Tagging (Day 1 Requirement)
    for chunk in chunks:
        chunk.metadata["category"] = "Enterprise Knowledge"
        chunk.metadata["ingestion_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Ensure source path is clean
        if "source" in chunk.metadata:
            chunk.metadata["filename"] = os.path.basename(chunk.metadata["source"])

    print(f"✅ Split into {len(chunks)} chunks with metadata tags.")

    # 4. Export Chunks for Inspection
    save_chunks_to_disk(chunks)

    # 5. Generate Local Embeddings
    print("Initializing Embedding Model...")
    embedder = Embedder()
    embeddings = embedder.get_embeddings()

    # 6. Store Vectors in FAISS
    print(f"Creating FAISS Index at {DB_PATH}...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    vectorstore.save_local(DB_PATH)
    print(f"✅ Ingestion Complete. Index saved successfully.")

if __name__ == "__main__":
    ingest()