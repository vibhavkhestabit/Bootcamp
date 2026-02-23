import os
import yaml
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Automatically loads the secrets from your .env file
load_dotenv()

class SQLGenerator:
    def __init__(self):
        # 1. Read the YAML configuration
        config_path = "src/config/model.yaml"
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file missing: {config_path}")
            
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            
        provider = config.get("provider")
        model_name = config.get("model_name")
        api_key_env = config.get("api_key_env")
        
        # 2. Grab the specific key the YAML asked for
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(f"API Key '{api_key_env}' not found in .env file.")

        # 3. Dynamically load the correct LLM
        print(f"[System] Initializing {provider} ({model_name})...")
        if provider == "gemini":
            self.llm = ChatGoogleGenerativeAI(
                model=model_name, 
                temperature=0, 
                google_api_key=api_key
            )
        # You can easily add 'elif provider == "openai":' here later!
        else:
            raise ValueError(f"Provider '{provider}' is not supported yet.")

    def generate_sql(self, question, schema):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert SQL data analyst. Output ONLY the raw SQL query without markdown formatting, explanations, or backticks. The table is named 'dataset'. Use the following schema:\n{schema}"),
            ("user", "{question}")
        ])
        chain = prompt | self.llm
        response = chain.invoke({"schema": schema, "question": question})
        return response.content.strip().replace("```sql", "").replace("```", "").strip()

    def validate_sql(self, sql):
        forbidden_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
        upper_sql = sql.upper()
        
        for word in forbidden_keywords:
            if word in upper_sql:
                raise ValueError(f"Malicious command detected: {word}. Aborting execution.")
                
        if not upper_sql.strip().startswith("SELECT"):
            raise ValueError("Only read-only SELECT queries are allowed.")
            
        return True

    def summarize_results(self, question, sql, results):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful data assistant. Given the user's question, the SQL query executed, and the raw database results, write a natural, concise, and professional summary of the answer."),
            ("user", "Question: {question}\nSQL Executed: {sql}\nRaw Results: {results}")
        ])
        chain = prompt | self.llm
        response = chain.invoke({"question": question, "sql": sql, "results": str(results)})
        return response.content