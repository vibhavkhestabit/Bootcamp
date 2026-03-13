from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_core.models import ChatCompletionClient

def get_research_agent(model_client: ChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        name="Research_Agent",
        description="Responsible for gathering raw information and facts.",
        system_message=(
            "You are the Research Agent. Your strict role is to gather accurate, raw information "
            "and facts based on the user's query. Provide detailed, factual data and context. "
            "Do not summarize. Do not include greetings, introductions, or conclusions. "
            "Output pure informational content to be processed by the next agent."
        ),
        model_client=model_client,
        model_context=BufferedChatCompletionContext(buffer_size=10)
    )