import asyncio
import json
import os
import re
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from autogen_agentchat.messages import TextMessage

from day5_nexus_ai import config
from day5_nexus_ai.config import get_model_client, MAX_REFLECTION_CYCLES, MAX_PLAN_STEPS
from day5_nexus_ai.agents import build_all_agents
from day5_nexus_ai.logger import (
    log_task, log_plan, log_agent_start, log_agent_result,
    log_reflection, log_memory, log_error, log_complete, log_session_info
)

import day4.memory.session_memory   as session
import day4.memory.long_term_memory as ltm
import day4.memory.vector_store     as vs

def parse_plan(raw: str) -> list:
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    try:
        plan = json.loads(raw)
        if isinstance(plan, list):
            return plan
    except json.JSONDecodeError:
        pass

    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    print("[Orchestrator] Could not parse plan — defaulting to RESEARCHER.")
    return [{"step": 1, "agent": "RESEARCHER", "task": raw}]

def build_memory_context(user_input: str) -> str:
    """Pull relevant context from all memory layers."""
    sections = []

    if vs.count() > 0:
        similar = vs.search(user_input, k=3)
        if similar:
            sections.append(vs.format_results(similar))
            log_memory("vector_recall", f"Found {len(similar)} similar memories")
        else:
            log_memory("vector_recall", "Empty — no similar memories found")
    else:
        log_memory("vector_recall", "Empty — no saved index")

    episodes = ltm.format_episodes_for_prompt(n=2)
    if "No past" not in episodes:
        sections.append(episodes)
        log_memory("sqlite_episodes", "Injected 2 past episodes")
    else:
        log_memory("sqlite_episodes", "Empty — no past episodes")

    facts = ltm.format_facts_for_prompt()
    if "No facts" not in facts:
        sections.append(facts)
        log_memory("sqlite_facts", "Injected stored facts")
    else:
        log_memory("sqlite_facts", "Empty — no facts stored")

    history = session.format_for_prompt(n=10)
    if "No conversation" not in history:
        sections.append(history)
        log_memory("session_ram", "Injected recent session history")
    else:
        log_memory("session_ram", "Empty — fresh session")

    if sections:
        return "\n\n".join(sections) + "\n\n"
    return ""

FACT_KEYWORDS = [
    "my name is", "i am", "i work", "i like", "i prefer", "remember that", "don't forget", "my goal", "i want to", "i need", "always", "never", "my favourite", "i hate",
]

def extract_facts(user_input: str) -> list[str]:
    lowered = user_input.lower()
    for keyword in FACT_KEYWORDS:
        if keyword in lowered:
            return [user_input]
    return []

async def run_pipeline(
    user_input: str,
    agents: dict,
    memory_context: str,
) -> tuple:
    
    print("\n[Orchestrator planning...]")
    orch_prompt = (
        f"{memory_context}"
        f"User task: {user_input}\n\n"
        f"Output a JSON execution plan using the available agents."
    )

    try:
        orch_resp = await agents["ORCHESTRATOR"].on_messages(
            [TextMessage(content=orch_prompt, source="user")],
            cancellation_token=None,
        )
        raw_plan = orch_resp.chat_message.content
        plan = parse_plan(raw_plan)
        plan = plan[:MAX_PLAN_STEPS]
    except Exception as e:
        log_error(0, "ORCHESTRATOR", str(e))
        plan = [
            {"step": 1, "agent": "RESEARCHER", "task": user_input},
        ]

    log_plan(plan)

    all_outputs = []
    reflection_count = 0

    for step in plan:
        agent_key = step["agent"].upper()
        task      = step["task"]

        if agent_key not in agents:
            print(f"  [WARNING] Unknown agent '{agent_key}' — skipping.")
            continue

        log_agent_start(step["step"], agent_key, task)

        if all_outputs:

            history = "\n\n".join(all_outputs)
            enriched_task = (
                f"{task}\n\n"
                f"--- Outputs from all previous steps ---\n{history}"
            )
        else:
            if memory_context:
                enriched_task = (
                    f"{task}\n\n"
                    f"--- Memory Context (use this to answer) ---\n"
                    f"{memory_context}"
                )
            else:
                enriched_task = task

        try:
            resp = await agents[agent_key].on_messages(
                [TextMessage(content=enriched_task, source="user")],
                cancellation_token=None,
            )
            result = resp.chat_message.content
            log_agent_result(step["step"], agent_key, result, success=True)
            all_outputs.append(f"[Step {step['step']} — {agent_key}]\n{result}")

            if agent_key == "CRITIC" and reflection_count < MAX_REFLECTION_CYCLES:
                critic_output = result
                pre_critic = all_outputs[-2] if len(all_outputs) >= 2 else ""

                optimizer_task = (
                    f"Improve the following output based on the Critic's feedback.\n\n"
                    f"Original output:\n{pre_critic}\n\n"
                    f"Critic feedback:\n{critic_output}"
                )

                log_agent_start(step["step"], "OPTIMIZER", optimizer_task[:100])
                opt_resp = await agents["OPTIMIZER"].on_messages(
                    [TextMessage(content=optimizer_task, source="user")],
                    cancellation_token=None,
                )
                optimizer_output = opt_resp.chat_message.content
                log_agent_result(step["step"], "OPTIMIZER", optimizer_output)
                log_reflection(reflection_count + 1, critic_output, optimizer_output)
                all_outputs.append(
                    f"[Reflection {reflection_count+1} — OPTIMIZER]\n{optimizer_output}"
                )
                reflection_count += 1

        except Exception as e:
            err = f"[ERROR] {e}"
            log_error(step["step"], agent_key, str(e))
            all_outputs.append(f"[Step {step['step']} — {agent_key} FAILED]\n{err}")
            print(f"  [Recovery] {agent_key} failed — continuing with remaining steps.")

    final_report = ""
    for output in reversed(all_outputs):
        if "REPORTER" in output:
            final_report = output.split("\n", 1)[1] if "\n" in output else output
            break

    if not final_report:
        final_report = all_outputs[-1] if all_outputs else "No output generated."

    return final_report, all_outputs, plan

