import asyncio
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from nexus_ai.config import get_model_client, ACTIVE_PROVIDER
from agents.research_agent import get_research_agent
from agents.summarizer_agent import get_summarizer_agent
from agents.answer_agent import get_answer_agent

async def main():
    model_client = get_model_client()
    researcher = get_research_agent(model_client)
    summarizer = get_summarizer_agent(model_client)
    answerer   = get_answer_agent(model_client)
    pipeline_team = RoundRobinGroupChat(
        participants=[researcher, summarizer, answerer],
        max_turns=3
    )

    print("\n=== Day 1: Agent Pipeline ===")
    print(f"    Provider : {ACTIVE_PROVIDER.upper()}")
    print("    Agents   : Researcher · Summarizer · Answer")
    print("    Type 'exit' to quit.\n")

    while True:
        user_input = input("\nUser: ")

        if user_input.lower() in ("exit", "quit"):
            print("Shutting down pipeline...")
            break

        if not user_input.strip():
            continue

        await Console(pipeline_team.run_stream(task=user_input))

if __name__ == "__main__":
    asyncio.run(main())