"""
memory/long_term_memory.py
─────────────────────────────────────────────────────────────────
Long-Term Memory using SQLite.

Stores important facts, summaries, and conversation episodes
persistently on disk. Survives across sessions.

Functions:
    store_fact(content, source, category)  → save an important fact
    store_episode(user_msg, agent_reply)   → save a conversation turn
    get_facts(category)                    → retrieve facts by category
    get_recent_episodes(n)                 → retrieve last n episodes
    summarize_and_store(session_history)   → summarize session → store
─────────────────────────────────────────────────────────────────
"""

import sqlite3
import os
from datetime import datetime


# ─────────────────────────────────────────────────────────────────
#  Database setup
# ─────────────────────────────────────────────────────────────────

DB_PATH = os.path.join("memory", "long_term.db")


def _get_connection() -> sqlite3.Connection:
    os.makedirs("memory", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Create the facts and episodes tables if they don't exist.
    Call this once at startup.
    """
    with _get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS facts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                content    TEXT    NOT NULL,
                source     TEXT    DEFAULT 'user',
                category   TEXT    DEFAULT 'general',
                created_at TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS episodes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_msg    TEXT NOT NULL,
                agent_reply TEXT NOT NULL,
                created_at  TEXT NOT NULL
            );
        """)
    print(f"[LongTermMemory] Database ready at '{DB_PATH}'")


# ─────────────────────────────────────────────────────────────────
#  Facts — semantic memory (important things to remember)
# ─────────────────────────────────────────────────────────────────

def store_fact(content: str, source: str = "user", category: str = "general") -> int:
    """
    Store an important fact in long-term memory.

    Args:
        content  : the fact to remember
        source   : where it came from ("user", "agent", "summary")
        category : label for grouping ("preference", "name", "task", etc.)

    Returns:
        The ID of the stored fact.
    """
    with _get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO facts (content, source, category, created_at) VALUES (?, ?, ?, ?)",
            (content, source, category, datetime.now().isoformat())
        )
        return cur.lastrowid


def get_facts(category: str = None) -> list[dict]:
    """
    Retrieve facts, optionally filtered by category.

    Args:
        category : if None, returns all facts

    Returns:
        List of fact dicts.
    """
    with _get_connection() as conn:
        if category:
            rows = conn.execute(
                "SELECT * FROM facts WHERE category = ? ORDER BY created_at DESC",
                (category,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM facts ORDER BY created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]

# ─────────────────────────────────────────────────────────────────
#  Episodes — episodic memory (conversation turns)
# ─────────────────────────────────────────────────────────────────

def store_episode(user_msg: str, agent_reply: str) -> int:
    """
    Store a single conversation turn as an episode.

    Args:
        user_msg    : what the user said
        agent_reply : what the agent replied

    Returns:
        The ID of the stored episode.
    """
    with _get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO episodes (user_msg, agent_reply, created_at) VALUES (?, ?, ?)",
            (user_msg, agent_reply, datetime.now().isoformat())
        )
        return cur.lastrowid


def get_recent_episodes(n: int = 5) -> list[dict]:
    """
    Retrieve the most recent n conversation episodes.

    Args:
        n : number of episodes to return

    Returns:
        List of episode dicts ordered most-recent-first.
    """
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM episodes ORDER BY created_at DESC LIMIT ?",
            (n,)
        ).fetchall()
        return [dict(r) for r in rows]


def format_episodes_for_prompt(n: int = 3) -> str:
    """Format recent episodes as a string for prompt injection."""
    episodes = get_recent_episodes(n)
    if not episodes:
        return "No past conversations found."

    lines = ["--- Past Conversations ---"]
    for ep in reversed(episodes):   # oldest first for readability
        lines.append(f"User: {ep['user_msg']}")
        lines.append(f"Agent: {ep['agent_reply']}")
        lines.append("")
    lines.append("--- End of Past Conversations ---")
    return "\n".join(lines)


def format_facts_for_prompt(category: str = None) -> str:
    """Format stored facts as a string for prompt injection."""
    facts = get_facts(category)
    if not facts:
        return "No facts stored yet."

    lines = ["--- Remembered Facts ---"]
    for f in facts:
        lines.append(f"• [{f['category']}] {f['content']}")
    lines.append("--- End of Facts ---")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────
#  Stats
# ─────────────────────────────────────────────────────────────────

def memory_stats() -> dict:
    """Return basic stats about long-term memory."""
    with _get_connection() as conn:
        facts_count    = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
        episodes_count = conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
        categories     = conn.execute(
            "SELECT DISTINCT category FROM facts"
        ).fetchall()
        return {
            "facts":      facts_count,
            "episodes":   episodes_count,
            "categories": [r[0] for r in categories],
            "db_path":    DB_PATH,
        }