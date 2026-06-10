"""
MemTrace-CLI: Session capture and management.

Provides the SessionCapture class for capturing AI agent interactions,
and utility functions for session lifecycle management.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .store import MemoryStore


class SessionCapture:
    """
    Capture and manage AI agent coding sessions.
    
    Acts as a wrapper/logger around CLI agent sessions, recording
    prompts, responses, and tool calls into the persistent memory store.
    """

    def __init__(
        self,
        store: Optional[MemoryStore] = None,
        agent: str = "unknown",
        workspace: str = "default",
        auto_tag: Optional[list[str]] = None,
    ):
        self.store = store or MemoryStore()
        self.agent = agent
        self.workspace = workspace
        self.auto_tag = auto_tag or []
        self._session_id: Optional[str] = None
        self._last_session_id: Optional[str] = None
        self._running = False
        self._message_buffer: list[dict] = []

    # ── Session Lifecycle ──────────────────────────────────────────

    @property
    def session_id(self) -> Optional[str]:
        """Return the current session ID, or the last one if stopped."""
        return self._session_id or self._last_session_id

    def start(self, metadata: Optional[dict] = None) -> str:
        """Start a new capture session."""
        self._session_id = self.store.create_session(
            agent=self.agent,
            workspace=self.workspace,
            metadata=metadata,
        )
        self._running = True
        self._message_buffer = []

        if self.auto_tag:
            self.store.add_tags(self._session_id, self.auto_tag)

        return self._session_id

    def stop(self, summary: Optional[str] = None) -> Optional[str]:
        """
        Stop the current session.
        Returns the session ID or None if no session was running.
        """
        if not self._session_id or not self._running:
            return None

        total_tokens = sum(
            m.get("token_count", 0) for m in self._message_buffer
        )
        self.store.end_session(
            session_id=self._session_id,
            summary=summary or self._auto_summarize(),
            token_count=total_tokens,
        )
        self._last_session_id = self._session_id
        self._session_id = None
        self._running = False
        return self._last_session_id

    # ── Message Recording ──────────────────────────────────────────

    def log(
        self,
        role: str,
        content: str,
        tool_name: Optional[str] = None,
        token_count: int = 0,
    ) -> int:
        """
        Log a single message into the current session.
        
        Args:
            role: One of 'user', 'assistant', 'tool', 'system'
            content: The message content
            tool_name: Optional tool name (for tool calls)
            token_count: Approximate token count
            
        Returns:
            Message ID
        """
        if not self._session_id or not self._running:
            raise RuntimeError("No active session. Call start() first.")

        msg_id = self.store.add_message(
            session_id=self._session_id,
            role=role,
            content=content,
            tool_name=tool_name,
            token_count=token_count,
        )
        self._message_buffer.append({
            "id": msg_id,
            "role": role,
            "content": content,
            "token_count": token_count,
        })
        return msg_id

    def log_user(self, content: str) -> int:
        """Convenience: log a user prompt."""
        return self.log("user", content)

    def log_assistant(self, content: str) -> int:
        """Convenience: log an assistant response."""
        return self.log("assistant", content)

    def log_tool(self, content: str, tool_name: str) -> int:
        """Convenience: log a tool call/response."""
        return self.log("tool", content, tool_name=tool_name)

    # ── CLI Wrapper ────────────────────────────────────────────────

    def wrap_command(
        self,
        command: list[str],
        session_name: Optional[str] = None,
        cwd: Optional[str] = None,
    ) -> int:
        """
        Run a CLI command while capturing its stdin/stdout as a session.
        
        This is a lightweight wrapper: it starts a session, runs the command,
        captures stdout/stderr as assistant messages, and stops the session.
        
        Args:
            command: The command to run (e.g., ["claude", "-p", "hello"])
            session_name: Optional session name/tag
            cwd: Working directory for the command
            
        Returns:
            Command exit code
        """
        session_id = self.start(metadata={
            "command": " ".join(command),
            "cwd": cwd or os.getcwd(),
            "type": "wrapped",
        })

        if session_name:
            self.store.add_tag(session_id, session_name)

        self.log_system(f"Running: {' '.join(command)}")

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=3600,
            )

            if result.stdout:
                self.log_assistant(result.stdout[:100_000])

            if result.stderr:
                self.log_tool(result.stderr[:50_000], tool_name="stderr")

            self.stop(
                summary=f"Exit code: {result.returncode}"
            )
            return result.returncode

        except subprocess.TimeoutExpired:
            self.log_tool("Command timed out after 3600s", tool_name="timeout")
            self.stop(summary="TIMEOUT")
            return -1
        except FileNotFoundError:
            self.log_tool(f"Command not found: {command[0]}", tool_name="error")
            self.stop(summary="COMMAND_NOT_FOUND")
            return -2
        except Exception as e:
            self.log_tool(f"Error: {e}", tool_name="error")
            self.stop(summary=f"ERROR: {e}")
            return -3

    # ── Helpers ────────────────────────────────────────────────────

    def log_system(self, content: str) -> int:
        """Log a system message."""
        return self.log("system", content)

    def _auto_summarize(self) -> str:
        """Generate an automatic summary from the message buffer."""
        msg_count = len(self._message_buffer)
        if msg_count == 0:
            return "Empty session"
        roles = {}
        for m in self._message_buffer:
            roles[m["role"]] = roles.get(m["role"], 0) + 1
        parts = [f"{k}={v}" for k, v in sorted(roles.items())]
        return f"Session: {msg_count} msgs ({', '.join(parts)})"

    # ── Context Manager ────────────────────────────────────────────

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.log_tool(f"Exception: {exc_val}", tool_name="exception")
            self.stop(summary=f"EXCEPTION: {exc_type.__name__}")
        else:
            self.stop()
        return False

    @classmethod
    def quick_capture(
        cls,
        command: list[str],
        agent: str = "cli",
        workspace: str = "default",
        tags: Optional[list[str]] = None,
    ) -> int:
        """
        One-liner: create a capture, run a command, save everything.
        
        Usage:
            exit_code = SessionCapture.quick_capture(
                ["claude", "-p", "explain this code"]
            )
        """
        capture = cls(agent=agent, workspace=workspace, auto_tag=tags)
        return capture.wrap_command(command)


def estimate_tokens(text: str) -> int:
    """Rough token estimation (~4 chars per token for English, ~1.5 for CJK)."""
    cjk = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    ascii_chars = len(text) - cjk
    return max(1, int(ascii_chars / 4 + cjk / 1.5))