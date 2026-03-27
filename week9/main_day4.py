import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
import memory.session_memory   as session
import memory.long_term_memory as ltm
import memory.vector_store     as vs
from nexus_ai.config import get_model_client, ACTIVE_PROVIDER

#  Memory-aware prompt builder

def build_prompt(user_input: str) -> str:
    sections = []

    # ── Vector memory: semantic recall ────────────────────────────
    similar = vs.search(user_input, k=3)
    if similar:
        sections.append(vs.format_results(similar))

    # ── Long-term: past episodes ──────────────────────────────────
    episodes = ltm.format_episodes_for_prompt(n=3)
    if "No past" not in episodes:
        sections.append(episodes)

    # ── Long-term: stored facts ───────────────────────────────────
    facts = ltm.format_facts_for_prompt()
    if "No facts" not in facts:
        sections.append(facts)

    # ── Session: recent conversation ──────────────────────────────
    history = session.format_for_prompt(n=6)
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

#  Save session to long-term memory (called only on exit)

def save_session_to_long_term(session_log: list[dict]) -> None:

    if not session_log:
        print("[Memory] Nothing to save — session was empty.")
        return

    print(f"\n[Memory] Saving {len(session_log)} exchanges to long-term memory...")

    for exchange in session_log:
        user_msg   = exchange["user"]
        agent_reply = exchange["agent"]

        # Save as episode
        ltm.store_episode(user_msg=user_msg, agent_reply=agent_reply)

        # Save facts if present
        facts = extract_facts(user_msg)
        for fact in facts:
            ltm.store_fact(content=fact, source="user", category="preference")
            print(f"[Memory] Stored fact: '{fact[:60]}'")

        # Save to vector store
        vs.add_memory(
            text=f"User: {user_msg} | Agent: {agent_reply[:200]}",
            metadata={"type": "conversation"},
        )

    # Persist FAISS index to disk
    vs.save(directory="memory")
    print(f"[Memory] Saved to long_term.db and faiss.index successfully.")

#  Main loop

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
    # ── Initialise all memory layers ─────────────────────────────
    ltm.init_db()
    vs.load(directory="memory")   # load saved FAISS index if exists

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
    # session_log holds this session's exchanges — saved to long-term on exit
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

        # ── Exit: save session then quit ──────────────────────────
        if user_input.lower() in ("exit", "quit", "q"):
            save_session_to_long_term(session_log)
            print("[Shutting down]")
            break

        # ── Memory stats ──────────────────────────────────────────
        if user_input.lower() == "memory":
            print("\n── Memory Stats ──")
            print(f"Session exchanges : {len(session_log)}")
            print(f"Session messages  : {session.session_stats()}")
            print(f"Long-term         : {ltm.memory_stats()}")
            print(f"Vector (saved)    : {vs.count()} memories in index")
            continue

        # ── Clear: wipe session RAM only ──────────────────────────
        if user_input.lower() == "clear":
            session.clear()
            session_log.clear()
            agent = create_agent()   # recreate agent to wipe its internal history
            print("[Session memory cleared. Long-term memory untouched.]")
            print("[Note: This session's conversations will NOT be saved on exit.]")
            continue

        # ── Step 1: Store user message in session RAM ─────────────
        session.add_message("user", user_input)

        # ── Step 2: Build memory-enriched prompt ──────────────────
        enriched_prompt = build_prompt(user_input)

        similar_count = len(vs.search(user_input, k=3)) if vs.count() > 0 else 0
        if similar_count > 0:
            print(f"[Memory] Found {similar_count} relevant past memories.")

        # ── Step 3: Run agent ─────────────────────────────────────
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

        # ── Step 4: Store reply in session RAM ────────────────────
        session.add_message("assistant", reply)

        # ── Step 5: Add to session log (saved to long-term on exit)
        session_log.append({"user": user_input, "agent": reply})

        print("\n" + "─" * 50)

if __name__ == "__main__":
    asyncio.run(main())