# Day 5 Capstone: Autonomous Multi-Agent AI System

## Executive Summary

Day 5 was the capstone of Week 9. We built NEXUS AI — a fully autonomous multi-agent system that combines everything from the week: tool-calling agents from Day 3, memory systems from Day 4, and a new orchestration layer that routes tasks, reflects on quality, and adapts based on feedback.
The system went through significant debugging and design iteration. Every edge case we hit became a learning about how LLMs, agents, and memory interact in production systems.

## Agent Roles and Why Each Matters

### 1. Orchestrator

The most critical agent. Runs first on every query. Reads the user's task combined with all memory context and decides which agents to invoke and in what order. Without a good Orchestrator, the entire pipeline misfires.
**Key learning:** Memory context must be injected into the Orchestrator's prompt,not just described to it. The Orchestrator needs to see the actual content of past conversations to make informed routing decisions.

### 2. Planner

Invoked for complex multi-phase tasks. Produces a structured breakdown with failure points and mitigation strategies. Prevents agents from acting on vague instructions by forcing explicit phase definitions before execution begins.
**Key learning:** Planner output is context for subsequent agents, not executableinstructions. The Coder still needs to be told explicitly what to run. 

### 3. Researcher

The knowledge and search agent. Has access to the web_search() tool via DuckDuckGo. Can answer factual questions from training data or fetch live data from the web.
**Key learning:** Without web search, Researcher fabricates current data — wrong dates, wrong temperatures, invented company names. Adding the tool completely eliminated this class of hallucination for real-time queries.

### 4. Coder
The only agent that actually executes Python code. Uses subprocess isolation with a 30-second timeout. Auto-installs missing packages via pip before running.
**Key learning:** Code execution must happen in the Coder step itself. When the Optimizer produces refactored code as text, that code is never re-executed — it exists only in the conversation context. A second Coder step is needed to
actually run improved code.

### 5. Analyst
Receives data or research output and produces structured insights. Separates the concerns of "what happened" (data) from "what it means" (analysis).
**Key learning:** Analyst produces better output when it receives real data fromprevious steps rather than being asked to analyse hypothetically. The all_outputs context chain is essential here.

### 6. Critic
The quality gatekeeper. Reviews the previous agent's output, scores it 1-10, and lists specific weaknesses. Has caught real bugs — domain errors in cricket data, thread safety issues in vector_store.py, hallucinated company names.
**Key learning:** Critic works best after a content-producing agent (Analyst, Researcher, Coder) and worst when the previous output is already empty or an error. A Critic on nothing produces a rubber-stamp PASS.

### 7. Optimizer
Always paired with Critic. Receives the original output and the Critic's feedback and produces a complete improved version.
**Key learning:** Optimizer runs twice per pipeline when Critic is in the plan — once automatically via the hardcoded reflection cycle in run_pipeline(), and once as an explicit Orchestrator-planned step. Both runs genuinely improve
output each time.

### 8. Validator
Checks final output for correctness before Reporter runs. Returns PASS orFAIL with specific reasons.
**Key learning:** Validator must check business logic, not just formatting. Inthe cricket dataset task, Validator rubber-stamped a PASS on data where Wicket-keepers had random bowling styles. The Critic caught what the Validator missed.

### 9. Reporter
Formats all previous agent outputs into a polished .md report. Only runswhen the user explicitly asks for a report.
**Key learning:** Reporter always ran on every task by default, creating unnecessary .md files for simple questions like "what is the weather today". Fixing this required returning the plan from run_pipeline() and checking whether REPORTER was in it before calling save_report().

### 10. File Agent
Reads and writes files on disk. Has five tools: read_file, write_file, write_csv, append_file, list_files.
**Key learning:** list_files() returns only filenames, not contents. When askedto analyse files, the Orchestrator must explicitly instruct File Agent to callread_file() on each file. Without this rule, Researcher would guess at filecontents from names and hallucinate — for example, describing config.py as using "Pydantic-based configuration" when it actually uses os.getenv().

### 11. DB Agent
Creates, queries, and manages SQLite databases. Always calls inspect_schema()first to understand what tables exist.
**Key learning:** DB Agent defaults to the wrong database path unless explicitlytold the db_path in every tool call. An empty database is not an error — it means the agent should create the table, not stop.

## Learnings while contrusting our app

### 1. Memory context not reaching the first agent
* **Problem:** Memory was injected into the Orchestrator prompt but not forwarded to specialist agents. Researcher would say "I don't know your name" even though the name was in the memory context.
* **Root cause:** The first agent's enriched_task was just the plain task string.
All previous agent outputs only accumulate from step 2 onwards.
* **Fix:** Explicitly inject memory_context into the first step's enriched_task:
* **Learning:** Memory injection and context chaining are two separate problems. Injecting into the Orchestrator makes the plan smarter. Injecting into the first agent makes the answer accurate.

### 2. AutoGen agent internal buffer not cleared on session clear
* **Problem:** After typing 'clear', the agent still knew the user's name because AutoGen's AssistantAgent maintains its own internal message history inside theobject. Clearing session RAM did not affect the agent's internal buffer.
* **Fix:** Recreate the agent object on every clear:
* **Learning:** AutoGen agents are stateful objects. Their internal history persists independently of any external memory system unless explicitly reset.

