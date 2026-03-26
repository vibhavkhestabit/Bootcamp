"""
─────────────────────────────────────────────────────────────────
Code Execution Agent.
Tools:
    auto_install(code)                → pip-installs any missing imports
    execute_python_script(code)       → runs Python in an isolated subprocess
─────────────────────────────────────────────────────────────────
"""
import re
import subprocess
import sys
import tempfile
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient

#  Package name normalisation

IMPORT_TO_PIP = {
    "sklearn":  "scikit-learn",
    "cv2":      "opencv-python",
    "PIL":      "Pillow",
    "bs4":      "beautifulsoup4",
    "yaml":     "pyyaml",
    "dotenv":   "python-dotenv",
    "dateutil": "python-dateutil",
}


def _extract_imports(code: str) -> list:
    pattern = re.compile(
        r'^\s*(?:import|from)\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.MULTILINE
    )
    seen = []
    for m in pattern.finditer(code):
        pkg = m.group(1)
        if pkg not in seen:
            seen.append(pkg)
    return seen


def auto_install(code: str) -> str:
    """
    Scan code for imports and pip-install any missing packages.
    Uses sys.executable so it always installs into the active venv.
    Returns a summary of what was installed.
    """
    installed = []
    for name in _extract_imports(code):
        try:
            __import__(name)
            continue
        except ImportError:
            pass

        pip_name = IMPORT_TO_PIP.get(name, name)
        result   = subprocess.run(
            [sys.executable, "-m", "pip", "install", pip_name, "-q"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            installed.append(pip_name)
            print(f"[auto_install] Installed: {pip_name}")
        else:
            print(f"[auto_install] Failed to install {pip_name}: {result.stderr[:100]}")

    if not installed:
        return "All imports already available — no installs needed."
    return f"Installed: {', '.join(installed)}"

#  Core executor

def execute_python_script(code: str) -> str:
    """
    Execute Python code in an isolated subprocess.

    Uses sys.executable (always the active venv Python — not a hardcoded 'python3' which may point to a different installation).
    Auto-installs missing packages before running.
    Hard timeout: 30 seconds.
    """
    auto_install(code)

    # Define tmp_path before try so finally block can safely reference it
    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        output_section = stdout if stdout else "Script ran successfully (no output)."
        if result.returncode != 0:
            output_section = f"{stdout}\n[Errors]\n{stderr}" if stdout else f"[Errors]\n{stderr}"

        return (
            f"[CODE]\n{code}\n\n"
            f"[OUTPUT]\n{output_section}"
        )

    except subprocess.TimeoutExpired:
        return "[execute_python_script ERROR] Timed out after 30 seconds."
    except Exception as e:
        return f"[execute_python_script ERROR] {e}"
    finally:
        try:
            if tmp_path:
                os.unlink(tmp_path)
        except Exception:
            pass


#  Agent builder

def get_code_agent(model_client: ChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        name="Code_Agent",
        description="Writes and executes Python code. Auto-installs missing packages.",
        system_message="""\
You are the Code Agent. You write and run Python code.

YOUR TOOLS:
  execute_python_script(code)   → runs Python in a subprocess.
                                  Returns both [CODE] and [OUTPUT] sections.
                                  Missing packages are auto-installed before running.

RULES:
  1. Always call execute_python_script() — always run the code, never skip execution.
  2. Write COMPLETE, runnable code (imports included).
  3. Use print() for every result — that is the only thing captured in [OUTPUT].
  4. You can use any library: pandas, csv, statistics, numpy, etc.
     Missing packages will be installed automatically.
  5. If execution fails, read the error, fix the code, and retry.
  6. Never use '...' or placeholder comments in the code.

CSV DATA OUTPUT RULE — CRITICAL:
  If the task generates data that will be saved as a CSV in a later step,
  ALWAYS print the FULL dataset as a JSON array of dicts:

  CORRECT — File Agent can parse this:
    import json
    rows = [{"product": "Widget A", "price": 10.5, "quantity": 3}, ...]
    print(json.dumps(rows))

  WRONG — File Agent cannot parse these:
    print(df.to_string())       ← formatted string, not parseable
    print(df.head(10))          ← only 10 rows, truncated
    print(df)                   ← formatted string, not parseable

  Always print ALL rows, never truncate with head() when saving to CSV.

RESPONSE RULES — what to include in your final reply:
  - If the user asked to "show", "give", "write", "display", or "generate" code
    → Include the full [CODE] section in your reply AND the [OUTPUT].
  - If the user asked to "run", "execute", "calculate", or "analyse" something
    → Include only the [OUTPUT] section in your reply.
  - If a later pipeline step needs to save the code to a file
    → Always include the full [CODE] section so the File Agent can write it.
  - When in doubt, include both [CODE] and [OUTPUT].\
""",
        model_client=model_client,
        tools=[execute_python_script],
    )