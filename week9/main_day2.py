import asyncio
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Import the custom DAG Orchestrator we built
from orchestrator.planner import DAGOrchestrator

async def main():
    # Define the local model client (Ollama running Mistral)
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

    # Initialize the Orchestrator
    orchestrator = DAGOrchestrator(model_client)

    print("\n=== Day 2: Multi-Agent DAG Orchestrator ===")
    print("Type 'exit' or 'quit' to shut down.\n")

    # Interactive CLI Loop
    while True:
        user_query = input("User: ")
        
        if user_query.lower() in ['exit', 'quit']:
            print("Shutting down Orchestrator...")
            break
            
        if not user_query.strip():
            continue
            
        # Execute the parallel task graph
        final_answer = await orchestrator.execute_tree(user_query)
        
        print(f"\n[Final Output]\n{final_answer}\n")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())