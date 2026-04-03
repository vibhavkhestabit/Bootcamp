import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)              
sys.path.insert(0, parent_dir)
import asyncio
from dotenv import load_dotenv
load_dotenv()
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
import day4.memory.session_memory   as session
import day4.memory.long_term_memory as ltm
import day4.memory.vector_store     as vs
from day5_nexus_ai.config import get_model_client, ACTIVE_PROVIDER

def build_prompt(user_input: str) -> str:
    sections = []

    similar = vs.search(user_input, k=3)
    if similar:
        sections.append(vs.format_results(similar))

    episodes = ltm.format_episodes_for_prompt(n=3)
    if "No past" not in episodes:
        sections.append(episodes)

    facts = ltm.format_facts_for_prompt()
    if "No facts" not in facts:
        sections.append(facts)

    history = session.format_for_prompt(n=10)
    if "No conversation" not in history:
        sections.append(history)

    if sections:
        memory_block = "\n\n".join(sections)
        return f"{memory_block}\n\nUser query: {user_input}"
    else:
        return user_input

#  Fact extractor

FACT_KEYWORDS = [
    "my name is", "i am", "i work", "i like", "i prefer", "remember that", "don't forget", "my goal", "i want to", "i need", "always", "never", "my favourite", "i hate",
]

def extract_facts(user_input: str) -> list[str]:

    lowered = user_input.lower()
    for keyword in FACT_KEYWORDS:
        if keyword in lowered:
            return [user_input]
    return []

def save_session_to_long_term(session_log: list[dict]) -> None:

    if not session_log:
        print("[Memory] Nothing to save — session was empty.")
        return

    print(f"\n[Memory] Saving {len(session_log)} exchanges to long-term memory...")

    for exchange in session_log:
        user_msg   = exchange["user"]
        agent_reply = exchange["agent"]

        ltm.store_episode(user_msg=user_msg, agent_reply=agent_reply)

        facts = extract_facts(user_msg)
        for fact in facts:
            ltm.store_fact(content=fact, source="user", category="preference")
            print(f"[Memory] Stored fact: '{fact[:60]}'")

        vs.add_memory(
            text=f"User: {user_msg} | Agent: {agent_reply[:200]}",
            metadata={"type": "conversation"},
        )

    vs.save()
    print(f"[Memory] Saved to long_term.db and faiss.index successfully.")

AGENT_SYSTEM = """\
You are a helpful AI assistant with memory. You remember past conversations
and use that context to give better, more personalised responses.

When memory context is provided above your query, use it to:
- Recall what the user told you before
- Avoid asking for information already given
- Reference past conversations naturally
- Build on previous answers

Be concise, helpful, and context-aware.\
"""
async def main():
    ltm.init_db()
    vs.load()

    model_client = get_model_client()

    def create_agent():
        """Create a fresh agent with no internal history."""
        return AssistantAgent(
            name="Memory_Agent",
            description="A memory-aware assistant that recalls past context.",
            system_message=AGENT_SYSTEM,
            model_client=model_client,
        )

    agent = create_agent()
    session_log: list[dict] = []

    print("\n=== Day 4: Agent Memory System ===")
    print(f"    Provider  : {ACTIVE_PROVIDER.upper()}")
    print(f"    Session   : RAM only (saved to long-term on exit)")
    print(f"    Long-term : memory/long_term.db")
    print(f"    Vector    : memory/faiss.index")
    print("    Type 'exit' to save and quit.")
    print("    Type 'memory' to see memory stats.")
    print("    Type 'clear' to wipe session memory.\n")

    while True:
        try:
            user_input = input("\nUser: ").strip()
        except (EOFError, KeyboardInterrupt):
            save_session_to_long_term(session_log)
            print("\n[Shutting down]")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "q"):
            save_session_to_long_term(session_log)
            print("[Shutting down]")
            break

        if user_input.lower() == "memory":
            print("\n── Memory Stats ──")
            print(f"Session exchanges : {len(session_log)}")
            print(f"Session messages  : {session.session_stats()}")
            print(f"Long-term         : {ltm.memory_stats()}")
            print(f"Vector (saved)    : {vs.count()} memories in index")
            continue

        if user_input.lower() == "clear":
            session.clear()
            session_log.clear()
            agent = create_agent()  
            print("[Session memory cleared. Long-term memory untouched.]")
            print("[Note: This session's conversations will NOT be saved on exit.]")
            continue

        session.add_message("user", user_input)

        enriched_prompt = build_prompt(user_input)

        similar_count = len(vs.search(user_input, k=3)) if vs.count() > 0 else 0
        if similar_count > 0:
            print(f"[Memory] Found {similar_count} relevant past memories.")

        print("[Agent thinking...]\n")
        try:
            resp = await agent.on_messages(
                [TextMessage(content=enriched_prompt, source="user")],
                cancellation_token=None,
            )
            reply = resp.chat_message.content
            print(f"Agent: {reply}")

        except Exception as e:
            print(f"[ERROR] {e}")
            reply = f"[ERROR] {e}"

        session.add_message("assistant", reply)

        session_log.append({"user": user_input, "agent": reply})

        print("\n" + "─" * 50)

if __name__ == "__main__":
    asyncio.run(main())