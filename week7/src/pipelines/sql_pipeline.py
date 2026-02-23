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
            print(f"❌ Failed to load data: {e}")
            return
        
        # 2. Generate SQL
        sql = self.generator.generate_sql(question, schema)
        print(f"[3] LLM Generated SQL:\n    {sql}")
        
        # 3. Validate SQL (Guardrails)
        try:
            self.generator.validate_sql(sql)
            print("[4] SQL Validated: Safe read-only query detected.")
        except ValueError as e:
            print(f"❌ Security Block: {e}")
            return

        # 4. Execute SQL
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            print(f"[5] Raw Execution Results: {results}")
        except Exception as e:
            print(f"❌ Execution failed: Database Error: {str(e)}")
            return

        # 5. Summarize Results
        summary = self.generator.summarize_results(question, sql, results)
        print("\n" + "="*50)
        print("🎯 FINAL ANSWER:")
        print(summary)
        print("="*50 + "\n")


if __name__ == "__main__":
    # Pointing directly to your real CSV!
    csv_path = "src/data/sql/customers-100.csv" 
    
    pipeline = SQLPipeline(data_file_path=csv_path)
    
    # Let's ask a generic question that should work for a customer dataset
    pipeline.run("How many total customers are in the dataset?")

    pipeline.run("Return customers whose first name starts from s")
    
    # Testing the security guardrails
    pipeline.run("Delete all records from the dataset.")