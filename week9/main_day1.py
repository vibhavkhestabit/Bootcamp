import asyncio
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Import your agents
from agents.research_agent import get_research_agent
from agents.summarizer_agent import get_summarizer_agent
from agents.answer_agent import get_answer_agent

async def main():
    # Define the local model client
    model_client = OpenAIChatCompletionClient(
        model="mistral",
        base_url="http://localhost:11434/v1",
        api_key="NotRequired",
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": False,
            "family": "unknown",
        }
    )

    # Instantiate the 3 distinct agents outside the loop so they retain memory
    researcher = get_research_agent(model_client)
    summarizer = get_summarizer_agent(model_client)
    answerer = get_answer_agent(model_client)

    # Create a linear pipeline using a RoundRobin team
    pipeline_team = RoundRobinGroupChat(
        participants=[researcher, summarizer, answerer],
        max_turns=3 
    )

    print("Initiating Day 1 Agent Pipeline (Type 'exit' to quit)...\n")
    
    # Interactive CLI Loop
    while True:
        user_input = input("\nUser: ")
        
        if user_input.lower() in ['exit', 'quit']:
            print("Shutting down pipeline...")
            break
            
        if not user_input.strip():
            continue
        await Console(pipeline_team.run_stream(task=user_input))

if __name__ == "__main__":
    asyncio.run(main())