# NEXUS AI — System Architecture

## Overview

NEXUS AI is an autonomous multi-agent AI system built on AutoGen. It combines multi-step planning, tool execution, self-reflection, persistent memory, real-time web search, and structured logging into a single cohesive pipeline.

```
Folder Structure
week9/
├── nexus_ai/
│   ├── main.py          ← entry point, pipeline runner, memory orchestration
│   ├── agents.py        ← all 11 specialist agents with system prompts
│   ├── config.py        ← model provider, paths, pipeline constants
│   └── logger.py        ← logging to .log + trace.jsonl
├── tools/
│   ├── code_executor.py ← Python subprocess execution tool
│   ├── file_agent.py    ← read/write/csv file tools
│   └── db_agent.py      ← SQLite inspect + query tools
├── memory/
│   ├── session_memory.py    ← RAM-only current session store
│   ├── long_term_memory.py  ← SQLite facts + episodes store
│   ├── vector_store.py      ← FAISS semantic search store
│   ├── long_term.db         ← auto-created SQLite database
│   ├── faiss.index          ← saved on exit
│   └── metadata.json        ← FAISS parallel metadata
├── logs/
│   ├── nexus_*.log          ← one per session, human-readable
│   ├── trace.jsonl          ← all sessions, machine-readable JSON events
│   └── report_*.md          ← saved when user requests a report
├── streamlit_app.py     ← browser UI for NEXUS AI
└── .env                 ← GEMINI_API_KEY
```

## Pipeline Architecture
```
User Query
    ↓
build_memory_context()
    ├── FAISS vector search (k=3 semantic matches)
    ├── SQLite episodes (last 2 conversations)
    ├── SQLite facts (stored user preferences)
    └── Session RAM (last 4 messages)
    ↓
Orchestrator receives: memory_context + user query
    → outputs JSON execution plan
    ↓
Specialist Agents run in sequence
    → each receives: task + all previous agent outputs
    → first agent also receives memory context directly
    ↓
Critic → Optimizer reflection cycle (auto-triggered, max 2 cycles)
    ↓
Reporter formats final output (only if user asked for a report)
    ↓
On exit: session saved to SQLite + FAISS
```

## Memory Architecture
```
┌─────────────────────────────────────────────────────────┐
│  Three independent memory layers                        │
│                                                         │
│  Session RAM        → Python list in memory             │
│                       cleared on 'clear' or session end │
│                       holds current conversation window │
│                                                         │
│  SQLite (long_term.db)                                  │
│    facts table    → user preferences, name, company     │
│    episodes table → full conversation turns             │
│    written only on exit                                 │
│                                                         │
│  FAISS (faiss.index + metadata.json)                    │
│    384-dim vectors via all-MiniLM-L6-v2                 │
│    semantic similarity search                           │
│    saved only on exit                                   │
└─────────────────────────────────────────────────────────┘

```
## Memory Injection Flow
Every query:
- build_memory_context(user_input)
- FAISS.search(k=3): finds semantically similar past tasks
- ltm.format_episodes(n=2): fetches last 2 SQLite conversations
- ltm.format_facts(): fetches all stored facts
- session.format(n=4): fetches last 4 session messages
- combined into one string
- injected into Orchestrator prompt
- also injected into first agent's enriched_task

**Save Strategy — (Save Only on Exit)**

During session: all data stays in RAM only.
* On exit: session_log saved to SQLite episodes + FAISS vectors.
* On clear: session RAM wiped, agents recreated, long-term untouched.

## Reflection Cycle
```
Orchestrator plan includes CRITIC at step N
    ↓
Agent before Critic produces output
    ↓
CRITIC reviews → scores 1-10, lists weaknesses
    ↓
[auto-triggered in run_pipeline() code]
OPTIMIZER receives: original output + critic feedback
OPTIMIZER produces: improved version
reflection_count += 1   (max: MAX_REFLECTION_CYCLES = 2)
    ↓
Pipeline continues to next planned step
The Optimizer has two triggers:

Auto-trigger — always fires after every Critic step (hardcoded in run_pipeline)
Plan trigger — Orchestrator may also include Optimizer as an explicit step
```

## Routing Logic

- Simple question        → RESEARCHER
- Real-time query        → RESEARCHER (calls web_search tool)
- Code task              → PLANNER → CODER → VALIDATOR
- Data analysis          → FILE → ANALYST → CRITIC → OPTIMIZER
- Architecture/strategy  → PLANNER → RESEARCHER → ANALYST
- CSV analysis           → FILE → CODER → ANALYST → CRITIC
- Report requested       → any chain above → REPORTER
- Reporter Rule: REPORTER only runs when user explicitly says
- "create a report", "generate a report", "make a .md", "document this".

All other queries show direct answers with no file saved.

## Logging Architecture

1) logs/nexus_YYYYMMDD_HHMMSS.log   ← one per session
    human-readable timestamped log of every agent action
    used for: debugging, reviewing past sessions

2) logs/trace.jsonl                  ← one file, all sessions appended
    one JSON object per line per event
    events: task, plan, agent_start, agent_result,
            reflection, memory_*, error, complete
    used for: analysis, dashboards, counting agent usage

3) logs/report_*.md                  ← one per task with Reporter
    the polished final output from Reporter
    saved only when REPORTER ran in the pipeline

## Web Search Integration

Researcher agent has access to web_search(query) tool using DuckDuckGo. No API key required. Returns top 3 results with title, snippet, source.
- Used for: weather, news, prices, company info, current events.
- Rate limited with time.sleep(1) between calls.

## Streamlit UI

* Single-page chat interface at streamlit_app.py.
* Sidebar: system status, provider, model, memory stats, agent roster.
* Main: persistent chat history with pipeline steps shown above each response.
* Save to Long-Term Memory button replaces terminal exit command.
* Full logger integration — Streamlit sessions produce identical .log and trace.jsonl files as terminal.