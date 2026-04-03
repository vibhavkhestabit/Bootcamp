from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient

def get_validator_agent(model_client: ChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        name="Validator_Agent",
        description="Strict QA engineer that checks the final output against original constraints.",
        system_message=(
            "You are the final Validator Agent. Your strict role is Quality Assurance. "
            "You will be provided with the 'Original Query' and the 'Draft Response'. "
            "1. You MUST cross-check the Draft Response against every specific constraint in the Original Query (e.g., exact number of days, item counts, specific locations). "
            "2. If the Draft Response misses a numerical constraint (like providing 5 days instead of 6), you must generate the missing information and fix the output. "
            "3. Return ONLY the final, corrected text for the user. Do not explain your edits."
        ),
        model_client=model_client
    )