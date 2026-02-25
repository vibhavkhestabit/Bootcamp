import sys
import os

sys.path.append(os.path.abspath("src"))
from memory.memory_store import MemoryStore
from evaluation.rag_eval import Evaluator
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# --- DAY 4: SQL PIPELINE ---
from pipelines.sql_pipeline import SQLPipeline

# --- DAY 3: VISION PIPELINE ---
from retriever.image_search import ImageSearch

# --- DAYS 1 & 2: TEXT PIPELINE COMPONENTS ---
from embeddings.embedder import Embedder
from langchain_community.vectorstores import FAISS
from retriever.hybrid_retriever import HybridRetriever
from retriever.reranker import DocumentReranker
from pipelines.context_builder import ContextBuilder

load_dotenv()

class CapstoneRouter:
    def __init__(self):
        self.memory = MemoryStore()
        self.evaluator = Evaluator()
        
        # Initialize our foundational LLM
        self.general_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
        
        print("\n[System] Spinning up Data Pipelines...")
        
        # 1. Initialize SQL System (Day 4)
        print(" -> Loading SQL Pipeline...")
        self.sql_pipeline = SQLPipeline(data_file_path="src/data/sql/customers-100.csv")
        
        # 2. Initialize Vision System (Day 3)
        print(" -> Loading Vision Pipeline...")
        self.vision_searcher = ImageSearch()
        
        # 3. Initialize Text RAG System (Days 1 & 2)
        print(" -> Loading Text Vector DB & Retrievers...")
        self.embedder = Embedder()
        self.vectorstore = FAISS.load_local(
            "src/vectorstore/db_faiss", 
            self.embedder.get_embeddings(), 
            allow_dangerous_deserialization=True
        )
        self.all_documents = list(self.vectorstore.docstore._dict.values())
        self.hybrid_retriever = HybridRetriever(self.vectorstore, self.all_documents)
        self.reranker = DocumentReranker()
        self.context_builder = ContextBuilder()
        
        print("[System] All systems GO.\n")

    def route_request(self, user_input):
        """API Endpoint Router."""
        
        parts = user_input.split(" ", 1)
        endpoint = parts[0].strip()
        query = parts[1].strip() if len(parts) > 1 else ""

        chat_history = self.memory.get_last_n_messages(n=5)
        
        draft_answer = ""
        context_used = ""

        print("\n Processing Request...")
        
        # ---------------------------------------------------------
        # ROUTE 1: TEXT RAG (/ask)
        # ---------------------------------------------------------
        if endpoint == "/ask":
            try:
                print(f" Running Hybrid Retrieval for query: '{query}'...")
                raw_results = self.hybrid_retriever.retrieve(query)
                print(f"   ↳ Retrieved {len(raw_results)} raw chunks.")
                
                unique_results = self.context_builder.deduplicate(raw_results)
                print(f" Deduplication complete: Filtered down to {len(unique_results)} unique chunks.")
                
                reranked_results = self.reranker.rerank(query, unique_results, top_k=3)
                print(f" Reranking complete: Sorted and selected the Top 3 chunks.")
                
                final_context = self.context_builder.format_context(reranked_results)
                print(" Passing refined context and chat history to the LLM...")
                
                # Ask LLM using the retrieved text and memory
                full_prompt = f"Context Documents:\n{final_context}\n\nConversation History:\n{chat_history}\n\nAnswer this new query: {query}"
                draft_answer = self.general_llm.invoke(full_prompt).content
                context_used = final_context
            except Exception as e:
                draft_answer = f"Text RAG Execution Failed: {str(e)}"
            
        # ---------------------------------------------------------
        # ROUTE 2: SQL DB (/ask-sql)
        # ---------------------------------------------------------
        elif endpoint == "/ask-sql":
            try:
                schema, conn = self.sql_pipeline.schema_loader.load_and_get_schema()
                sql = self.sql_pipeline.generator.generate_sql(query, schema)
                cursor = conn.cursor()
                cursor.execute(sql)
                raw_results = cursor.fetchall()
                draft_answer = self.sql_pipeline.generator.summarize_results(query, sql, raw_results)
                context_used = str(raw_results)
            except Exception as e:
                draft_answer = f"SQL Execution Failed: {str(e)}"

        # ---------------------------------------------------------
        # ROUTE 3: VISION RAG (/ask-image)
        # ---------------------------------------------------------
        elif endpoint == "/ask-image":
            import os
            try:
                # 1. SMART ROUTING: Check if the user typed a valid file path
                if os.path.isfile(query):
                    print(" Image file detected! Running Image-to-Image search...")
                    # Call the image-to-image method you built in Day 3
                    search_results = self.vision_searcher.search_by_image(query, top_k=3)
                else:
                    print(" Text query detected! Running Text-to-Image search...")
                    # Fall back to standard text search
                    search_results = self.vision_searcher.search_by_text(query, top_k=3)
                
                # 2. FORMAT THE OUTPUT
                if search_results:
                    draft_answer = "Here are the top matching images from your database:\n"
                    context_used = ""
                    
                    # Loop through the results and explicitly print the file names
                    for i, res in enumerate(search_results):
                        draft_answer += f"{i+1}. File: {res['filename']}\n   - Caption: {res['caption']}\n   - OCR: {res['ocr_text']}\n\n"
                        context_used += f"File: {res['filename']} | Summary: {res['caption']} | OCR: {res['ocr_text']}\n"
                else:
                    draft_answer = "No matching images found in the database."
                    context_used = "None"
            except Exception as e:
                draft_answer = f"Vision Search Failed: {str(e)}"

            
        elif endpoint == "/history":
            print("\n --- Current Memory Stack ---")
            raw_history = self.memory.get_last_n_messages(n=5)
            if raw_history:
                print(raw_history)
            else:
                print("Memory stack is currently empty.")
            print("------------------------------\n")
            return  # We return here so it doesn't try to run the Evaluator on the history!
            
        else:
            print(" Invalid Endpoint. Use /ask, /ask-sql, or /ask-image")
            return

        # ---------------------------------------------------------
        # AGENTIC EVALUATION & LOGGING
        # ---------------------------------------------------------
        print(" Running Agentic Evaluation & Hallucination Check...")
        final_answer, confidence_score = self.evaluator.grade_and_refine(query, draft_answer, context_used)

        self.memory.append_message(endpoint, query, final_answer, confidence_score)

        print("\n" + "="*50)
        print(f" Confidence Score: {confidence_score}/100")
        print(f" Final AI Answer:\n{final_answer}")
        print("="*50 + "\n")


if __name__ == "__main__":
    app = CapstoneRouter()
    print(" Day 5 Capstone API Router Online. Type 'exit' to quit.")
    print("Endpoints: /ask [query], /ask-sql [query], /ask-image [query], /history")
    
    while True:
        user_input = input("\nEnter Command: ")
        if user_input.lower() == 'exit':
            break
        app.route_request(user_input)