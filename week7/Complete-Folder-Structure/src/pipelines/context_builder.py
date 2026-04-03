import sys
import os

# Ensure Python can find your 'src' modules when running directly
sys.path.append(os.path.abspath("src"))

from langchain_community.vectorstores import FAISS
from embeddings.embedder import Embedder
from retriever.hybrid_retriever import HybridRetriever
from retriever.reranker import DocumentReranker

class ContextBuilder:
    @staticmethod
    def deduplicate(documents):
        """Removes duplicate chunks based on their text content."""
        seen_texts = set()
        unique_docs = []
        for doc in documents:
            if doc.page_content not in seen_texts:
                seen_texts.add(doc.page_content)
                unique_docs.append(doc)
        return unique_docs

    @staticmethod
    def format_context(documents):
        """Formats the context to be strictly traceable for the LLM."""
        formatted_strings = []
        for i, doc in enumerate(documents):
            source = doc.metadata.get("source", "Unknown Source")
            page = doc.metadata.get("page", "Unknown Page")
            
            context_block = (
                f"--- Chunk {i+1} ---\n"
                f"[Source: {source} | Page: {page}]\n"
                f"Content: {doc.page_content}\n"
            )
            formatted_strings.append(context_block)
        return "\n".join(formatted_strings)


# --- PIPELINE EXECUTION BLOCK ---
if __name__ == "__main__":
    print("--- Starting RAG Pipeline from Context Builder ---")
    
    print("Loading Embedder and FAISS Database...")
    embedder = Embedder()
    vectorstore = FAISS.load_local(
        "src/vectorstore/db_faiss", 
        embedder.get_embeddings(), 
        allow_dangerous_deserialization=True
    )
    
    all_documents = list(vectorstore.docstore._dict.values())
    print(f"Loaded {len(all_documents)} chunks for Keyword Search.")

    print("\nInitializing Hybrid Retriever and Reranker...")
    hybrid_retriever = HybridRetriever(vectorstore, all_documents)
    reranker = DocumentReranker()
    cb = ContextBuilder()

    # The Exercise Query
    query = "Explain how credit underwriting works"
    my_filters = {
        "category": "Enterprise Knowledge",
        "filename": "file.pdf" 
    }
    
    # You pass the dictionary INTO the function here
    raw_results = hybrid_retriever.retrieve(query, metadata_filters=my_filters)
    
    print(f" Step 1: Retrieved {len(raw_results)} initial chunks via Hybrid Search.")

    unique_results = cb.deduplicate(raw_results)
    print(f" Step 2: Removed duplicates. {len(unique_results)} unique chunks remain.")

    reranked_results = reranker.rerank(query, unique_results, top_k=3)
    print(" Step 3: Reranked chunks using Cross-Encoder. Selected Top 3.")

    final_context = cb.format_context(reranked_results)
    
    print("\n" + "="*60)
    print(" FINAL TRACEABLE CONTEXT (Ready for the LLM)")
    print("="*60)
    print(final_context)
    print("="*60)