import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)              
sys.path.insert(0, parent_dir)
import asyncio
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from day5.nexus_ai.config import get_model_client, ACTIVE_PROVIDER
from day1.agents.research_agent import get_research_agent
from day1.agents.summarizer_agent import get_summarizer_agent
from day1.agents.answer_agent import get_answer_agent

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