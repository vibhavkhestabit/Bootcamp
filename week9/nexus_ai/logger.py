import os
import json
import logging
from datetime import datetime
from config import LOGS_DIR

os.makedirs(LOGS_DIR, exist_ok=True)

_session_id  = datetime.now().strftime("%Y%m%d_%H%M%S")
_log_file    = os.path.join(LOGS_DIR, f"nexus_{_session_id}.log")
_trace_file  = os.path.join(LOGS_DIR, "trace.jsonl")

# File logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(_log_file, encoding="utf-8"),
    ]
)
_logger = logging.getLogger("nexus")

#  Public API

def log_task(task: str) -> None:
    """Log a new user task."""
    msg = f"[TASK] {task}"
    print(f"\n{'='*60}")
    print(msg)
    print(f"{'='*60}")
    _logger.info(msg)
    _trace(event="task", data={"task": task})


def log_plan(plan: list) -> None:
    """Log the Orchestrator's plan."""
    print(f"\n[NEXUS PLAN] {len(plan)} steps:")
    for step in plan:
        line = f"  Step {step['step']} → [{step['agent']}] {step['task'][:80]}..."
        print(line)
        _logger.info(line)
    _trace(event="plan", data={"steps": plan})


def log_agent_start(step: int, agent: str, task: str) -> None:
    """Log when an agent starts running."""
    msg = f"[Step {step}] {agent} Agent starting..."
    print(f"\n{msg}")
    print(f"  Task: {task[:100]}{'...' if len(task) > 100 else ''}")
    _logger.info(msg)
    _trace(event="agent_start", data={"step": step, "agent": agent, "task": task})


def log_agent_result(step: int, agent: str, result: str, success: bool = True) -> None:
    """Log an agent's result."""
    status = "SUCCESS" if success else "FAILURE"
    msg = f"[Step {step}] {agent} Agent → {status}"
    print(f"\n[{agent} Result]\n{result}\n")
    _logger.info(f"{msg}\n{result}")
    _trace(event="agent_result", data={
        "step": step, "agent": agent,
        "result": result[:500], "success": success
    })


def log_reflection(cycle: int, critic: str, optimizer: str) -> None:
    """Log a Critic → Optimizer reflection cycle."""
    msg = f"[Reflection Cycle {cycle}]"
    print(f"\n{msg}")
    _logger.info(f"{msg}\nCritic: {critic[:200]}\nOptimizer: {optimizer[:200]}")
    _trace(event="reflection", data={
        "cycle": cycle,
        "critic": critic[:300],
        "optimizer": optimizer[:300]
    })


def log_memory(event: str, detail: str) -> None:
    """Log a memory operation."""
    msg = f"[Memory:{event}] {detail}"
    print(msg)
    _logger.info(msg)
    _trace(event=f"memory_{event}", data={"detail": detail})

def log_error(step: int, agent: str, error: str) -> None:
    """Log an agent error."""
    msg = f"[ERROR] Step {step} — {agent}: {error}"
    print(f"\n {msg}")
    _logger.error(msg)
    _trace(event="error", data={"step": step, "agent": agent, "error": error})

def log_complete(task: str, report_path: str) -> None:
    """Log task completion."""
    msg = f"[COMPLETE] Task finished. Report: {report_path}"
    print(f"\n{'='*60}")
    print(f" {msg}")
    print(f"{'='*60}")
    _logger.info(msg)
    _trace(event="complete", data={"task": task, "report": report_path})

def log_session_info() -> dict:
    """Return info about the current log session."""
    return {
        "session_id": _session_id,
        "log_file":   _log_file,
        "trace_file": _trace_file,
    }

#  Internal tracer

def _trace(event: str, data: dict) -> None:
    """Append a structured JSON event to the trace file."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "session":   _session_id,
        "event":     event,
        **data,
    }
    with open(_trace_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")