def save_report(task: str, report: str) -> str:
    from datetime import datetime
    os.makedirs(config.LOGS_DIR, exist_ok=True)
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name   = re.sub(r'[^a-z0-9]+', '_', task.lower())[:40]
    report_path = os.path.join(config.LOGS_DIR, f"report_{safe_name}_{timestamp}.md")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# NEXUS AI Report\n\n")
        f.write(f"**Task:** {task}\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        f.write(report)

    return report_path

# Main loop 

async def main():
    os.makedirs(config.MEMORY_DIR, exist_ok=True)
    os.makedirs(config.LOGS_DIR, exist_ok=True)
    ltm.init_db()
    vs.load() 

    model_client = get_model_client()
    agents = build_all_agents(model_client)
    session_log: list[dict] = []

    info = log_session_info()
    print("\n" + "="*60)
    print("  PROJECT: NEXUS AI")
    print("  Autonomous Multi-Agent AI System")
    print("="*60)
    print(f"  Provider : {config.ACTIVE_PROVIDER.upper()}")
    print(f"  Agents   : Orchestrator · Planner · Researcher · Coder")
    print(f"           : Analyst · Critic · Optimizer · Validator · Reporter")
    print(f"  Memory   : Session + Long-term + Vector")
    print(f"  Log file : {info['log_file']}")
    print(f"  Traces   : {info['trace_file']}")
    print("="*60)
    print("  Type 'exit' to save and quit.")
    print("  Type 'memory' to see memory stats.")
    print("  Type 'clear' to reset session.\n")

    while True:
        try:
            user_input = input("\nNEXUS > ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            if session_log:
                print(f"\n[Memory] Saving {len(session_log)} exchanges...")
                for exchange in session_log:
                    ltm.store_episode(exchange["task"], exchange["report"][:500])
                    
                    facts = extract_facts(exchange["task"])
                    for fact in facts:
                        ltm.store_fact(content=fact, source="user", category="preference")
                        print(f"  [Memory] Stored fact: '{fact[:60]}'")

                    vs.add_memory(
                        text=f"Task: {exchange['task']} | Summary: {exchange['report'][:300]}",
                        metadata={"type": "nexus_task"},
                    )
                
                vs.save()
                print("[Memory] Saved to long-term memory.")
            else:
                print("[Memory] Nothing to save.")
            print("[NEXUS AI Shutting down]")
            break

        if user_input.lower() == "memory":
            print("\n── NEXUS Memory Stats ──")
            print(f"  Session tasks  : {len(session_log)}")
            print(f"  Long-term      : {ltm.memory_stats()}")
            print(f"  Vector index   : {vs.count()} memories")
            continue

        if user_input.lower() == "clear":
            session.clear()
            session_log.clear()
            agents = build_all_agents(model_client)
            print("[Session cleared. Long-term memory untouched.]")
            continue

        log_task(user_input)
        session.add_message("user", user_input)

        memory_context = build_memory_context(user_input)

        try:
            final_report, all_outputs, plan = await run_pipeline(
                user_input=user_input,
                agents=agents,
                memory_context=memory_context,
            )
            reporter_ran = any(
                step.get("agent", "").upper() == "REPORTER"
                for step in plan
            )

            if reporter_ran:
                report_path = save_report(user_input, final_report)
                log_complete(user_input, report_path)
                print(f"\n Report saved to: {report_path}")
            else:
                log_complete(user_input, "direct answer — no report saved")
                print(f"\n Done.")

            session.add_message("assistant", final_report[:500])
            session_log.append({
                "task":   user_input,
                "report": final_report,
            })

        except Exception as e:
            log_error(0, "PIPELINE", str(e))
            print(f"\n[NEXUS ERROR] {e}")

        print("\n" + "─"*60)

if __name__ == "__main__":
    asyncio.run(main())