"""
Tests for MemTrace-CLI core modules.
"""

import os
import sys
import tempfile
import time
from pathlib import Path

import pytest

# Ensure the package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from memtrace.store import MemoryStore
from memtrace.session import SessionCapture, estimate_tokens
from memtrace.search import MemorySearch


@pytest.fixture
def store():
    """Create a temporary MemoryStore for testing."""
    tmp_dir = tempfile.mkdtemp()
    s = MemoryStore(db_dir=tmp_dir)
    yield s
    s.close()


class TestMemoryStore:
    """Test suite for MemoryStore."""

    def test_create_session(self, store):
        sid = store.create_session(agent="test-agent", workspace="test-ws")
        assert sid is not None
        assert len(sid) == 12

        session = store.get_session(sid)
        assert session is not None
        assert session["agent"] == "test-agent"
        assert session["workspace"] == "test-ws"
        assert session["ended_at"] is None

    def test_end_session(self, store):
        sid = store.create_session()
        store.end_session(sid, summary="done", token_count=100)
        session = store.get_session(sid)
        assert session["ended_at"] is not None
        assert session["summary"] == "done"
        assert session["token_count"] == 100

    def test_add_messages(self, store):
        sid = store.create_session()
        msg_id = store.add_message(sid, "user", "Hello")
        assert msg_id > 0

        messages = store.get_messages(sid)
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"

        # Add another
        store.add_message(sid, "assistant", "Hi!", token_count=10)
        messages = store.get_messages(sid)
        assert len(messages) == 2

    def test_tags(self, store):
        sid = store.create_session()
        store.add_tag(sid, "python")
        store.add_tag(sid, "AI")
        store.add_tag(sid, "python")  # duplicate

        tags = store.get_tags(sid)
        assert len(tags) == 2
        assert "python" in tags
        assert "ai" in tags

        # Add multiple
        sid2 = store.create_session()
        store.add_tags(sid2, ["test", "debug"])
        assert len(store.get_tags(sid2)) == 2

    def test_search(self, store):
        sid = store.create_session()
        store.add_message(sid, "user", "How do I implement a binary search?")
        store.add_message(sid, "assistant", "Here's a Python binary search implementation...")
        store.end_session(sid)

        results = store.search("binary search")
        assert len(results) >= 1
        assert "binary" in results[0]["content"].lower()

    def test_search_fallback(self, store):
        """Test LIKE fallback when FTS5 syntax fails."""
        sid = store.create_session()
        store.add_message(sid, "user", "test content with special chars $%^")
        results = store.search("special chars")
        assert len(results) >= 1

    def test_delete_session(self, store):
        sid = store.create_session()
        store.add_message(sid, "user", "test")
        store.add_tag(sid, "test-tag")

        assert store.delete_session(sid) is True
        assert store.get_session(sid) is None
        assert store.delete_session("nonexistent") is False

    def test_stats(self, store):
        stats = store.stats()
        assert "sessions" in stats
        assert "messages" in stats
        assert "db_size_bytes" in stats
        assert stats["sessions"] == 0

        store.create_session()
        stats = store.stats()
        assert stats["sessions"] == 1

    def test_list_sessions(self, store):
        for i in range(5):
            sid = store.create_session(agent=f"agent-{i}")
            store.end_session(sid)

        sessions = store.list_sessions(limit=3)
        assert len(sessions) == 3

        sessions = store.list_sessions(agent="agent-0")
        assert len(sessions) == 1

    def test_list_all_tags(self, store):
        sid = store.create_session()
        store.add_tags(sid, ["a", "b", "c"])
        sid2 = store.create_session()
        store.add_tags(sid2, ["a", "b"])

        tags = store.list_all_tags()
        assert len(tags) >= 3
        tag_dict = dict(tags)
        assert tag_dict["a"] == 2
        assert tag_dict["c"] == 1


class TestSessionCapture:
    """Test suite for SessionCapture."""

    def test_session_lifecycle(self, store):
        cap = SessionCapture(store=store, agent="test")
        sid = cap.start(metadata={"test": True})
        assert sid is not None

        cap.log_user("Hello")
        cap.log_assistant("Hi!")
        cap.log_tool("tool output", tool_name="search")

        result = cap.stop(summary="test session")
        assert result == sid

        session = store.get_session(sid)
        assert session["ended_at"] is not None
        assert session["summary"] == "test session"

        messages = store.get_messages(sid)
        assert len(messages) == 3

    def test_context_manager(self, store):
        with SessionCapture(store=store, agent="ctx-test") as cap:
            cap.log_user("test")
            assert cap.session_id is not None

        # Session should be ended after context exit
        session = store.get_session(cap.session_id)
        assert session["ended_at"] is not None

    def test_auto_tag(self, store):
        cap = SessionCapture(store=store, agent="test", auto_tag=["auto1", "auto2"])
        cap.start()
        cap.stop()

        tags = store.get_tags(cap.session_id)
        assert "auto1" in tags
        assert "auto2" in tags

    def test_estimate_tokens(self):
        assert estimate_tokens("hello world") >= 2
        assert estimate_tokens("你好世界") >= 2
        assert estimate_tokens("") == 1

    def test_auto_summarize(self, store):
        cap = SessionCapture(store=store, agent="test")
        cap.start()
        cap.log_user("hello")
        cap.log_assistant("world")
        sid = cap.stop()
        session = store.get_session(sid)
        assert session["summary"] is not None
        assert "msgs" in session["summary"]


class TestMemorySearch:
    """Test suite for MemorySearch."""

    def test_search_empty(self, store):
        engine = MemorySearch(store)
        results = engine.search("anything")
        assert results["total"] == 0
        assert len(results["results"]) == 0

    def test_search_with_data(self, store):
        sid = store.create_session(agent="test-agent", workspace="test-ws")
        store.add_message(sid, "user", "What is Python?")
        store.add_message(sid, "assistant", "Python is a programming language.")
        store.add_tag(sid, "python")
        store.end_session(sid)

        engine = MemorySearch(store)

        # Basic search
        results = engine.search("Python")
        assert results["total"] >= 2

        # Agent filter
        results = engine.search("Python", agent="test-agent")
        assert results["total"] >= 1

        # Tag filter
        results = engine.search("Python", tag="python")
        assert results["total"] >= 1

    def test_recent_sessions(self, store):
        store.create_session(agent="a1")
        store.create_session(agent="a2")

        engine = MemorySearch(store)
        recent = engine.recent_sessions()
        assert len(recent) == 2

    def test_sessions_by_tag(self, store):
        sid = store.create_session()
        store.add_tag(sid, "urgent")

        engine = MemorySearch(store)
        sessions = engine.sessions_by_tag("urgent")
        assert len(sessions) == 1

    def test_export_markdown(self, store):
        sid = store.create_session(agent="exporter")
        store.add_message(sid, "user", "test")
        store.add_tag(sid, "export")
        store.end_session(sid)

        engine = MemorySearch(store)
        output = engine.export_session(sid, format="markdown")
        assert "Session:" in output
        assert "USER" in output

    def test_export_json(self, store):
        sid = store.create_session(agent="exporter")
        store.add_message(sid, "user", "test")
        store.end_session(sid)

        engine = MemorySearch(store)
        output = engine.export_session(sid, format="json")
        import json
        data = json.loads(output)
        assert "session" in data
        assert "messages" in data

    def test_summarize(self, store):
        sid = store.create_session(agent="test")
        store.end_session(sid)

        engine = MemorySearch(store)
        summary = engine.summarize(days=30)
        assert summary["sessions"] >= 1
        assert summary["messages"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])