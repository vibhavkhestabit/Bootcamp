
import streamlit as st
import asyncio
import os
import sys
from datetime import datetime

# ── Path setup ────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "nexus_ai"))

st.set_page_config(page_title="NEXUS AI", page_icon="⬡", layout="centered")

st.markdown("""
<style>
    .stApp { background: #0f0f0f; color: #e2e8f0; }
    .stTextInput input {
        background: #1a1a1a !important;
        color: #e2e8f0 !important;
        border: 1px solid #333 !important;
        border-radius: 6px !important;
        font-family: monospace !important;
    }
    .stButton button {
        background: #7c3aed !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
    }
    .user-bubble {
        background: #1e1e2e;
        border-left: 3px solid #7c3aed;
        padding: 12px 16px;
        border-radius: 6px;
        margin: 8px 0;
        font-size: 14px;
    }
    .nexus-bubble {
        background: #111827;
        border-left: 3px solid #06b6d4;
        padding: 12px 16px;
        border-radius: 6px;
        margin: 8px 0;
        font-size: 13px;
        font-family: monospace;
        white-space: pre-wrap;
    }
    .pipeline-info {
        font-size: 11px;
        color: #64748b;
        font-family: monospace;
        margin: 4px 0 10px 0;
    }
    .step-line {
        font-size: 11px;
        color: #64748b;
        font-family: monospace;
        padding: 2px 0;
    }
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
#  Session state
# ─────────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_log" not in st.session_state:
    st.session_state.session_log = []


# ─────────────────────────────────────────────────────────────────
#  Load NEXUS (cached)
# ─────────────────────────────────────────────────────────────────

@st.cache_resource
def load_nexus():
    try:
        os.chdir(ROOT)
        import config
        from config import get_model_client
        from nexus_ai.agents import build_all_agents
        import memory.long_term_memory as ltm
        import memory.vector_store as vs
        import memory.session_memory as session

        os.makedirs(config.MEMORY_DIR, exist_ok=True)
        os.makedirs(config.LOGS_DIR, exist_ok=True)
        ltm.init_db()
        vs.load(directory=config.MEMORY_DIR)
        model_client = get_model_client()
        agents = build_all_agents(model_client)

        return {
            "ok": True,
            "agents": agents,
            "ltm": ltm,
            "vs": vs,
            "session": session,
            "config": config,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ─────────────────────────────────────────────────────────────────
#  Run pipeline
# ─────────────────────────────────────────────────────────────────

def run_query(user_input: str, nexus: dict) -> dict:

    async def _run():
        from autogen_agentchat.messages import TextMessage
        from nexus_ai.main import parse_plan, build_memory_context, save_report
        import config

        agents  = nexus["agents"]
        session = nexus["session"]
        MAX_C   = config.MAX_REFLECTION_CYCLES
        MAX_S   = config.MAX_PLAN_STEPS

        session.add_message("user", user_input)
        memory_context = build_memory_context(user_input)

        # Orchestrator
        orch_prompt = (
            f"{memory_context}"
            f"User task: {user_input}\n\n"
            f"Output a JSON execution plan using the available agents."
        )
        orch_resp = await agents["ORCHESTRATOR"].on_messages(
            [TextMessage(content=orch_prompt, source="user")],
            cancellation_token=None,
        )
        plan = parse_plan(orch_resp.chat_message.content)[:MAX_S]

        all_outputs = []
        step_log    = []
        reflection_count = 0

        for step in plan:
            agent_key = step["agent"].upper()
            task      = step["task"]
            if agent_key not in agents:
                continue

            if all_outputs:
                history  = "\n\n".join(all_outputs)
                enriched = f"{task}\n\n--- Outputs from all previous steps ---\n{history}"
            else:
                if memory_context:
                    enriched = f"{task}\n\n--- Memory Context (use this to answer) ---\n{memory_context}"
                else:
                    enriched = task

            try:
                resp   = await agents[agent_key].on_messages(
                    [TextMessage(content=enriched, source="user")],
                    cancellation_token=None,
                )
                result = resp.chat_message.content
                all_outputs.append(f"[Step {step['step']} — {agent_key}]\n{result}")
                step_log.append(f"Step {step['step']} → [{agent_key}]")

                # Reflection
                if agent_key == "CRITIC" and reflection_count < MAX_C:
                    pre   = all_outputs[-2] if len(all_outputs) >= 2 else ""
                    o_task = (
                        f"Improve the following output based on the Critic's feedback.\n\n"
                        f"Original:\n{pre}\n\nCritic feedback:\n{result}"
                    )
                    o_resp = await agents["OPTIMIZER"].on_messages(
                        [TextMessage(content=o_task, source="user")],
                        cancellation_token=None,
                    )
                    o_out = o_resp.chat_message.content
                    all_outputs.append(f"[Reflection {reflection_count+1} — OPTIMIZER]\n{o_out}")
                    step_log.append(f"  ↳ Reflection {reflection_count+1} → [OPTIMIZER]")
                    reflection_count += 1

            except Exception as e:
                step_log.append(f"Step {step['step']} → [{agent_key}] ❌ ERROR: {e}")

        # Extract final output
        final = ""
        for output in reversed(all_outputs):
            if "REPORTER" in output:
                final = output.split("\n", 1)[1] if "\n" in output else output
                break
        if not final:
            final = all_outputs[-1] if all_outputs else "No output generated."
        if final.startswith("[Step") and "\n" in final:
            final = final.split("\n", 1)[1]

        # Save report if Reporter ran
        reporter_ran = any("REPORTER" in s for s in step_log)
        report_path  = None
        if reporter_ran:
            report_path = save_report(user_input, final)

        session.add_message("assistant", final[:500])
        st.session_state.session_log.append({"task": user_input, "report": final})

        return {
            "plan":        plan,
            "step_log":    step_log,
            "final":       final,
            "report_path": report_path,
        }

    return asyncio.run(_run())


# ─────────────────────────────────────────────────────────────────
#  UI
# ─────────────────────────────────────────────────────────────────

nexus = load_nexus()

# Header
st.markdown("## ⬡ NEXUS AI")
if nexus["ok"]:
    st.markdown(
        f'<span style="font-family:monospace;font-size:11px;color:#10b981">● System Ready &nbsp;·&nbsp; '
        f'Provider: GEMINI &nbsp;·&nbsp; '
        f'Memory: {nexus["vs"].count()} vectors</span>',
        unsafe_allow_html=True
    )
else:
    st.error(f"Failed to load NEXUS AI: {nexus['error']}")
    st.stop()

st.divider()

# Chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="user-bubble"><b>You</b><br>{msg["content"]}</div>',
            unsafe_allow_html=True
        )
    else:
        # Pipeline steps
        if msg.get("step_log"):
            steps_txt = "\n".join(msg["step_log"])
            st.markdown(
                f'<div class="pipeline-info">{steps_txt}</div>',
                unsafe_allow_html=True
            )
        # Answer
        st.markdown(
            f'<div class="nexus-bubble">{msg["content"]}</div>',
            unsafe_allow_html=True
        )
        # Report saved
        if msg.get("report_path"):
            st.markdown(
                f'<div class="step-line">📄 Report saved → {msg["report_path"]}</div>',
                unsafe_allow_html=True
            )

st.divider()

# Input
col1, col2, col3 = st.columns([6, 1, 1])
with col1:
    user_input = st.text_input(
        "input",
        placeholder="Ask NEXUS AI...",
        label_visibility="collapsed",
        key="user_input",
    )
with col2:
    send = st.button("Send")
with col3:
    if st.button("Clear"):
        st.session_state.messages = []
        st.session_state.session_log = []
        nexus["session"].clear()
        st.rerun()

# Memory save on exit hint
with st.expander("💾 Save session to long-term memory"):
    if st.button("Save & Exit"):
        if st.session_state.session_log:
            for exchange in st.session_state.session_log:
                nexus["ltm"].store_episode(exchange["task"], exchange["report"][:500])
                nexus["vs"].add_memory(
                    text=f"Task: {exchange['task']} | Summary: {exchange['report'][:300]}",
                    metadata={"type": "nexus_task"},
                )
            nexus["vs"].save(directory=nexus["config"].MEMORY_DIR)
            st.success(f"✅ Saved {len(st.session_state.session_log)} exchanges to long-term memory.")
        else:
            st.info("Nothing to save.")

# Handle send
if send and user_input.strip():
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
    })

    with st.spinner("⬡ NEXUS AI thinking..."):
        try:
            result = run_query(user_input, nexus)
            st.session_state.messages.append({
                "role":        "assistant",
                "content":     result["final"],
                "step_log":    result["step_log"],
                "report_path": result.get("report_path"),
            })
        except Exception as e:
            st.session_state.messages.append({
                "role":    "assistant",
                "content": f"[ERROR] {e}",
                "step_log": [],
            })

    st.rerun()