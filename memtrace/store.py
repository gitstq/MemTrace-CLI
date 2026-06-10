"""
MemTrace-CLI: SQLite-based persistent memory store.

Zero external dependencies — uses only Python stdlib (sqlite3, json, time, pathlib).
Supports FTS5 full-text search for fast retrieval across captured sessions.
"""

import json
import os
import sqlite3
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator, Optional


class MemoryStore:
    """
    Persistent, thread-safe memory store backed by SQLite.
    
    Stores sessions, messages (prompts/responses/tool-calls), tags, and
    provides full-text search via SQLite FTS5.
    """

    DEFAULT_DB_DIR = os.path.join(Path.home(), ".memtrace")

    def __init__(self, db_dir: Optional[str] = None):
        self.db_dir = Path(db_dir or self.DEFAULT_DB_DIR)
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.db_dir / "memory.db"
        self._local = threading.local()
        self._init_db()

    # ── Connection Management ──────────────────────────────────────

    @property
    def _conn(self) -> sqlite3.Connection:
        """Thread-local connection."""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
            )
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA synchronous=NORMAL")
        return self._local.conn

    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = self._conn
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id          TEXT PRIMARY KEY,
                agent       TEXT NOT NULL DEFAULT 'unknown',
                workspace   TEXT NOT NULL DEFAULT 'default',
                started_at  TEXT NOT NULL,
                ended_at    TEXT,
                summary     TEXT,
                token_count INTEGER DEFAULT 0,
                metadata    TEXT DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS messages (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  TEXT NOT NULL REFERENCES sessions(id),
                role        TEXT NOT NULL CHECK(role IN ('user','assistant','tool','system')),
                content     TEXT NOT NULL,
                tool_name   TEXT,
                token_count INTEGER DEFAULT 0,
                created_at  TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );

            CREATE TABLE IF NOT EXISTS tags (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  TEXT NOT NULL REFERENCES sessions(id),
                tag         TEXT NOT NULL,
                UNIQUE(session_id, tag)
            );

            CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts 
            USING fts5(content, tokenize='unicode61');

            CREATE INDEX IF NOT EXISTS idx_messages_session 
            ON messages(session_id);
            CREATE INDEX IF NOT EXISTS idx_sessions_agent 
            ON sessions(agent);
            CREATE INDEX IF NOT EXISTS idx_sessions_started 
            ON sessions(started_at);
        """)
        conn.commit()

    # ── Session CRUD ───────────────────────────────────────────────

    def create_session(
        self,
        agent: str = "unknown",
        workspace: str = "default",
        metadata: Optional[dict] = None,
    ) -> str:
        """Create a new session and return its ID."""
        session_id = uuid.uuid4().hex[:12]
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            """INSERT INTO sessions (id, agent, workspace, started_at, metadata)
               VALUES (?, ?, ?, ?, ?)""",
            (session_id, agent, workspace, now, json.dumps(metadata or {})),
        )
        self._conn.commit()
        return session_id

    def end_session(
        self,
        session_id: str,
        summary: Optional[str] = None,
        token_count: int = 0,
    ) -> None:
        """Mark a session as ended."""
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            """UPDATE sessions 
               SET ended_at = ?, summary = ?, token_count = ?
               WHERE id = ?""",
            (now, summary, token_count, session_id),
        )
        self._conn.commit()

    def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve a single session by ID."""
        row = self._conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if row is None:
            return None
        return dict(row)

    def list_sessions(
        self,
        agent: Optional[str] = None,
        workspace: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """List sessions with optional filtering."""
        query = "SELECT * FROM sessions WHERE 1=1"
        params: list[Any] = []
        if agent:
            query += " AND agent = ?"
            params.append(agent)
        if workspace:
            query += " AND workspace = ?"
            params.append(workspace)
        query += " ORDER BY started_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        return [dict(r) for r in self._conn.execute(query, params).fetchall()]

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages/tags."""
        self._conn.execute("DELETE FROM tags WHERE session_id = ?", (session_id,))
        self._conn.execute(
            "DELETE FROM messages_fts WHERE rowid IN "
            "(SELECT id FROM messages WHERE session_id = ?)",
            (session_id,),
        )
        self._conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        cur = self._conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        self._conn.commit()
        return cur.rowcount > 0

    # ── Messages ───────────────────────────────────────────────────

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_name: Optional[str] = None,
        token_count: int = 0,
    ) -> int:
        """Add a message to a session. Returns message ID."""
        now = datetime.now(timezone.utc).isoformat()
        cur = self._conn.execute(
            """INSERT INTO messages (session_id, role, content, tool_name, token_count, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (session_id, role, content, tool_name, token_count, now),
        )
        msg_id = cur.lastrowid
        # Sync FTS index
        self._conn.execute(
            "INSERT INTO messages_fts (rowid, content) VALUES (?, ?)",
            (msg_id, content),
        )
        self._conn.commit()
        return msg_id

    def get_messages(
        self, session_id: str, limit: int = 500
    ) -> list[dict]:
        """Get all messages for a session."""
        rows = self._conn.execute(
            """SELECT * FROM messages 
               WHERE session_id = ? 
               ORDER BY id ASC LIMIT ?""",
            (session_id, limit),
        )
        return [dict(r) for r in rows.fetchall()]

    # ── Tags ───────────────────────────────────────────────────────

    def add_tag(self, session_id: str, tag: str) -> None:
        """Add a tag to a session."""
        try:
            self._conn.execute(
                "INSERT OR IGNORE INTO tags (session_id, tag) VALUES (?, ?)",
                (session_id, tag.lower().strip()),
            )
            self._conn.commit()
        except sqlite3.IntegrityError:
            pass

    def add_tags(self, session_id: str, tags: list[str]) -> None:
        """Add multiple tags."""
        for tag in tags:
            self.add_tag(session_id, tag)

    def get_tags(self, session_id: str) -> list[str]:
        """Get all tags for a session."""
        rows = self._conn.execute(
            "SELECT tag FROM tags WHERE session_id = ? ORDER BY tag",
            (session_id,),
        )
        return [r["tag"] for r in rows.fetchall()]

    def list_all_tags(self) -> list[tuple[str, int]]:
        """List all tags with their usage counts."""
        rows = self._conn.execute(
            """SELECT tag, COUNT(*) as cnt 
               FROM tags GROUP BY tag ORDER BY cnt DESC"""
        )
        return [(r["tag"], r["cnt"]) for r in rows.fetchall()]

    # ── Search ─────────────────────────────────────────────────────

    def search(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        """
        Full-text search across all messages using FTS5.
        Returns a list of matching messages with their session context.
        """
        # Sanitize FTS5 query syntax
        safe_query = " ".join(
            f'"{w}"' if not w.startswith('"') else w
            for w in query.split()
        )
        try:
            rows = self._conn.execute(
                """SELECT m.*, s.agent, s.workspace, s.started_at as session_started
                   FROM messages_fts fts
                   JOIN messages m ON fts.rowid = m.id
                   JOIN sessions s ON m.session_id = s.id
                   WHERE messages_fts MATCH ?
                   ORDER BY rank
                   LIMIT ? OFFSET ?""",
                (safe_query, limit, offset),
            )
            return [dict(r) for r in rows.fetchall()]
        except sqlite3.OperationalError:
            # Fallback to LIKE search if FTS5 syntax error
            like_q = f"%{query}%"
            rows = self._conn.execute(
                """SELECT m.*, s.agent, s.workspace, s.started_at as session_started
                   FROM messages m
                   JOIN sessions s ON m.session_id = s.id
                   WHERE m.content LIKE ?
                   ORDER BY m.id DESC
                   LIMIT ? OFFSET ?""",
                (like_q, limit, offset),
            )
            return [dict(r) for r in rows.fetchall()]

    # ── Statistics ─────────────────────────────────────────────────

    def stats(self) -> dict:
        """Return memory store statistics."""
        session_count = self._conn.execute(
            "SELECT COUNT(*) FROM sessions"
        ).fetchone()[0]
        message_count = self._conn.execute(
            "SELECT COUNT(*) FROM messages"
        ).fetchone()[0]
        active_sessions = self._conn.execute(
            "SELECT COUNT(*) FROM sessions WHERE ended_at IS NULL"
        ).fetchone()[0]
        total_tokens = self._conn.execute(
            "SELECT COALESCE(SUM(token_count), 0) FROM sessions"
        ).fetchone()[0]
        agents = [
            dict(r)
            for r in self._conn.execute(
                "SELECT agent, COUNT(*) as cnt FROM sessions GROUP BY agent ORDER BY cnt DESC"
            ).fetchall()
        ]
        db_size = os.path.getsize(self.db_path) if self.db_path.exists() else 0

        return {
            "sessions": session_count,
            "messages": message_count,
            "active_sessions": active_sessions,
            "total_tokens": total_tokens,
            "agents": agents,
            "db_size_bytes": db_size,
            "db_path": str(self.db_path),
        }

    def close(self) -> None:
        """Close the database connection."""
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()