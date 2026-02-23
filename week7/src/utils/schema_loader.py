import pandas as pd
import sqlite3
import os

class SchemaLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        # The invisible RAM database
        self.conn = sqlite3.connect(":memory:") 
        self.table_name = "dataset"

    def load_and_get_schema(self):
        """Reads CSV/Excel, loads it into SQLite RAM, and returns the schema."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Could not find the file: {self.file_path}")

        print(f"[System] Loading {self.file_path} into memory...")
        
        # Read the file
        if self.file_path.endswith('.csv'):
            df = pd.read_csv(self.file_path)
        elif self.file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(self.file_path)
        else:
            raise ValueError("Unsupported file format. Please use .csv or .xlsx")

        # Push into the RAM database
        df.to_sql(self.table_name, self.conn, index=False, if_exists="replace")

        # Extract schema for Gemini
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{self.table_name}';")
        schema = cursor.fetchone()[0]

        return schema, self.conn