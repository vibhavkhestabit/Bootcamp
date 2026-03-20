"""
tools/file_agent.py
─────────────────────────────────────────────────────────────────
File Operations Agent.

Tools:
    read_file(file_path)               → returns raw text
    write_file(file_path, content)     → creates/overwrites any file
    write_csv(file_path, rows)         → writes valid CSV from list of dicts
                                         (guaranteed safe escaping via DictWriter)
    append_file(file_path, content)    → appends to existing file
    list_files(directory)              → lists files in a folder
─────────────────────────────────────────────────────────────────
"""

import csv
import os
import statistics
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient


# ─────────────────────────────────────────────────────────────────
#  Tool functions
# ─────────────────────────────────────────────────────────────────

def read_file(file_path: str) -> str:
    """
    Read any local file and return its content as a string.
    For .csv files also returns column statistics.
    """
    try:
        path_lower = file_path.lower()

        if path_lower.endswith(".csv"):
            with open(file_path, newline="", encoding="utf-8") as f:
                reader  = csv.DictReader(f)
                rows    = list(reader)
                columns = list(reader.fieldnames or [])

            if not rows:
                return f"[read_file] '{file_path}' is empty."

            lines = [
                f"CSV file: {file_path}",
                f"  {len(rows)} rows  x  {len(columns)} columns",
                f"  Columns: {', '.join(columns)}",
                "",
                "── Rows ──",
            ]
            for i, r in enumerate(rows, 1):
                lines.append(f"  {i:>3}. " + " | ".join(f"{k}={v}" for k, v in r.items()))

            lines.append("")
            lines.append("── Column statistics ──")
            for col in columns:
                values = [r[col] for r in rows if r.get(col, "").strip() != ""]
                try:
                    nums  = [float(v) for v in values]
                    mean  = statistics.mean(nums)
                    stdev = statistics.stdev(nums) if len(nums) > 1 else 0.0
                    lines.append(
                        f"  [{col}] numeric  count={len(nums)}  "
                        f"min={min(nums):.2f}  max={max(nums):.2f}  "
                        f"mean={mean:.2f}  stdev={stdev:.2f}"
                    )
                except ValueError:
                    unique = list(dict.fromkeys(values))
                    lines.append(
                        f"  [{col}] text  count={len(values)}  "
                        f"unique={len(unique)}  values={unique[:5]}"
                    )
            return "\n".join(lines)

        else:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

    except Exception as e:
        return f"[read_file ERROR] {e}"


def write_file(file_path: str, content: str) -> str:
    """
    Write (overwrite) a local file with the given text content.
    Creates parent directories automatically.
    For .csv files prefer write_csv() — this writes raw text as-is.
    """
    try:
        parent = os.path.dirname(file_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"[write_file OK] Wrote {len(content)} chars to '{file_path}'"
    except Exception as e:
        return f"[write_file ERROR] {e}"


def write_csv(file_path: str, rows: list) -> str:
    """
    Write structured data to a CSV file safely.

    Accepts:
      - list of dicts:  [{"name": "Alice", "age": 30}, ...]   ← preferred
      - list of lists with header row:  [["name","age"], ["Alice",30], ...]
      - list of lists without header:   [["Alice", 30], ...]  → cols named col_0, col_1...
      - JSON string:    '[{"name": "Alice", "age": 30}, ...]' ← auto-parsed

    Uses csv.DictWriter — guarantees correct escaping of commas, quotes, newlines.
    Creates parent directories automatically.
    """
    import json as _json
    try:
        if not rows:
            return "[write_csv ERROR] No rows provided."

        # ── Handle JSON string input from Code Agent ──────────────
        if isinstance(rows, str):
            try:
                rows = _json.loads(rows)
            except _json.JSONDecodeError:
                return "[write_csv ERROR] Could not parse JSON string input."

        if not rows:
            return "[write_csv ERROR] No rows provided."

        # ── Normalise to list of dicts ────────────────────────────
        if isinstance(rows[0], dict):
            dict_rows = rows
        elif isinstance(rows[0], (list, tuple)):
            if all(isinstance(v, str) for v in rows[0]):
                headers   = [str(h) for h in rows[0]]
                dict_rows = [dict(zip(headers, r)) for r in rows[1:]]
            else:
                headers   = [f"col_{i}" for i in range(len(rows[0]))]
                dict_rows = [dict(zip(headers, r)) for r in rows]
        else:
            return f"[write_csv ERROR] Unrecognised row type: {type(rows[0])}"

        if not dict_rows:
            return "[write_csv ERROR] No data rows after normalisation."

        parent = os.path.dirname(file_path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=dict_rows[0].keys())
            writer.writeheader()
            writer.writerows(dict_rows)

        return (
            f"[write_csv OK] '{file_path}' — "
            f"{len(dict_rows)} rows, {len(dict_rows[0])} columns"
        )
    except Exception as e:
        return f"[write_csv ERROR] {e}"


def append_file(file_path: str, content: str) -> str:
    """Append content to an existing file (creates it if missing)."""
    try:
        parent = os.path.dirname(file_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content)
        return f"[append_file OK] Appended {len(content)} chars to '{file_path}'"
    except Exception as e:
        return f"[append_file ERROR] {e}"


def list_files(directory: str = ".") -> str:
    """List all files in a directory (non-recursive)."""
    try:
        entries = os.listdir(directory)
        files   = [e for e in entries if os.path.isfile(os.path.join(directory, e))]
        if not files:
            return f"[list_files] No files found in '{directory}'"
        return "\n".join(files)
    except Exception as e:
        return f"[list_files ERROR] {e}"


# ─────────────────────────────────────────────────────────────────
#  Agent builder
# ─────────────────────────────────────────────────────────────────

def get_file_agent(model_client: ChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        name="File_Agent",
        description="Reads, writes, and manages local files including CSVs.",
        system_message="""\
You are the File Operations Agent. You ONLY act by calling your tools.
You NEVER write Python code to do file operations.
You NEVER narrate, describe, or explain what you are about to do.
You NEVER say "I will...", "Here is...", or "Based on the rules...".
You MUST call a tool immediately and directly — that is your only valid response.

YOUR TOOLS:
  read_file(file_path)              → reads any file (.txt, .csv, .md, .py, ...)
                                      CSV files also return column statistics
  write_file(file_path, content)    → writes raw text to any file
  write_csv(file_path, rows)        → writes a properly formatted CSV
                                      rows = list of dicts [{"col": val}, ...]
                                      ALWAYS use this for .csv files, not write_file
  append_file(file_path, content)   → adds to an existing file
  list_files(directory)             → lists files in a folder

DECISION RULES — pick the tool and call it immediately:
  Task says READ?                  → call read_file()
  Task says WRITE / CREATE a .csv? → call write_csv()   ← not write_file
  Task says WRITE / CREATE a .txt? → call write_file()
  Task says APPEND?                → call append_file()
  Task says LIST?                  → call list_files()

RULES:
  1. Call a tool immediately — never fake, guess, or narrate content.
  2. For CSV creation: use write_csv() with rows as a list of dicts.
     Example: write_csv("data/planets.csv", [{"name":"Jupiter","moons":95}, ...])
  3. For text/report/code creation: use write_file() with the complete content
     extracted from the previous step's output.
  4. After the tool call succeeds, report only the tool result (e.g. [write_file OK]).
  5. Do NOT write Python code to accomplish file tasks — call the tool directly.
  6. Do NOT call write_file for CSV — it won't escape commas correctly.\
""",
        model_client=model_client,
        tools=[read_file, write_file, write_csv, append_file, list_files],
    )