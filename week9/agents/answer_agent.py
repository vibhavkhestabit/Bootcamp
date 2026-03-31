from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_core.models import ChatCompletionClient

def get_answer_agent(model_client: ChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        name="Answer_Agent",
        description="Responsible for formatting the final user-facing response.",
        system_message=(
            "You are the Answer Agent. Your strict role is to take the bulleted key points "
            "from the Summarizer_Agent and draft a polite, well-formatted, and cohesive final response "
            "for the user. Synthesize the points naturally so it does not just look like a list of bullets. "
            "This is the final output, so ensure the tone is helpful and professional, and directly "
            "addresses the user's original query."
        ),
        model_client=model_client,
        model_client_stream=True,
        model_context=BufferedChatCompletionContext(buffer_size=10)
    )