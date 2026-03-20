"""
memory/session_memory.py
─────────────────────────────────────────────────────────────────
Short-Term Session Memory.

Stores the current conversation in RAM as a list of messages.
Cleared when the session ends — does not persist to disk.

Functions:
    add_message(role, content)     → adds a message to session
    get_history()                  → returns full conversation list
    get_recent(n)                  → returns last n messages
    clear()                        → wipes the session
    summarize_session(model_client)→ returns AI summary of session
─────────────────────────────────────────────────────────────────
"""

from datetime import datetime


# ─────────────────────────────────────────────────────────────────
#  In-memory store
# ─────────────────────────────────────────────────────────────────

_session: list[dict] = []


def add_message(role: str, content: str) -> None:
    """
    Add a message to the current session.

    Args:
        role    : "user" | "assistant" | "system"
        content : the message text
    """
    _session.append({
        "role":      role,
        "content":   content,
        "timestamp": datetime.now().isoformat(),
    })


def get_history() -> list[dict]:
    """Return the full session conversation."""
    return list(_session)


def get_recent(n: int = 5) -> list[dict]:
    """Return the last n messages from the session."""
    return list(_session[-n:])


def clear() -> None:
    """Wipe the current session from memory."""
    _session.clear()


def format_for_prompt(n: int = 10) -> str:
    """
    Format the last n messages as a readable string
    suitable for injecting into an agent prompt.
    """
    recent = get_recent(n)
    if not recent:
        return "No conversation history yet."

    lines = ["--- Recent Conversation ---"]
    for msg in recent:
        role = msg["role"].upper()
        lines.append(f"[{role}]: {msg['content']}")
    lines.append("--- End of History ---")
    return "\n".join(lines)


def session_stats() -> dict:
    """Return basic stats about the current session."""
    return {
        "total_messages": len(_session),
        "user_messages":      sum(1 for m in _session if m["role"] == "user"),
        "assistant_messages": sum(1 for m in _session if m["role"] == "assistant"),
        "started_at": _session[0]["timestamp"] if _session else None,
        "last_at":    _session[-1]["timestamp"] if _session else None,
    }