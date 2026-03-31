import sqlite3
import re as _re
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient

#  Tool functions

def inspect_schema(db_path: str) -> str:
    """
    Return full schema of all user tables: columns, types, and sample rows.
    Always call this before writing SQL so you know the exact column names.
    Skips internal sqlite_* tables.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            tables = [r["name"] for r in cur.fetchall()]

            if not tables:
                return f"[inspect_schema] '{db_path}' has no user tables."

            lines = [f"DATABASE SCHEMA: {db_path}", "=" * 40]
            for table in tables:
                # Quote table name to handle spaces/special chars safely
                cur.execute(f'PRAGMA table_info("{table}")')
                cols = cur.fetchall()

                cur.execute(f'SELECT COUNT(*) as n FROM "{table}"')
                n_rows = cur.fetchone()["n"]

                lines.append(f"\nTable: {table}  ({n_rows} rows)")
                lines.append("Columns:")
                for c in cols:
                    pk = " PRIMARY KEY" if c["pk"] else ""
                    lines.append(f"  {c['name']}  {c['type']}{pk}")

                cur.execute(f'SELECT * FROM "{table}" LIMIT 3')
                samples = [dict(r) for r in cur.fetchall()]
                if samples:
                    lines.append("Sample rows:")
                    for r in samples:
                        lines.append("  " + ", ".join(f"{k}={v}" for k, v in r.items()))

            lines.append("\n" + "=" * 40)
            return "\n".join(lines)

    except Exception as e:
        return f"[inspect_schema ERROR] {e}"


def execute_sql(query: str, db_path: str) -> str:
    """
    Execute a SQL query and return formatted results.
    Always call inspect_schema() first to know column names.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            # Multi-statement scripts (not SELECT)
            if ";" in query and not query.strip().upper().startswith(("SELECT", "PRAGMA", "WITH")):
                cur.executescript(query)
                conn.commit()
                # Verify actual row counts after INSERT
                tables = _re.findall(r"INSERT\s+INTO\s+(\w+)", query, _re.IGNORECASE)
                if tables:
                    counts = []
                    for t in set(tables):
                        try:
                            cur.execute(f'SELECT COUNT(*) FROM "{t}"')
                            n = cur.fetchone()[0]
                            counts.append(f"{t}: {n} rows")
                        except Exception:
                            pass
                    if counts:
                        return f"[execute_sql OK] Script executed. Row counts — {', '.join(counts)}"
                return "[execute_sql OK] Script executed successfully."

            cur.execute(query)

            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE",
                                                   "CREATE", "DROP", "ALTER")):
                conn.commit()
                return f"[execute_sql OK] Rows affected: {cur.rowcount}"

            rows = [dict(r) for r in cur.fetchall()]
            if not rows:
                return "[execute_sql] Query returned no rows."

            header   = " | ".join(rows[0].keys())
            sep      = "─" * len(header)
            rows_str = "\n".join(
                " | ".join(str(v) for v in r.values()) for r in rows
            )
            return f"{header}\n{sep}\n{rows_str}"

    except Exception as e:
        return f"[execute_sql ERROR] {e}"


#  Agent builder

def get_db_agent(model_client: ChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        name="DB_Agent",
        description="Inspects and queries SQLite databases.",
        system_message="""\
You are the Database Agent. You work with SQLite databases.

YOUR TOOLS:
  inspect_schema(db_path)           → shows all tables, columns, and sample rows
  execute_sql(query, db_path)       → runs SQL and returns results

RULES:
  1. Call inspect_schema() first to check existing tables.
     If the schema shows no tables — that is EXPECTED for a new database.
     Proceed immediately to CREATE the table and INSERT data.
     NEVER stop or give up just because a database is empty.
  2. When task says INSERT data — always do TWO things in order:
     a. CREATE TABLE IF NOT EXISTS with correct columns
     b. INSERT all rows
     Combine both into one execute_sql() call as a script.
  3. Write SQL using only the column names from the provided data.
  4. SQLite does NOT support CREATE DATABASE — create a table instead.
  5. After inserting rows, ALWAYS verify row count.
     If row count is 0, the insert failed — retry with corrected SQL.

     APPEND RULE — CRITICAL:
  When task says "append", "add more", or "insert more rows":
  → NEVER use fixed SaleID/ID values — use NULL or omit the PRIMARY KEY
    so SQLite auto-increments from the last existing value.
  → After inserting, SELECT COUNT(*) must show original rows + new rows.
  → If count equals only the new rows, data was lost — report the error.

  CORRECT:
    INSERT INTO Sales (Date, ProductID, CustomerID, TotalAmount)
    VALUES ('2024-01-01', 101, 1001, 250.00), ...   ← no SaleID, auto-increments

  WRONG:
    INSERT INTO Sales VALUES (1, ...), (2, ...) ← conflicts with existing rows
    
  6. If a query fails, fix the SQL and retry immediately.

EMPTY DATABASE RULE — CRITICAL:
  If inspect_schema() returns "has no user tables" — this is NOT an error.
  It means the database is new. Your job is to CREATE the table yourself.
  WRONG behaviour: stopping and reporting the database is empty.
  CORRECT behaviour: create the table, insert the data, verify row count.

  Example flow for "insert data into NewDB.db table Sales":
    Step 1: inspect_schema("NewDB.db")       → "has no user tables" (expected)
    Step 2: execute_sql("CREATE TABLE IF NOT EXISTS Sales (...); INSERT INTO Sales VALUES (...);", "NewDB.db")
    Step 3: execute_sql("SELECT COUNT(*) FROM Sales", "NewDB.db")  → verify rows

DB_PATH RULE — CRITICAL:
  ALWAYS pass db_path explicitly in EVERY tool call — never rely on the default.
  If the task mentions a specific database file (e.g. "Vibhav.db", "Test.db"),
  use that exact filename in ALL tool calls for that task.

  CORRECT:
    inspect_schema("Test.db")
    execute_sql("CREATE TABLE IF NOT EXISTS RevenueByProduct ...", "Test.db")

  WRONG:
    inspect_schema()                    <- defaults to database.db
    execute_sql("SELECT * FROM Sales")  <- wrong db

  Every single tool call must have the db_path argument. No exceptions.\
""",
        model_client=model_client,
        tools=[inspect_schema, execute_sql],
    )