import os
from dotenv import load_dotenv
load_dotenv()

# ─────────────────────────────────────────────────────────────────
#  Model Configuration
# ─────────────────────────────────────────────────────────────────

ACTIVE_PROVIDER = "gemini"   # "ollama" | "gemini"

OLLAMA_MODEL    = "qwen2.5"
OLLAMA_BASE_URL = "http://localhost:11434"

GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL    = "gemini-3.1-flash-lite-preview"

# ─────────────────────────────────────────────────────────────────
#  Paths
# ─────────────────────────────────────────────────────────────────

LOGS_DIR         = "logs"
MEMORY_DIR       = "memory"
NEXUS_DB_PATH    = os.path.join(MEMORY_DIR, "nexus.db")

# ─────────────────────────────────────────────────────────────────
#  Agent Pipeline Configuration
# ─────────────────────────────────────────────────────────────────

# How many Critic → Optimizer cycles to allow per task
MAX_REFLECTION_CYCLES = 2

# Max steps the Orchestrator can plan
MAX_PLAN_STEPS = 10

# ─────────────────────────────────────────────────────────────────
#  Agent Roster — used by Orchestrator to pick agents
# ─────────────────────────────────────────────────────────────────

AGENT_ROSTER = {
    "PLANNER":    "Breaks the task into detailed ordered steps",
    "RESEARCHER": "Gathers background knowledge and context",
    "CODER":      "Writes and executes Python code",
    "ANALYST":    "Analyses data, finds patterns, draws conclusions",
    "CRITIC":     "Reviews output and finds weaknesses",
    "OPTIMIZER":  "Improves output based on Critic feedback",
    "VALIDATOR":  "Checks final output for correctness and completeness",
    "REPORTER":   "Formats everything into a polished final report",
}

# ─────────────────────────────────────────────────────────────────
#  Model client factory
# ─────────────────────────────────────────────────────────────────

def get_model_client():
    if ACTIVE_PROVIDER == "ollama":
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        print(f"[Model] LOCAL Ollama → {OLLAMA_MODEL}")
        return OpenAIChatCompletionClient(
            model=OLLAMA_MODEL,
            base_url=f"{OLLAMA_BASE_URL}/v1",
            api_key="NotRequired",
            model_info={
                "vision": False,
                "function_calling": True,
                "json_output": True,
                "family": "unknown",
                "structured_output": True,
            }
        )

    elif ACTIVE_PROVIDER == "gemini":
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found. Add it to your .env file.")
        print(f"[Model] Gemini API → {GEMINI_MODEL}")
        return OpenAIChatCompletionClient(
            model=GEMINI_MODEL,
            api_key=GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            model_capabilities={
                "vision": False,
                "function_calling": True,
                "json_output": True,
                "family": "unknown",
                "structured_output": True,
            },
        )

    else:
        raise ValueError(f"Unknown provider '{ACTIVE_PROVIDER}'.")