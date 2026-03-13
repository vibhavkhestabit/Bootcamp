from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient

def get_validator_agent(model_client: ChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        name="Validator_Agent",
        description="Checks the final output for errors.",
        system_message=(
            "You are the Validator Agent. Review the provided response. If it contains obvious "
            "logical errors, contradictions, or incomplete sentences, fix them. If it looks correct, "
            "output the clean text as the final, polished answer for the user."
        ),
        model_client=model_client
    )