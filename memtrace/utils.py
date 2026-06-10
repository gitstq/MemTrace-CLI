"""
MemTrace-CLI: Utilities and helper functions.

Provides shared utility functions used across the library.
"""

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def generate_session_id() -> str:
    """Generate a short, unique session ID."""
    import uuid
    return uuid.uuid4().hex[:12]


def estimate_tokens(text: str) -> int:
    """Estimate token count (~4 chars/token for ASCII, ~1.5 for CJK)."""
    cjk = sum(1 for c in text if '\u4e00' <= c <= '\u9fff' or '\u3040' <= c <= '\u30ff')
    ascii_chars = len(text) - cjk
    return max(1, int(ascii_chars / 4 + cjk / 1.5))


def truncate_content(text: str, max_len: int = 1000) -> str:
    """Truncate content while preserving whole lines."""
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit("\n", 1)[0] + "\n... [truncated]"


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format a timestamp in ISO-8601."""
    dt = dt or datetime.now(timezone.utc)
    return dt.isoformat()


def parse_timestamp(ts: str) -> Optional[datetime]:
    """Parse an ISO-8601 timestamp string."""
    try:
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


def safe_json_loads(text: str, default: Any = None) -> Any:
    """Safely parse JSON, returning default on failure."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def detect_content_type(text: str) -> str:
    """Detect whether content is code, natural language, or structured data."""
    code_patterns = [
        r'^(def |class |import |from |function|const |let |var )',
        r'^(fn |pub |impl |struct |enum |trait )',
        r'^(package |public class|private |protected )',
        r'^\s*[{(\[].*[})\]]\s*$',
        r'<(!DOCTYPE|html|div|script|style)',
    ]
    for pat in code_patterns:
        if re.search(pat, text, re.MULTILINE):
            return "code"
    structured_patterns = [
        r'^\s*[{\[].*[}\]]\s*$',
        r'^\s*[\w_-]+:\s',
        r'^---\s*$',
    ]
    for pat in structured_patterns:
        if re.search(pat, text, re.MULTILINE):
            return "structured"
    return "natural"


def ensure_dir(path: str) -> Path:
    """Ensure a directory exists, creating it if needed."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_data_dir() -> Path:
    """Get the platform-appropriate data directory."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "memtrace"


def colorize(text: str, color_code: str) -> str:
    """Wrap text in ANSI color codes if the terminal supports it."""
    if not sys.stdout.isatty():
        return text
    return f"{color_code}{text}\033[0m"