from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient

def get_reflection_agent(model_client: ChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        name="Reflection_Agent",
        description="Synthesizes parallel worker outputs.",
        system_message=(
            "You are the Reflection Agent. Take the fragmented outputs from multiple parallel "
            "workers and synthesize them into a single, cohesive, and logically flowing response "
            "that answers the user's original query."
        ),
        model_client=model_client
    )