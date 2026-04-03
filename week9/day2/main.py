import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)              
sys.path.insert(0, parent_dir)
import asyncio
from day5_nexus_ai.config import get_model_client, ACTIVE_PROVIDER
from day2.orchestrator.planner import DAGOrchestrator

async def main():
    model_client = get_model_client()

    orchestrator = DAGOrchestrator(model_client)

    print("\n=== Day 2: Multi-Agent DAG Orchestrator ===")
    print(f"    Provider : {ACTIVE_PROVIDER.upper()}")
    print("    Type 'exit' to quit.\n")

    while True:
        user_query = input("User: ")

        if user_query.lower() in ("exit", "quit"):
            print("Shutting down Orchestrator...")
            break

        if not user_query.strip():
            continue

        final_answer = await orchestrator.execute_tree(user_query)

        print(f"\n[Final Output]\n{final_answer}\n")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())