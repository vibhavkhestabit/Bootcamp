import asyncio
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Import your agents
from agents.research_agent import get_research_agent
from agents.summarizer_agent import get_summarizer_agent
from agents.answer_agent import get_answer_agent

async def main():
    # Define the local model client (Ollama running Mistral)
    model_client = OpenAIChatCompletionClient(
        model="mistral",
        base_url="http://localhost:11434/v1",
        api_key="NotRequired"
    )

    # Instantiate the 3 distinct agents
    researcher = get_research_agent(model_client)
    summarizer = get_summarizer_agent(model_client)
    answerer = get_answer_agent(model_client)

    # Create a linear pipeline using a RoundRobin team.
    # We pass the participants in the exact order we want them to act.
    # max_turns=3 ensures we get exactly one pass through the pipeline:
    # Task -> Researcher -> Summarizer -> Answerer -> Stop
    pipeline_team = RoundRobinGroupChat(
        participants=[researcher, summarizer, answerer],
        max_turns=3 
    )

    task = "Find out how the ReAct pattern works in AI agents, summarize it, and explain it to me."
    
    print("Initiating Day 1 Agent Pipeline...\n")
    # The Console UI will stream the handoffs in the terminal
    await Console(pipeline_team.run_stream(task=task))

if __name__ == "__main__":
    asyncio.run(main())