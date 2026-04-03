import streamlit as st
import asyncio
import os
import sys
from datetime import datetime

# ─────────────────────────────────────────────────────────────────
#  Absolute Pathing Setup
# ─────────────────────────────────────────────────────────────────
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir) # points to week9/
sys.path.insert(0, parent_dir)

st.set_page_config(
    page_title="NEXUS AI",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: #f5f6fa !important;
    color: #1c1c2e !important;
}

[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e4e6ef !important;
}
[data-testid="stSidebar"] * { color: #1c1c2e !important; }

.main .block-container { padding-top: 1.8rem !important; }

.brand-name {
    font-size: 20px;
    font-weight: 600;
    color: #1c1c2e;
    letter-spacing: -0.3px;
}
.brand-tag {
    font-size: 10px;
    font-family: 'DM Mono', monospace;
    color: #9ea3b5;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-top: 1px;
}

.sb-section {
    background: #f8f9fd;
    border: 1px solid #e4e6ef;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 12px;
}
.sb-label {
    font-size: 9px;
    font-weight: 600;
    color: #9ea3b5;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-family: 'DM Mono', monospace;
    margin-bottom: 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid #e4e6ef;
}
.sb-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid #eef0f7;
    font-size: 12px;
}
.sb-row:last-child { border-bottom: none; }
.sb-key { color: #6b7185; font-size: 12px; }
.sb-val {
    font-family: 'DM Mono', monospace;
    font-weight: 500;
    color: #4f52c9;
    font-size: 12px;
}
.status-online {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 12px;
    color: #15803d;
    font-family: 'DM Mono', monospace;
}
.dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #16a34a;
    display: inline-block;
}

