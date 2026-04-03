from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient

def get_worker_agent(model_client: ChatCompletionClient, worker_id: int) -> AssistantAgent:
    return AssistantAgent(
        name=f"Worker_Agent_{worker_id}",
        description="Executes a specific subtask concurrently.",
        system_message=(
            "You are a specialized Worker Agent. Execute the specific subtask assigned to you "
            "quickly and accurately. Provide only the factual answer to your specific task. "
            "Do not attempt to answer the entire overarching query."
        ),
        model_client=model_client
    )