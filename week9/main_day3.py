import asyncio
import json
import os
import re
import sqlite3
from dotenv import load_dotenv
load_dotenv() 
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.agents import AssistantAgent
from tools.file_agent    import get_file_agent
from tools.db_agent      import get_db_agent
from tools.code_executor import get_code_agent
from nexus_ai.config import get_model_client, ACTIVE_PROVIDER

def setup_dummy_data():
    # Only create sales.csv if it doesn't exist
    if not os.path.exists("sales.csv"):
        with open("sales.csv", "w", encoding="utf-8") as f:
            f.write("id,product,revenue\n1,Widget A,100\n2,Widget B,550\n3,Widget C,300")
        print("[System] Created sales.csv")

    # Only create database.db users table if it doesn't exist
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, role TEXT)")
    # Only insert if table is empty
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (name, role) VALUES ('Alice', 'Admin'), ('Bob', 'User')")
        print("[System] Created users table.")
    conn.commit()
    conn.close()
    print("[System] Demo data ready.")

PLANNER_SYSTEM = """\
You are a task planner for a multi-agent system. Given a user request, break it into an ordered list of steps. Each step must be handled by exactly one agent.

AGENTS AND THEIR JOBS:
  FILE  → read files, write files, create .csv/.txt/.md, list files
  DB    → query SQLite databases, run SQL, insert/read table rows
  CODE  → run Python code, do calculations, analyse data, generate insights

RULES:
  - If a task needs multiple agents (e.g. read a file THEN analyse it THEN write a report), output multiple steps in the correct order.
  - Each step's "task" must be a COMPLETE, SELF-CONTAINED instruction that also references any relevant output from previous steps 
    (e.g. "Using the CSV data provided, analyse it and return top 5 insights").
  - The last step should always produce what the user ultimately asked for.
  - Output ONLY valid JSON — no explanation, no markdown fences.

FILE SAVING RULE — CRITICAL:
  Only add a FILE step to save code if the user EXPLICITLY asked to save or create a file. Trigger words: "save", "store", 
  "create a file", "write to a file", "put it in a file", "export".

  CORRECT — user said "save it":
    "generate fibonacci code and save it as fibonacci.py"
    → Step 1: CODE, Step 2: FILE

  WRONG — user only asked to see the code:
    "generate fibonacci code"        → Step 1: CODE only  (no FILE step)
    "give me the binary search code" → Step 1: CODE only  (no FILE step)
    "show me a sorting algorithm"    → Step 1: CODE only  (no FILE step)

DB INSERT RULE — CRITICAL:
  When a DB step needs to insert data, the task MUST explicitly say:
  "CREATE TABLE IF NOT EXISTS ... then INSERT the data".
  Never just say "insert into" — always include the CREATE step.

  CORRECT:
    "CREATE TABLE IF NOT EXISTS Vibhav in Vibhav.db with columns SaleID, Date, ProductID, CustomerID, Quantity, UnitPrice —
     then INSERT the 10 rows provided."

  WRONG:
    "Insert the 10 entries into Vibhav table in Vibhav.db" ← Agent may stop if table doesn't exist yet

DB EXPORT RULE — CRITICAL:
  When a DB query step is followed by a FILE step that exports data, the DB step task MUST explicitly say "return ALL rows as a formatted table".
  The FILE agent needs actual data rows — NOT a confirmation like "[execute_sql OK]".

  CORRECT:
    DB step task:   "Query ALL rows from RevenueByProduct in Test.db and return the complete results as a formatted data table."
    FILE step task: "Write the query results provided into revenue.csv"

  WRONG:
    DB step task:   "Query the RevenueByProduct table"
    FILE step task: "Export the table as revenue.csv"  ← FILE gets no data

OUTPUT FORMAT (strict JSON array):
[
  {"step": 1, "agent": "FILE", "task": "Read the file sales.csv and return its full content."},
  {"step": 2, "agent": "CODE", "task": "Using the CSV data provided, calculate total revenue per product and identify the top 3."},
  {"step": 3, "agent": "FILE", "task": "Write a file called report.txt containing the analysis results provided."}
]
"""

def parse_plan(raw: str) -> list:
    """Extract JSON array from planner output robustly."""
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    try:
        plan = json.loads(raw)
        if isinstance(plan, list):
            return plan
    except json.JSONDecodeError:
        pass

    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    print("[Planner] Could not parse plan — defaulting to single CODE step.")
    return [{"step": 1, "agent": "CODE", "task": raw}]

#  Main loop

async def main():
    setup_dummy_data()
    model_client = get_model_client()
    planner = AssistantAgent(
        name="Planner_Agent",
        description="Breaks user requests into ordered multi-agent steps.",
        system_message=PLANNER_SYSTEM,
        model_client=model_client,
    )
    agents = {
        "FILE": get_file_agent(model_client),
        "DB":   get_db_agent(model_client),
        "CODE": get_code_agent(model_client),
    }

    print("\n=== Day 3: Autonomous Tool-Calling Pipeline ===")
    print(f"    Provider : {ACTIVE_PROVIDER.upper()}")
    print("    Agents   : FILE · DB · CODE")
    print("    Planning : Multi-step chaining enabled")
    print("    Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("\nUser: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[Shutting down]")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            print("[Shutting down]")
            break

        # ── Plan ──────────────────────────────────────────────────
        print("\n[Planner thinking...]")
        planner_resp = await planner.on_messages(
            [TextMessage(content=user_input, source="user")],
            cancellation_token=None,
        )
        raw_plan = planner_resp.chat_message.content
        plan = parse_plan(raw_plan)

        print(f"[Planner] {len(plan)}-step plan:")
        for step in plan:
            print(f"  Step {step['step']} → [{step['agent']}] {step['task'][:80]}...")

        # ── Execute steps in sequence ─────────────────────────────
        # all_outputs accumulates every step's result so later agents always have full context — not just the last step's output.
        all_outputs = []

        for step in plan:
            agent_key = step["agent"].upper()
            task      = step["task"]

            if all_outputs:
                history = "\n\n".join(all_outputs)
                enriched_task = (
                    f"{task}\n\n"
                    f"--- Outputs from all previous steps ---\n{history}"
                )
            else:
                enriched_task = task

            print(f"\n[Step {step['step']}] Running {agent_key} Agent...")
            print(f"  Task: {task[:100]}{'...' if len(task) > 100 else ''}")

            if agent_key not in agents:
                print(f"  [WARNING] Unknown agent '{agent_key}' — skipping.")
                continue

            try:
                resp = await agents[agent_key].on_messages(
                    [TextMessage(content=enriched_task, source="user")],
                    cancellation_token=None,
                )
                result = resp.chat_message.content
                all_outputs.append(
                    f"[Step {step['step']} — {agent_key} Agent]\n{result}"
                )
                print(f"\n[{agent_key} Agent Result]\n{result}\n")
            except Exception as e:
                err = f"[ERROR] {e}"
                all_outputs.append(f"[Step {step['step']} — {agent_key} Agent]\n{err}")
                print(f"  [ERROR in {agent_key} Agent] {e}")

        print("─" * 50)
        print("\n[Pipeline complete]")
        print("─" * 50)

if __name__ == "__main__":
    asyncio.run(main())