import asyncio
import sqlite3
import json
import re
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.agents import AssistantAgent

from tools.file_agent import get_file_agent, read_file, write_file
from tools.db_agent import get_db_agent, execute_sql
from tools.code_executor import get_code_agent, execute_python_script


def setup_dummy_data():
    with open("sales.csv", "w", encoding="utf-8") as f:
        f.write("id,product,revenue\n1,Widget A,100\n2,Widget B,550\n3,Widget C,300")
    
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, role TEXT)")
    c.execute("DELETE FROM users") 
    c.execute("INSERT INTO users (name, role) VALUES ('Alice', 'Admin'), ('Bob', 'User')")
    conn.commit()
    conn.close()
    print("[System] Dummy data ready.")


async def main():
    setup_dummy_data()

    model_client = OpenAIChatCompletionClient(
        model="mistral",
        base_url="http://localhost:11434/v1",
        api_key="NotRequired",
        model_info={"vision": False, "function_calling": True, "json_output": False, "family": "unknown"}
    )

    agents = {
        "FILE": get_file_agent(model_client),
        "DB": get_db_agent(model_client),
        "CODE": get_code_agent(model_client)
    }

    router_agent = AssistantAgent(
        name="Router_Agent",
        description="Routes user queries to the correct specialized agent.",
        system_message=(
            "You are a STRICT router.\n"
            "Your job is to classify the user's request into ONE of three categories:\n\n"

            "CODE → if the user asks for programming, logic, algorithms, or calculations\n"
            "FILE → if the user asks to read or write files\n"
            "DB → if the user asks about databases, tables, or stored data\n\n"

            "Rules:\n"
            "- Output ONLY one word: CODE, FILE, or DB\n"
            "- No explanation, no formatting\n"
            "- If the request involves multiple steps, choose the PRIMARY intent\n"
            "- If unsure, choose CODE\n"
        ),
        model_client=model_client
    )

    print("\n=== Day 3: Fully Autonomous Tool-Calling ===")
    print("Type your request. Type 'exit' to quit.\n")

    while True:
        user_input = input("\nUser: ").strip()
        
        if user_input.lower() in ['exit', 'quit']:
            print("Shutting down...")
            break
        if not user_input:
            continue

        print("\n[ROUTER IS ANALYZING...]")
        
        router_response = await router_agent.on_messages(
            [TextMessage(content=user_input, source="user")], 
            cancellation_token=None
        )

        raw_output = router_response.chat_message.content.strip().upper()

        if "CODE" in raw_output:
            target = "CODE"
        elif "FILE" in raw_output:
            target = "FILE"
        elif "DB" in raw_output:
            target = "DB"
        else:
            print(f"[System] Router confused ('{raw_output}'). Defaulting to CODE.")
            target = "CODE"

        print(f"[ROUTER DECISION]: {target}")
        print(f"[{target} AGENT RUNNING...]")

        active_agent = agents[target]
        
        try:
            response = await active_agent.on_messages(
                [TextMessage(content=user_input, source="user")], 
                cancellation_token=None
            )
            
            output_text = response.chat_message.content
            print(f"\n[{target} OUTPUT]\n{output_text}\n")
            
            matches = re.findall(r'\[\s*\{\s*"name"\s*:.*?\}\s*\]', output_text)
            
            if matches:
                print("[SYSTEM] Executing tool calls...")
                for match in matches:
                    try:
                        tool_calls = json.loads(match)
                        
                        for call in tool_calls:
                            func_name = call.get("name")
                            args = call.get("arguments", {})
                            
                            print(f"\n[EXECUTING]: {func_name}")
                            
                            if func_name == "write_file":
                                result = write_file(args.get("content"), args.get("file_path"))

                            elif func_name == "read_file":
                                result = read_file(args.get("file_path"))

                            elif func_name == "execute_sql":
                                result = execute_sql(
                                args.get("query"),
                                args.get("db_path", "database.db")
                            )

                            elif func_name == "execute_python_script":
                                code = args.get("code")
                                print(f"\n[CODE]:\n{code}\n")
                                result = execute_python_script(code)

                            else:
                                result = f"Unknown tool: {func_name}"
                                
                            print(f"[RESULT]:\n{result}")
                            
                    except json.JSONDecodeError:
                        print(f"[WARNING] Bad JSON: {match}")
                        continue

        except Exception as e:
            print(f"[ERROR]: {e}")
        
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())