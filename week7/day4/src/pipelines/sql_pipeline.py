import os
import sys

sys.path.append(os.path.abspath("src"))
from utils.schema_loader import SchemaLoader
from generator.sql_generator import SQLGenerator

class SQLPipeline:
    def __init__(self, data_file_path):
        self.schema_loader = SchemaLoader(data_file_path)
        self.generator = SQLGenerator()

    def run(self, question):
        print(f"\n[1] User Question: '{question}'")
        
        # 1. Load Schema and get RAM connection
        try:
            schema, conn = self.schema_loader.load_and_get_schema()
            print("[2] CSV successfully converted to in-memory SQL table.")
        except Exception as e:
            print(f" Failed to load data: {e}")
            return
        
        # 2. Generate SQL
        sql = self.generator.generate_sql(question, schema)
        print(f"[3] LLM Generated SQL:\n    {sql}")
        
        # 3 & 4. Validate and Execute with Error Correction Loop
        max_attempts = 3
        results = None
        
        for attempt in range(max_attempts):
            # Step A: Guardrails (Runs every single time, even on fixed queries)
            try:
                self.generator.validate_sql(sql)
                if attempt == 0:
                    print("[4] SQL Validated: Safe read-only query detected.")
                else:
                    print("[4] Fixed SQL Validated: Safe read-only query detected.")
            except ValueError as e:
                print(f" Security Block: {e}")
                return 
            
            # Step B: Execution
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                results = cursor.fetchall()
                print(f"[5] Raw Execution Results: {results}")
                break 
            except Exception as e:
                error_msg = str(e)
                print(f" [Attempt {attempt + 1}] Database Error: {error_msg}")
                
                # Step C: The Agentic Self-Healing Loop
                if attempt < max_attempts - 1:
                    print(" Sending error back to LLM for self-correction...")
                    sql = self.generator.fix_sql(question, schema, sql, error_msg)
                    print(f"[3] LLM Generated Fixed SQL:\n    {sql}")
                else:
                    print(" Max retries reached. Could not fix the query.")
                    return 

        # 5. Summarize Results
        summary = self.generator.summarize_results(question, sql, results)
        print("\n" + "="*50)
        print(" FINAL ANSWER:")
        print(summary)
        print("="*50 + "\n")


if __name__ == "__main__":
    # Pointing directly to your real CSV
    csv_path = "src/data/sql/customers-100.csv" 
    
    pipeline = SQLPipeline(data_file_path=csv_path)
    
    pipeline.run("How many total customers are in the dataset?")

    pipeline.run("Return customers whose first name starts from s in descending order")
    
    pipeline.run("Delete all records from the dataset.")