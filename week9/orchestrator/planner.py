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
                "You are the Orchestrator Planner. Your strict job is to break the user's query into highly specific, actionable research tasks for your workers. "
                "CRITICAL RULES: "
                "1. You MUST break the query into EXACTLY 3 distinct subtasks. "
                "2. The subtasks must be hyper-specific and include all constraints (dates, numbers, locations) from the user's prompt. "
                "3. Use this format: [Specific Action] for [Topic] ensuring [Constraints]. "
                "4. You MUST return them as a pipe-separated string (e.g., Research specific 5-star hotels for 4 people in Paris|Create a detailed day-by-day itinerary for 3 days in Paris). "
                "5. Do NOT output any other text, introductions, or formatting. Only the pipe-separated string."
            ),
            model_client=model_client
        )
        self.reflection_agent = get_reflection_agent(model_client)
        self.validator_agent = get_validator_agent(model_client)

    async def execute_tree(self, query: str):
        print("\n[DAG] Execution Tree Started")
        print(f" |--- User Query: {query}")
        
        plan_msg = TextMessage(content=query, source="user")
        plan_response = await self.planner_agent.on_messages([plan_msg], cancellation_token=None)
        
        subtasks = plan_response.chat_message.content.split("|")
        print(f" |--- Planner generated {len(subtasks)} parallel tasks.")
        
        print(f" |--- [Parallel Execution Initiated]")
        worker_coroutines = []
        for i, task in enumerate(subtasks):
            worker = get_worker_agent(self.model_client, worker_id=i+1)
            worker_msg = TextMessage(content=task.strip(), source="planner")
            print(f" |    |---Worker {i+1} assigned: {task.strip()}")
            worker_coroutines.append(worker.on_messages([worker_msg], cancellation_token=None))
        
        worker_results = await asyncio.gather(*worker_coroutines)
        
        combined_output = "\n\n".join([f"Worker {i+1}: {res.chat_message.content}" for i, res in enumerate(worker_results)])
        print(f" |---[Parallel Execution Completed]")
        
        print(" |--- Reflection Agent synthesizing results...")
        reflect_msg = TextMessage(content=f"Original Query: {query}\n\nWorker Outputs:\n{combined_output}", source="orchestrator")
        reflection_response = await self.reflection_agent.on_messages([reflect_msg], cancellation_token=None)
        
        print(" |--- Validator Agent checking constraints against original query...")
        
        validation_payload = (
            f"Original Query: {query}\n\n"
            f"Draft Response:\n{reflection_response.chat_message.content}"
        )
        
        valid_msg = TextMessage(content=validation_payload, source="reflection")
        validator_response = await self.validator_agent.on_messages([valid_msg], cancellation_token=None)
        
        print(" |___ Final Answer Delivered.\n")
        return validator_response.chat_message.content