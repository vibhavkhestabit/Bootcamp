from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_core.models import ChatCompletionClient

def get_summarizer_agent(model_client: ChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        name="Summarizer_Agent",
        description="Responsible for condensing raw information into key points.",
        system_message=(
            "You are the Summarizer Agent. Your strict role is to take the raw, unstructured "
            "information provided by the Research_Agent and condense it into concise, bulleted key points. "
            "Do not add any external information that was not explicitly provided by the Research_Agent."
        ),
        model_client=model_client,
        model_context=BufferedChatCompletionContext(buffer_size=10)
    )