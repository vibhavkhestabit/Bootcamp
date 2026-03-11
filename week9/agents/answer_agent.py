from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_core.models import ChatCompletionClient

def get_answer_agent(model_client: ChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        name="Answer_Agent",
        description="Responsible for formatting the final user-facing response.",
        system_message=(
            "You are the Answer Agent. Your strict role is to take the summarized bullet points "
            "from the Summarizer_Agent and draft a polite, well-formatted, and cohesive final response "
            "for the user. This is the final output, so ensure the tone is helpful and professional."
        ),
        model_client=model_client,
        model_context=BufferedChatCompletionContext(buffer_size=10)
    )