### 3. FAISS index/metadata mismatch causing IndexError
* **Problem:** IndexError: list index out of range in vector_store.py because the FAISS index had 8 vectors but the metadata list was shorter — caused by a crash during a previous session's save process.
* **Fix:** Guard against mismatch in search():
* **Learning:** FAISS indexes and metadata lists must always be saved atomically. If a crash interrupts the save, they go out of sync. The safest fix is to delete both files and start fresh when this happens.

### 4. File Agent using list_files() instead of read_file()
* **Problem:** When asked to "analyse the nexus_ai/ folder", File Agent called list_files() which returns only filenames. Researcher then guessed at file contents, describing config.py as having "Pydantic-based configuration" — wrong.
* **Fix:** Added FILE ANALYSIS RULE to the Orchestrator and CRITICAL DISTINCTION to the File Agent system prompt explicitly requiring read_file() per file.
* **Learning:** list_files() and read_file() are completely different operations. A rule that seems obvious to a human — "analysing files means reading their contents" — must be explicitly stated to the model.

### 5. Reporter always saving files regardless of user intent
* **Problem:** save_report() was called unconditionally after every pipeline run, creating .md files for simple questions like "what is the weather today".
* **Fix:** Return plan from run_pipeline(), check if REPORTER was in it:
* **Learning:** Default behaviour should be minimal. Saving files is a side-effect that should only happen on explicit user intent.

### 6. Researcher fabricating real-time data
* **Problem:** Researcher invented "October 24, 2024" as today's date and made up temperatures for Noida (39°C) with fake source citations.
* **Fix:** Added web_search() tool to Researcher using DuckDuckGo, with a REAL-TIME DATA RULE in the system prompt requiring it to call web_search() for any live data and never fabricate current information.
* **Learning:** LLMs will confidently fabricate plausible real-time data when they have no access to it. Tool access is the only reliable fix — prompt rules alone reduce hallucination but do not eliminate it.

### 7. Orchestrator routing to REPORTER for simple questions
* **Problem:** "What is the weather today?" triggered a full pipeline ending with REPORTER, producing a formal report for a casual question.
* **Fix:** Added REPORTER RULE to Orchestrator system prompt — Reporter only runs on explicit trigger words: "create a report", "generate a report", "make a .md", "document this".
* **Learning:** Orchestrator routing rules must be extremely explicit. Without a
clear rule, the model defaults to the most complete pipeline it knows.

### 8. Hallucinated Personal Information
* **Problem:** When asked "which company do I work for?", NEXUS AI said "Scaleup Ventures" — a completely fabricated answer. The user works at Hestabit.
* **Root cause:** The Hestabit conversation had been done in a session where 'clear' was typed before 'exit', so it was never saved to long-term memory. FAISS and SQLite had no Hestabit data. Researcher fabricated a plausible answer.
* **Learning:** When there is no grounding data, LLMs invent plausible-sounding
facts. 
* **The fix is two-part:** 
1) ensure important facts get saved by always using 'exit' not 'clear' before closing, 
2) the Researcher HONESTY RULE must state explicitly — never invent personal facts, say "I don't have this stored".

### 9. DB Agent using wrong database path
* **Problem:** DB Agent defaulted to database.db instead of the specified long_term.db, finding no tables and stopping with an empty database error.
* **Fix:** Added DB_PATH RULE to DB Agent system prompt — always pass db_path explicitly in every tool call, never rely on the default.
* **Learning:** Default parameters in tool functions are dangerous in agent pipelines. The agent must be explicitly instructed to override defaults.

### 10. Streamlit sessions not producing logs
* **Problem:** Streamlit UI worked correctly but produced no .log or trace.jsonl entries because the run_query() function was written from scratch and never imported logger.py.
* **Fix:** Import and call all logger functions inside run_query(): log_task, log_plan, log_agent_start, log_agent_result, log_reflection, log_error, log_complete.
* **Learning:** When refactoring code for a new interface, side-effect functions (logging, saving) must be explicitly re-wired. They do not automatically transfer just because the core logic was reused.

## Planer Orchestrator

- Predictability: exact agent order every time, easy to debug
- Failure recovery: know exactly which step failed
- Logging: trivial to trace since we control the loop
- Tool use: proven reliable with sequential context passing
- Model compatibility: GroupChat requires strong models for emergent coordination;
- Planner Pipeline works well with Gemini Flash Lite

## Conclusion

NEXUS AI demonstrates that a well-structured multi-agent pipeline with explicit routing rules, grounded memory, and quality reflection loops can handle genuinely complex tasks autonomously. Every failure we encountered taught a concrete principle about how agents, memory, and LLMs behave in production — principles that apply far beyond this specific project.

The most important lesson of Day 5: explicit beats implicit at every layer. Explicit routing rules, explicit memory injection, explicit tool instructions, explicit save triggers. The more precisely we described expected behaviour in system prompts and code, the more reliably the system performed.

## Output

![ss](screenshots/ss1.png)
![ss](screenshots/ss2.png)
![ss](screenshots/ss3.png)
![ss](screenshots/ss4.png)
![ss](screenshots/ss5.png)
![ss](screenshots/ss6.png)
![ss](screenshots/ss7.png)
![ss](screenshots/ss8.png)
![ss](screenshots/ss9.png)
![ss](screenshots/ss10.png)
![ss](screenshots/ss11.png)
![ss](screenshots/ss12.png)
![ss](screenshots/ss13.png)
![ss](screenshots/ss14.png)