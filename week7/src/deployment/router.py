import sys
import os
import yaml

sys.path.append(os.path.abspath("src"))
from memory.memory_store import MemoryStore
from evaluation.rag_eval import Evaluator
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

from pipelines.sql_pipeline import SQLPipeline
from retriever.image_search import ImageSearch
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
        
        config_path = "src/config/model.yaml"
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
            
        model_name = config.get("model_name", "gemini-2.5-flash")
        self.general_llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.7)
        
        self.sql_pipeline = SQLPipeline(data_file_path="src/data/sql/customers-100.csv")
        self.vision_searcher = ImageSearch()
        
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

    def process_query(self, endpoint, query):
        """Processes the request and RETURNS the data instead of printing it."""
        chat_history = self.memory.get_last_n_messages(n=5)
        draft_answer = ""
        context_used = ""
        image_paths = [] # NEW: We will store the actual image paths here!

        # ROUTE 1: TEXT RAG (/ask)
        if endpoint == "/ask":
            try:
                raw_results = self.hybrid_retriever.retrieve(query)
                unique_results = self.context_builder.deduplicate(raw_results)
                reranked_results = self.reranker.rerank(query, unique_results, top_k=3)
                final_context = self.context_builder.format_context(reranked_results)
                
                full_prompt = f"""You are a precise and helpful AI assistant. 
                    Your primary directive is to answer the user's query based ONLY on the provided Context Documents and Conversation History. 

                    IMPORTANT: If the answer cannot be found within the provided Context Documents, you must state exactly: "I am sorry, but I do not have enough information in the provided documents to answer that question." 
                    Do NOT use your own external knowledge to fill in the blanks.

                    Context Documents:
                    {final_context}

                    Conversation History:
                    {chat_history}

                    User Query: {query}
                    Answer:"""
                draft_answer = self.general_llm.invoke(full_prompt).content
                context_used = final_context
            except Exception as e:
                draft_answer = f"Text RAG Execution Failed: {str(e)}"
            
        # ROUTE 2: SQL DB (/ask-sql)
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

        # ROUTE 3: VISION RAG (/ask-image)
        elif endpoint == "/ask-image":
            try:
                if os.path.isfile(query):
                    search_results = self.vision_searcher.search_by_image(query, top_k=3)
                else:
                    search_results = self.vision_searcher.search_by_text(query, top_k=3)
                
                if search_results:
                    context_used = ""
                    detailed_list = ""
                    for i, res in enumerate(search_results):
                        context_used += f"File: {res['filename']} | Summary: {res['caption']} | OCR: {res['ocr_text']}\n"
                        detailed_list += f"{i+1}. File: {res['filename']}\n   - Caption: {res['caption']}\n   - OCR: {res['ocr_text']}\n\n"
                        
                        # NEW: Add the path so Streamlit can render it
                        image_paths.append(res['filepath'])
                    
                    prompt = f"""Here is data extracted from {len(search_results)} images: 
                    {context_used}\n\nThe user searched for: '{query}'. 
                    Write a conversational summary that explicitly mentions and describes EVERY SINGLE image provided in the data above."""
                    
                    ai_summary = self.general_llm.invoke(prompt).content
                    draft_answer = f"**AI Vision Summary:**\n{ai_summary}\n\n**Source Files:**\n{detailed_list}"
                else:
                    draft_answer = "No matching images found in the database."
                    context_used = "None"
            except Exception as e:
                draft_answer = f"Vision Search Failed: {str(e)}"

        # AGENTIC EVALUATION
        final_answer, confidence_score, critique_text = self.evaluator.grade_and_refine(query, draft_answer, context_used)

        # Return a clean dictionary to Streamlit
        return {
            "endpoint": endpoint,
            "query": query,
            "draft_answer": draft_answer,
            "context_used": context_used,
            "final_answer": final_answer,
            "confidence_score": confidence_score,
            "critique_text": critique_text,
            "image_paths": image_paths # NEW: Passing the paths to the UI
        }

    def save_feedback(self, endpoint, query, final_answer, confidence_score, critique_text, feedback_label):
        """Called by Streamlit buttons to save the final memory state."""
        self.memory.append_message(endpoint, query, final_answer, confidence_score, critique=critique_text, feedback=feedback_label)