from datetime import datetime

#  In-memory store

_session: list[dict] = []

def add_message(role: str, content: str) -> None:
    
    _session.append({
        "role":      role,
        "content":   content,
        "timestamp": datetime.now().isoformat(),
    })

def get_recent(n: int = 5) -> list[dict]:
    return list(_session[-n:])

def clear() -> None:
    _session.clear()

def format_for_prompt(n: int = 10) -> str:
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