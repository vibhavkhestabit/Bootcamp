import os
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient

def read_file(file_path: str) -> str:
    """Reads the text content of a file from the local filesystem and returns it as a string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(content: str, file_path: str) -> str:
    """Writes text content to a local file. Creates the file if it does not exist."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Success: Wrote content to {file_path}"
    except Exception as e:
        return f"Error writing file: {e}"

def get_file_agent(model_client: ChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        name="File_Agent",
        description="An agent that can read and write local files.",
        system_message=(
            "You are the File Operations Agent.\n\n"

            "Rules:\n"
            "1. For reading files → use read_file(file_path).\n"
            "2. For creating/writing files → use write_file(content, file_path).\n"
            "3. NEVER use write_file when user wants to read.\n"
            "4. ALWAYS provide BOTH content and file_path when writing.\n"
            "5. For CSV/data → generate complete data, no '...' or placeholders.\n"
            "6. Do NOT explain anything, just call the correct tool.\n"
        ),
        model_client=model_client,
        tools=[read_file, write_file]
    )