import asyncio
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient

from agents.worker_agent import get_worker_agent
from agents.reflection_agent import get_reflection_agent
from agents.validator import get_validator_agent

class DAGOrchestrator:
    def __init__(self, model_client: ChatCompletionClient):
        self.model_client = model_client
        self.planner_agent = AssistantAgent(
            name="Planner_Agent",
            system_message=(
                "You are the Orchestrator Planner. Break the user query into exactly 2 distinct "
                "subtasks that can be executed in parallel by different workers. "
                "CRITICAL: Return them as a pipe-separated string (e.g., Subtask 1|Subtask 2). "
                "Do not add any other text, introductions, or formatting."
            ),
            model_client=model_client
        )
        self.reflection_agent = get_reflection_agent(model_client)
        self.validator_agent = get_validator_agent(model_client)

    async def execute_tree(self, query: str):
        print("\n[DAG] Execution Tree Started")
        print(f" ├── User Query: {query}")
        
        # 1. Planning Phase (Sequential)
        plan_msg = TextMessage(content=query, source="user")
        plan_response = await self.planner_agent.on_messages([plan_msg], cancellation_token=None)
        
        # Parse the pipe-separated string into a list of tasks
        subtasks = plan_response.chat_message.content.split("|")
        print(f" ├── Planner generated {len(subtasks)} parallel tasks.")
        
        # 2. Worker Phase (PARALLEL EXECUTION)
        print(f" ├── [Parallel Execution Initiated]")
        worker_coroutines = []
        for i, task in enumerate(subtasks):
            worker = get_worker_agent(self.model_client, worker_id=i+1)
            worker_msg = TextMessage(content=task.strip(), source="planner")
            print(f" │    ├── Worker {i+1} assigned: {task.strip()}")
            # Add to asyncio event loop without awaiting immediately
            worker_coroutines.append(worker.on_messages([worker_msg], cancellation_token=None))
        
        # Await all workers simultaneously
        worker_results = await asyncio.gather(*worker_coroutines)
        
        combined_output = "\n\n".join([f"Worker {i+1}: {res.chat_message.content}" for i, res in enumerate(worker_results)])
        print(f" ├── [Parallel Execution Completed]")
        
        # 3. Reflection Phase (Sequential)
        print(" ├── Reflection Agent synthesizing results...")
        reflect_msg = TextMessage(content=f"Original Query: {query}\n\nWorker Outputs:\n{combined_output}", source="orchestrator")
        reflection_response = await self.reflection_agent.on_messages([reflect_msg], cancellation_token=None)
        
        # 4. Validator Phase (Sequential)
        print(" ├── Validator Agent checking for errors...")
        valid_msg = TextMessage(content=reflection_response.chat_message.content, source="reflection")
        validator_response = await self.validator_agent.on_messages([valid_msg], cancellation_token=None)
        
        print(" └── Final Answer Delivered.\n")
        return validator_response.chat_message.content