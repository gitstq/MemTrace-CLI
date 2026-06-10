"""
MemTrace-CLI — Lightweight Terminal AI Agent Shared Memory Engine

A zero-dependency Python CLI tool that captures, indexes, and retrieves
AI coding agent sessions as persistent, searchable memory.

Inspired by the concept of shared agent memory (activeloopai/hivemind),
reimagined as a lightweight, local-first, cross-platform CLI utility.
"""

__version__ = "0.1.0"
__author__ = "MemTrace Team"
__license__ = "MIT"

from .store import MemoryStore
from .session import SessionCapture
from .search import MemorySearch

__all__ = ["MemoryStore", "SessionCapture", "MemorySearch"]