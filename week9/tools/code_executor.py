import subprocess
import tempfile
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient


def execute_python_script(code: str) -> str:
    """
    Executes Python code.
    - Uses direct terminal execution for small code
    - Falls back to temp file for larger/multi-line scripts
    """
    try:
        # Decide execution strategy
        if len(code) < 800:
            # Fast path (no file creation)
            result = subprocess.run(
                ["python3", "-c", code],
                capture_output=True,
                text=True,
                timeout=15
            )
        else:
            # Safe fallback for larger scripts
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as f:
                f.write(code)
                temp_path = f.name

            result = subprocess.run(
                ["python3", temp_path],
                capture_output=True,
                text=True,
                timeout=15
            )

            os.remove(temp_path)

        output = result.stdout.strip()
        error = result.stderr.strip()

        # Combine output + errors cleanly
        if error:
            return f"{output}\nErrors:\n{error}" if output else f"Errors:\n{error}"

        return output if output else "Script executed successfully with no console output."

    except Exception as e:
        return f"Critical Execution error: {e}"


def get_code_agent(model_client: ChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        name="Code_Agent",
        description="An agent that writes and runs Python scripts to analyze data or generate results.",
        system_message=(
            "You are a Python Data Scientist.\n\n"

            "Your job is to write CORRECT, COMPLETE, and EXECUTABLE Python code.\n\n"

            "CRITICAL RULES:\n"
            "1. ALWAYS write FULL working code (include imports and function definitions).\n"
            "2. ALWAYS ensure correct syntax (indentation, colons, loops).\n"
            "3. ALWAYS include print statements to display final results.\n"
            "4. If the user asks ONLY for code → return code ONLY (no tool call).\n"
            "5. If the user asks for result/computation → use `execute_python_script`.\n"
            "6. NEVER call the tool with incomplete code.\n"
            "7. NEVER use placeholders like '...' or '[...]'.\n"
            "8. If execution fails → fix and retry.\n"
            "9. Think step-by-step before writing code.\n"
        ),
        model_client=model_client,
        tools=[execute_python_script]
    )