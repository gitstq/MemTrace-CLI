"""
MemTrace-CLI: Memory search and retrieval engine.

Provides advanced search capabilities over captured agent sessions,
including full-text search, tag-based filtering, time-ranged queries,
and result formatting for different output targets.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from .store import MemoryStore


class MemorySearch:
    """
    High-level search and retrieval interface for the memory store.
    
    Wraps raw SQL queries with convenient filtering, sorting,
    and formatting utilities.
    """

    def __init__(self, store: Optional[MemoryStore] = None):
        self.store = store or MemoryStore()

    # ── Core Search ────────────────────────────────────────────────

    def search(
        self,
        query: str,
        agent: Optional[str] = None,
        workspace: Optional[str] = None,
        tag: Optional[str] = None,
        days: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        """
        Comprehensive search with multiple filters.
        
        Returns:
            dict with 'results' (list of messages) and 'total' count
        """
        where_clauses = ["1=1"]
        params: list = []

        # Full-text search conditions
        if query:
            safe_query = " ".join(
                f'"{w}"' if not w.startswith('"') else w
                for w in query.split()
            )
            where_clauses.append("""
                (m.content LIKE ? OR m.id IN (
                    SELECT rowid FROM messages_fts WHERE messages_fts MATCH ?
                ))
            """)
            params.extend([f"%{query}%", safe_query])

        # Agent filter
        if agent:
            where_clauses.append("s.agent = ?")
            params.append(agent)

        # Workspace filter
        if workspace:
            where_clauses.append("s.workspace = ?")
            params.append(workspace)

        # Time range
        if days is not None and days > 0:
            cutoff = (
                datetime.now(timezone.utc) - timedelta(days=days)
            ).isoformat()
            where_clauses.append("m.created_at >= ?")
            params.append(cutoff)

        # Tag filter
        if tag:
            where_clauses.append("""
                s.id IN (SELECT session_id FROM tags WHERE tag = ?)
            """)
            params.append(tag.lower().strip())

        where = " AND ".join(where_clauses)

        # Count
        count_sql = f"""
            SELECT COUNT(*) FROM messages m
            JOIN sessions s ON m.session_id = s.id
            WHERE {where}
        """
        total = self.store._conn.execute(count_sql, params).fetchone()[0]

        # Fetch
        fetch_sql = f"""
            SELECT m.*, s.agent, s.workspace, s.started_at as session_started
            FROM messages m
            JOIN sessions s ON m.session_id = s.id
            WHERE {where}
            ORDER BY m.id DESC
            LIMIT ? OFFSET ?
        """
        rows = self.store._conn.execute(
            fetch_sql, params + [limit, offset]
        ).fetchall()

        results = []
        for r in rows:
            msg = dict(r)
            # Fetch tags for the session
            msg["tags"] = self.store.get_tags(msg["session_id"])
            results.append(msg)

        return {"results": results, "total": total, "query": query}

    # ── Convenience Queries ────────────────────────────────────────

    def recent_sessions(self, days: int = 7, limit: int = 20) -> list[dict]:
        """Get recent sessions."""
        return self.store.list_sessions(limit=limit)

    def sessions_by_tag(self, tag: str, limit: int = 20) -> list[dict]:
        """Find sessions with a specific tag."""
        rows = self.store._conn.execute(
            """SELECT s.* FROM sessions s
               JOIN tags t ON s.id = t.session_id
               WHERE t.tag = ?
               ORDER BY s.started_at DESC
               LIMIT ?""",
            (tag.lower().strip(), limit),
        )
        return [dict(r) for r in rows.fetchall()]

    def find_similar(
        self, session_id: str, limit: int = 5
    ) -> list[dict]:
        """
        Find sessions similar to a given one, based on shared tags and agent.
        """
        session = self.store.get_session(session_id)
        if not session:
            return []

        tags = self.store.get_tags(session_id)
        agent = session.get("agent", "")

        rows = self.store._conn.execute(
            """SELECT s.*, 
                      (CASE WHEN s.agent = ? THEN 2 ELSE 0 END +
                       (SELECT COUNT(*) FROM tags t2 
                        WHERE t2.session_id = s.id 
                        AND t2.tag IN ({placeholders}))) as score
               FROM sessions s
               WHERE s.id != ?
               HAVING score > 0
               ORDER BY score DESC, s.started_at DESC
               LIMIT ?""".format(
                placeholders=",".join("?" for _ in tags)
            ),
            [agent] + tags + [session_id, limit],
        )
        return [dict(r) for r in rows.fetchall()]

    # ── Export ─────────────────────────────────────────────────────

    def export_session(
        self, session_id: str, format: str = "markdown"
    ) -> str:
        """
        Export a session in the specified format.
        
        Supported formats: 'markdown', 'json', 'text'
        """
        session = self.store.get_session(session_id)
        if not session:
            return f"Session {session_id} not found."

        messages = self.store.get_messages(session_id)
        tags = self.store.get_tags(session_id)
        agent = session.get("agent", "unknown")

        if format == "json":
            return json.dumps({
                "session": session,
                "tags": tags,
                "messages": messages,
            }, indent=2, ensure_ascii=False)

        if format == "markdown":
            lines = [
                f"# Session: {session_id}",
                f"",
                f"**Agent:** {agent}  ",
                f"**Workspace:** {session.get('workspace', 'default')}  ",
                f"**Started:** {session.get('started_at', 'N/A')}  ",
                f"**Ended:** {session.get('ended_at', 'N/A')}  ",
                f"**Summary:** {session.get('summary', 'N/A')}  ",
                f"**Tokens:** {session.get('token_count', 0)}  ",
                f"",
            ]
            if tags:
                lines.append(f"**Tags:** `{'`, `'.join(tags)}`")
                lines.append("")
            lines.append("---")
            lines.append("")
            for msg in messages:
                role = msg["role"].upper()
                content = msg["content"]
                lines.append(f"### {role}")
                if msg.get("tool_name"):
                    lines.append(f"*Tool: {msg['tool_name']}*")
                lines.append("")
                lines.append(f"```\n{content}\n```")
                lines.append("")
            return "\n".join(lines)

        # Plain text
        lines = [
            f"Session: {session_id}",
            f"Agent: {agent}",
            f"Workspace: {session.get('workspace', 'default')}",
            f"Started: {session.get('started_at', 'N/A')}",
            f"Summary: {session.get('summary', 'N/A')}",
            f"Tags: {', '.join(tags) if tags else 'N/A'}",
            "",
            "--- Messages ---",
            "",
        ]
        for msg in messages:
            role = msg["role"].upper()
            content = msg["content"]
            lines.append(f"[{role}]")
            if msg.get("tool_name"):
                lines.append(f"  Tool: {msg['tool_name']}")
            # Truncate very long content in text mode
            if len(content) > 500:
                content = content[:500] + "... [truncated]"
            lines.append(f"  {content}")
            lines.append("")
        return "\n".join(lines)

    # ── Stats / Summary ────────────────────────────────────────────

    def summarize(self, days: int = 7) -> dict:
        """Generate a summary of recent memory activity."""
        cutoff = (
            datetime.now(timezone.utc) - timedelta(days=days)
        ).isoformat()

        recent_sessions = self.store._conn.execute(
            """SELECT COUNT(*) FROM sessions WHERE started_at >= ?""",
            (cutoff,),
        ).fetchone()[0]

        recent_messages = self.store._conn.execute(
            """SELECT COUNT(*) FROM messages m
               JOIN sessions s ON m.session_id = s.id
               WHERE s.started_at >= ?""",
            (cutoff,),
        ).fetchone()[0]

        top_agents = [
            dict(r)
            for r in self.store._conn.execute(
                """SELECT agent, COUNT(*) as cnt 
                   FROM sessions WHERE started_at >= ?
                   GROUP BY agent ORDER BY cnt DESC LIMIT 5""",
                (cutoff,),
            ).fetchall()
        ]

        return {
            "period_days": days,
            "sessions": recent_sessions,
            "messages": recent_messages,
            "top_agents": top_agents,
        }


import json  # noqa: E811 (used in export_session)