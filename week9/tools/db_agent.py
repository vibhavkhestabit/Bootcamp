import sqlite3
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient

def execute_sql(query: str, db_path: str = "database.db") -> str:
    """Executes SQL query and returns formatted results."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Multi-statement support
            if ";" in query and not query.strip().upper().startswith("SELECT"):
                cursor.executescript(query)
                return "Script executed successfully."

            cursor.execute(query)

            # Write operations
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "DROP")):
                return f"Query executed successfully. Rows affected: {cursor.rowcount}"

            rows = cursor.fetchall()

            if not rows:
                return "No results found."

            # ✅ Get column names
            columns = [desc[0] for desc in cursor.description]

            # ✅ Format output
            header = " | ".join(columns)
            separator = "-" * len(header)
            data_rows = "\n".join([" | ".join(map(str, row)) for row in rows])

            return f"{header}\n{separator}\n{data_rows}"

    except Exception as e:
        return f"Database error: {e}"

def get_db_agent(model_client: ChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        name="DB_Agent",
        description="An agent that writes and executes SQL queries.",
        system_message=(
            "You are the Database Agent.\n\n"

            "CRITICAL RULES:\n"
            "1. You are using SQLite.\n"
            "2. SQLite does NOT support CREATE DATABASE.\n"
            "3. If user asks to create a database, create a table instead.\n"
            "4. ALWAYS use execute_sql tool.\n"
            "5. DO NOT explain anything.\n"
        ),
        model_client=model_client,
        tools=[execute_sql]
    )