.agent-row {
    display: flex;
    align-items: baseline;
    gap: 10px;
    padding: 6px 0;
    border-bottom: 1px solid #eef0f7;
    font-size: 12px;
}
.agent-row:last-child { border-bottom: none; }
.agent-name {
    font-family: 'DM Mono', monospace;
    font-weight: 500;
    color: #4f52c9;
    font-size: 11px;
    min-width: 90px;
}
.agent-desc { color: #6b7185; font-size: 11px; }

.chat-title {
    font-size: 22px;
    font-weight: 600;
    color: #1c1c2e;
    letter-spacing: -0.3px;
}
.chat-sub {
    font-size: 12px;
    font-family: 'DM Mono', monospace;
    color: #9ea3b5;
    letter-spacing: 0.3px;
    margin-top: 2px;
    margin-bottom: 16px;
}

.user-label {
    text-align: right;
    font-size: 10px;
    font-family: 'DM Mono', monospace;
    color: #9ea3b5;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin: 8px 4px -2px 0;
}
.user-bubble {
    background: #4f52c9;
    color: #ffffff !important;
    padding: 12px 18px;
    border-radius: 16px 16px 3px 16px;
    margin: 0 0 4px 80px;
    font-size: 14px;
    line-height: 1.6;
    box-shadow: 0 2px 10px rgba(79,82,201,0.18);
}
.nexus-label {
    font-size: 10px;
    font-family: 'DM Mono', monospace;
    color: #4f52c9;
    letter-spacing: 1px;
    text-transform: uppercase;
    font-weight: 500;
    margin: 8px 0 -2px 4px;
}
.nexus-bubble {
    background: #ffffff;
    border: 1px solid #e4e6ef;
    padding: 14px 18px;
    border-radius: 3px 16px 16px 16px;
    margin: 0 80px 4px 0;
    font-size: 13px;
    font-family: 'DM Mono', monospace;
    line-height: 1.85;
    white-space: pre-wrap;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
    color: #2d2f45;
}
.pipeline-block {
    background: #f0f1f9;
    border: 1px solid #dde0f0;
    border-left: 3px solid #c5c7e8;
    border-radius: 0 6px 6px 0;
    padding: 8px 14px;
    margin: 3px 80px 3px 0;
    font-size: 11px;
    font-family: 'DM Mono', monospace;
    color: #7b7fa8;
    line-height: 1.9;
}
.report-block {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-left: 3px solid #4ade80;
    border-radius: 0 6px 6px 0;
    padding: 7px 14px;
    margin: 3px 80px 3px 0;
    font-size: 11px;
    font-family: 'DM Mono', monospace;
    color: #15803d;
}

.stTextInput input {
    background: #ffffff !important;
    border: 1.5px solid #e4e6ef !important;
    border-radius: 8px !important;
    color: #1c1c2e !important;
    font-size: 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 10px 14px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
.stTextInput input:focus {
    border-color: #4f52c9 !important;
    box-shadow: 0 0 0 3px rgba(79,82,201,0.1) !important;
}
.stTextInput input::placeholder { color: #b5b9cc !important; }

.stButton button {
    background: #4f52c9 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 20px !important;
    box-shadow: 0 2px 8px rgba(79,82,201,0.2) !important;
    letter-spacing: 0.2px !important;
}
.stButton button:hover { background: #3d40b5 !important; }

hr { border: none; border-top: 1px solid #e4e6ef !important; margin: 12px 0 !important; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
#  Session state
# ─────────────────────────────────────────────────────────────────
if "messages"    not in st.session_state: st.session_state.messages    = []
if "session_log" not in st.session_state: st.session_state.session_log = []

# ─────────────────────────────────────────────────────────────────
#  Load NEXUS (cached)
# ─────────────────────────────────────────────────────────────────
@st.cache_resource
def load_nexus():
    try:
        from day5_nexus_ai import config
        from day5_nexus_ai.config import get_model_client
        from day5_nexus_ai.agents import build_all_agents
        import day4.memory.long_term_memory as ltm
        import day4.memory.vector_store     as vs
        import day4.memory.session_memory   as session

        os.makedirs(config.MEMORY_DIR, exist_ok=True)
        os.makedirs(config.LOGS_DIR,   exist_ok=True)
        ltm.init_db()
        vs.load()
        model_client = get_model_client()
        agents       = build_all_agents(model_client)

        return {
            "ok": True, "agents": agents, "ltm": ltm,
            "vs": vs, "session": session, "config": config,
            "provider": config.ACTIVE_PROVIDER.upper(),
            "model":    config.GEMINI_MODEL if config.ACTIVE_PROVIDER == "gemini" else config.OLLAMA_MODEL,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ─────────────────────────────────────────────────────────────────
#  Run pipeline — with full logging integrated
# ─────────────────────────────────────────────────────────────────
def run_query(user_input: str, nexus: dict) -> dict:
    async def _run():
        from autogen_agentchat.messages import TextMessage
        from day5_nexus_ai.main   import parse_plan, build_memory_context, save_report
        from day5_nexus_ai.logger import (
            log_task, log_plan, log_agent_start, log_agent_result,
            log_reflection, log_error, log_complete,
        )
        from day5_nexus_ai import config

        agents  = nexus["agents"]
        session = nexus["session"]

        # ── Memory ────────────────────────────────────────────────
        session.add_message("user", user_input)
        memory_context = build_memory_context(user_input)

        # ── Log task ──────────────────────────────────────────────
        log_task(user_input)

        # ── Orchestrator ──────────────────────────────────────────
        orch_prompt = (
            f"{memory_context}"
            f"User task: {user_input}\n\n"
            f"Output a JSON execution plan using the available agents."
        )
        orch_resp = await agents["ORCHESTRATOR"].on_messages(
            [TextMessage(content=orch_prompt, source="user")],
            cancellation_token=None,
        )
        plan = parse_plan(orch_resp.chat_message.content)[:config.MAX_PLAN_STEPS]

        # ── Log plan ──────────────────────────────────────────────
        log_plan(plan)

        all_outputs      = []
        step_log         = []
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
                enriched = (
                    f"{task}\n\n--- Memory Context (use this to answer) ---\n{memory_context}"
                    if memory_context else task
                )

            # ── Log agent start ───────────────────────────────────
            log_agent_start(step["step"], agent_key, task)

            try:
                resp   = await agents[agent_key].on_messages(
                    [TextMessage(content=enriched, source="user")],
                    cancellation_token=None,
                )
                result = resp.chat_message.content
                all_outputs.append(f"[Step {step['step']} — {agent_key}]\n{result}")
                step_log.append(f"Step {step['step']}  →  {agent_key}")

                # ── Log agent result ──────────────────────────────
                log_agent_result(step["step"], agent_key, result, success=True)

                # ── Reflection cycle ──────────────────────────────
                if agent_key == "CRITIC" and reflection_count < config.MAX_REFLECTION_CYCLES:
                    pre    = all_outputs[-2] if len(all_outputs) >= 2 else ""
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
                    step_log.append(f"  Reflection {reflection_count+1}  →  OPTIMIZER")

                    # ── Log reflection ────────────────────────────
                    log_reflection(reflection_count + 1, result, o_out)
                    reflection_count += 1

            except Exception as e:
                step_log.append(f"Step {step['step']}  →  {agent_key}  [ERROR: {e}]")
                # ── Log error ─────────────────────────────────────
                log_error(step["step"], agent_key, str(e))

        # ── Extract final output ──────────────────────────────────
        final = ""
        for output in reversed(all_outputs):
            if "REPORTER" in output:
                final = output.split("\n", 1)[1] if "\n" in output else output
                break
        if not final:
            final = all_outputs[-1] if all_outputs else "No output generated."
        if final.startswith("[Step") and "\n" in final:
            final = final.split("\n", 1)[1]

        reporter_ran = any("REPORTER" in s for s in step_log)
        report_path  = save_report(user_input, final) if reporter_ran else None

        # ── Log complete ──────────────────────────────────────────
        if reporter_ran:
            log_complete(user_input, report_path)
        else:
            log_complete(user_input, "direct answer — no report saved")

        session.add_message("assistant", final[:500])
        st.session_state.session_log.append({"task": user_input, "report": final})

        return {"plan": plan, "step_log": step_log, "final": final, "report_path": report_path}

    return asyncio.run(_run())


# ─────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────
nexus = load_nexus()

with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 20px 0">
        <div class="brand-name">NEXUS AI</div>
        <div class="brand-tag">Autonomous Multi-Agent System</div>
    </div>
    """, unsafe_allow_html=True)

    if nexus["ok"]:
        mem   = nexus["ltm"].memory_stats()
        faiss = nexus["vs"].count()

        st.markdown(f"""
        <div class="sb-section">
            <div class="sb-label">System</div>
            <div class="sb-row">
                <span class="sb-key">Status</span>
                <span class="status-online"><span class="dot"></span>Online</span>
            </div>
            <div class="sb-row">
                <span class="sb-key">Provider</span>
                <span class="sb-val">{nexus['provider']}</span>
            </div>
            <div class="sb-row">
                <span class="sb-key">Model</span>
                <span class="sb-val" style="font-size:10px">{nexus['model']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="sb-section">
            <div class="sb-label">Memory</div>
            <div class="sb-row">
                <span class="sb-key">Vector Store (FAISS)</span>
                <span class="sb-val">{faiss}</span>
            </div>
            <div class="sb-row">
                <span class="sb-key">Stored Facts</span>
                <span class="sb-val">{mem['facts']}</span>
            </div>
            <div class="sb-row">
                <span class="sb-key">Episodes</span>
                <span class="sb-val">{mem['episodes']}</span>
            </div>
            <div class="sb-row">
                <span class="sb-key">Session Tasks</span>
                <span class="sb-val">{len(st.session_state.session_log)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.error(f"Failed to load NEXUS AI: {nexus['error']}")
        st.stop()

    AGENTS = [
        ("ORCHESTRATOR", "Routes tasks to the right agents"),
        ("PLANNER",      "Breaks tasks into ordered steps"),
        ("RESEARCHER",   "Web search and background knowledge"),
        ("CODER",        "Writes and executes Python code"),
        ("ANALYST",      "Finds patterns and draws insights"),
        ("CRITIC",       "Reviews output and finds weaknesses"),
        ("OPTIMIZER",    "Improves output based on Critic"),
        ("VALIDATOR",    "Verifies correctness and completeness"),
        ("REPORTER",     "Formats polished final report"),
        ("FILE",         "Reads and writes files"),
        ("DB",           "SQLite database operations"),
    ]

    agents_html = '<div class="sb-section"><div class="sb-label">Agents</div>'
    for name, desc in AGENTS:
        agents_html += f"""
        <div class="agent-row">
            <span class="agent-name">{name}</span>
            <span class="agent-desc">{desc}</span>
        </div>"""
    agents_html += "</div>"
    st.markdown(agents_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Save to Long-Term Memory"):
        if st.session_state.session_log and nexus["ok"]:
            for exchange in st.session_state.session_log:
                nexus["ltm"].store_episode(exchange["task"], exchange["report"][:500])
                nexus["vs"].add_memory(
                    text=f"Task: {exchange['task']} | Summary: {exchange['report'][:300]}",
                    metadata={"type": "nexus_task"},
                )
            nexus["vs"].save()
            st.success(f"Saved {len(st.session_state.session_log)} exchanges.")
        else:
            st.info("Nothing new to save.")

    if st.button("Clear Chat"):
        st.session_state.messages    = []
        st.session_state.session_log = []
        if nexus["ok"]:
            nexus["session"].clear()
        st.rerun()


# ─────────────────────────────────────────────────────────────────
#  MAIN — Chat
# ─────────────────────────────────────────────────────────────────

st.markdown("""
<div class="chat-title">Chat</div>
<div class="chat-sub">memory recall &nbsp;·&nbsp; web search &nbsp;·&nbsp; code execution &nbsp;·&nbsp; file operations &nbsp;·&nbsp; database</div>
""", unsafe_allow_html=True)

st.divider()

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown('<div class="user-label">You</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="nexus-label">NEXUS AI</div>', unsafe_allow_html=True)

        if msg.get("step_log"):
            steps_txt = "\n".join(msg["step_log"])
            st.markdown(f'<div class="pipeline-block">{steps_txt}</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="nexus-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

        if msg.get("report_path"):
            st.markdown(
                f'<div class="report-block">Report saved  →  {msg["report_path"]}</div>',
                unsafe_allow_html=True
            )

st.divider()

col1, col2 = st.columns([8, 1])
with col1:
    user_input = st.text_input(
        "msg", placeholder="Type your message...",
        label_visibility="collapsed", key="chat_input",
    )
with col2:
    send = st.button("Send")

if not nexus["ok"]:
    st.error("NEXUS AI failed to load.")
    st.stop()

if send and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("NEXUS AI is thinking..."):
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
                "role": "assistant", "content": f"[ERROR] {e}", "step_log": [],
            })
    st.rerun()