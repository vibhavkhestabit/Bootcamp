import sys
import os

sys.path.append(os.path.abspath("src"))
from memory.memory_store import MemoryStore
from evaluation.rag_eval import Evaluator
from pipelines.sql_pipeline import SQLPipeline 
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class CapstoneRouter:
    def __init__(self):
        self.memory = MemoryStore()
        self.evaluator = Evaluator()
        
        # Initialize our tools
        self.general_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
        self.sql_pipeline = SQLPipeline(data_file_path="src/data/sql/customers-100.csv")

    def route_request(self, user_input):
        """Simulates API endpoints via CLI text routing."""
        
        # Extract the endpoint command and the actual query
        parts = user_input.split(" ", 1)
        endpoint = parts[0].strip()
        query = parts[1].strip() if len(parts) > 1 else ""

        # Fetch last 5 messages for context
        chat_history = self.memory.get_last_n_messages(n=5)
        
        draft_answer = ""
        context_used = ""

        print("\n⚙️ Processing Request...")
        
        # Route 1: General Knowledge + Memory
        if endpoint == "/ask":
            full_prompt = f"{chat_history}\nNow answer this new query: {query}"
            draft_answer = self.general_llm.invoke(full_prompt).content
            context_used = chat_history
            
        # Route 2: SQL Interrogation
        elif endpoint == "/ask-sql":
            # We intercept stdout to grab the summary from your existing pipeline
            # For brevity in CLI, we'll run a quick dedicated SQL prompt
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

        # Route 3: Image/Vision (Mocked for CLI standard structure)
        elif endpoint == "/ask-image":
            draft_answer = "Image processing endpoint reached. (Requires Streamlit UI for file upload)."
            
        else:
            print("❌ Invalid Endpoint. Use /ask, /ask-sql, or /ask-image")
            return

        # Pass through the Evaluation & Refinement Loop
        print("🔍 Running Agentic Evaluation & Hallucination Check...")
        final_answer, confidence_score = self.evaluator.grade_and_refine(query, draft_answer, context_used)

        # Log to Memory
        self.memory.append_message(endpoint, query, final_answer, confidence_score)

        print("\n" + "="*50)
        print(f"📊 Confidence Score: {confidence_score}/100")
        print(f"🤖 Final AI Answer:\n{final_answer}")
        print("="*50 + "\n")

if __name__ == "__main__":
    app = CapstoneRouter()
    print("🚀 Day 5 Capstone API Router Online. Type 'exit' to quit.")
    print("Endpoints: /ask [query], /ask-sql [query]")
    
    while True:
        user_input = input("\nEnter Command: ")
        if user_input.lower() == 'exit':
            break
        app.route_request(user_input)