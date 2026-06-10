"""
MemTrace-CLI: Terminal UI dashboard.

Provides a rich TUI dashboard for browsing sessions, searching memory,
and viewing statistics — all with zero external dependencies beyond
the Python standard library.

Uses simple ANSI terminal sequences for rendering (no curses/ncurses
required for basic operation).
"""

import os
import shutil
import sys
import time
from datetime import datetime, timezone
from typing import Optional

from .store import MemoryStore
from .search import MemorySearch


# ── ANSI helpers ───────────────────────────────────────────────────

class Style:
    """Simple ANSI style constants."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"
    BG_BLUE = "\033[44m"
    BG_GREEN = "\033[42m"
    BG_DARK = "\033[40m"


def _term_width() -> int:
    """Get terminal width."""
    return shutil.get_terminal_size().columns or 80


def _term_height() -> int:
    """Get terminal height."""
    return shutil.get_terminal_size().lines or 24


def _truncate(text: str, max_len: int) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def _format_size(size_bytes: int) -> str:
    """Format byte size human-readably."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def _time_ago(iso_str: str) -> str:
    """Format ISO timestamp as relative time."""
    if not iso_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso_str)
        now = datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = now - dt
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return f"{seconds}s ago"
        if seconds < 3600:
            return f"{seconds // 60}m ago"
        if seconds < 86400:
            return f"{seconds // 3600}h ago"
        return f"{seconds // 86400}d ago"
    except (ValueError, TypeError):
        return iso_str[:10] if iso_str else "N/A"


# ── Renderers ──────────────────────────────────────────────────────

def render_header(title: str) -> None:
    """Render a styled header."""
    width = _term_width()
    print()
    print(f"{Style.BG_BLUE}{Style.WHITE}{Style.BOLD} {title.center(width - 2)} {Style.RESET}")
    print()


def render_stats(store: MemoryStore) -> None:
    """Render memory store statistics."""
    stats = store.stats()
    width = _term_width()

    render_header(" MEMTRACE STATISTICS ")

    left_col = [
        ("Sessions", str(stats["sessions"])),
        ("Active", str(stats["active_sessions"])),
        ("Messages", str(stats["messages"])),
        ("Total Tokens", str(stats["total_tokens"])),
        ("DB Size", _format_size(stats["db_size_bytes"])),
    ]

    right_col = []
    for a in stats.get("agents", []):
        right_col.append((f"  {a['agent']}", str(a["cnt"])))

    # Two-column layout
    for i in range(max(len(left_col), len(right_col))):
        left = ""
        right = ""
        if i < len(left_col):
            k, v = left_col[i]
            left = f"  {Style.BOLD}{k}:{Style.RESET} {Style.GREEN}{v}{Style.RESET}"
        if i < len(right_col):
            k, v = right_col[i]
            right = f"  {Style.BOLD}{k}:{Style.RESET} {Style.YELLOW}{v}{Style.RESET}"

        if right:
            # Align to center
            left_str = left.ljust(width // 2)
            print(f"{left_str}{right}")
        else:
            print(left)

    print(f"\n  {Style.DIM}DB Path: {stats['db_path']}{Style.RESET}")
    print()


def render_sessions(
    store: MemoryStore,
    sessions: list[dict],
    title: str = " SESSIONS ",
    show_tags: bool = True,
) -> None:
    """Render a list of sessions."""
    if not sessions:
        print(f"\n  {Style.DIM}No sessions found.{Style.RESET}\n")
        return

    width = _term_width()
    render_header(title)

    for i, s in enumerate(sessions):
        sid = s["id"]
        agent = s.get("agent", "?")
        summary = s.get("summary") or ""
        started = _time_ago(s.get("started_at", ""))
        ended = "active" if s.get("ended_at") is None else _time_ago(s.get("ended_at", ""))
        tokens = s.get("token_count", 0)

        tags = store.get_tags(sid) if show_tags else []

        # Session line
        line = (
            f"  {Style.BOLD}{sid}{Style.RESET} "
            f"{Style.CYAN}{agent}{Style.RESET} "
            f"{Style.GRAY}{started}{Style.RESET}"
        )
        print(line)

        # Summary (truncated)
        if summary:
            print(f"    {_truncate(summary, width - 6)}")

        # Tags
        if tags:
            tag_str = " ".join(f"{Style.GREEN}#{t}{Style.RESET}" for t in tags[:5])
            print(f"    {tag_str}")

        # Meta line
        meta_parts = []
        if tokens:
            meta_parts.append(f"~{tokens} tokens")
        meta_parts.append(f"ended: {ended}")
        print(f"    {Style.GRAY}{', '.join(meta_parts)}{Style.RESET}")

        if i < len(sessions) - 1:
            print()

    print(f"\n  {Style.DIM}Total: {len(sessions)} sessions{Style.RESET}\n")


def render_search_results(results: dict) -> None:
    """Render search results."""
    items = results.get("results", [])
    total = results.get("total", 0)
    query = results.get("query", "")

    if not items:
        print(f"\n  {Style.DIM}No results for '{query}'.{Style.RESET}\n")
        return

    width = _term_width()
    render_header(f' SEARCH: "{query}" ({total} results) ')

    for i, msg in enumerate(items):
        role = msg["role"].upper()
        content = msg.get("content", "")
        session_id = msg.get("session_id", "?")
        agent = msg.get("agent", "?")
        created = _time_ago(msg.get("created_at", ""))
        tags = msg.get("tags", [])

        # Role colored indicator
        role_colors = {
            "USER": Style.GREEN,
            "ASSISTANT": Style.BLUE,
            "TOOL": Style.YELLOW,
            "SYSTEM": Style.MAGENTA,
        }
        role_color = role_colors.get(role, Style.WHITE)

        line = (
            f"  [{role_color}{role}{Style.RESET}] "
            f"{Style.CYAN}{agent}{Style.RESET} "
            f"{Style.GRAY}{session_id[:8]}{Style.RESET} "
            f"{Style.GRAY}{created}{Style.RESET}"
        )
        print(line)

        # Content preview
        preview = _truncate(content.strip(), width - 6)
        print(f"    {preview}")

        if tags:
            tag_str = " ".join(f"{Style.GREEN}#{t}{Style.RESET}" for t in tags[:3])
            print(f"    {tag_str}")

        if i < len(items) - 1:
            print()

    print(f"\n  {Style.DIM}Showing {len(items)} of {total} results{Style.RESET}\n")


def render_session_detail(store: MemoryStore, session_id: str) -> None:
    """Render a detailed view of a single session."""
    session = store.get_session(session_id)
    if not session:
        print(f"\n  {Style.RED}Session '{session_id}' not found.{Style.RESET}\n")
        return

    messages = store.get_messages(session_id)
    tags = store.get_tags(session_id)
    width = _term_width()

    render_header(f" SESSION: {session_id} ")

    # Metadata
    print(f"  {Style.BOLD}Agent:{Style.RESET}     {Style.CYAN}{session.get('agent', 'N/A')}{Style.RESET}")
    print(f"  {Style.BOLD}Workspace:{Style.RESET}  {session.get('workspace', 'default')}")
    print(f"  {Style.BOLD}Started:{Style.RESET}    {session.get('started_at', 'N/A')}")
    print(f"  {Style.BOLD}Ended:{Style.RESET}      {session.get('ended_at', 'N/A')}")
    print(f"  {Style.BOLD}Tokens:{Style.RESET}     {session.get('token_count', 0)}")

    summary = session.get("summary")
    if summary:
        print(f"  {Style.BOLD}Summary:{Style.RESET}   {summary}")

    if tags:
        tag_str = " ".join(f"{Style.GREEN}#{t}{Style.RESET}" for t in tags)
        print(f"  {Style.BOLD}Tags:{Style.RESET}      {tag_str}")

    print()
    print(f"  {Style.BOLD}{'─' * (width - 4)}{Style.RESET}")
    print()

    # Messages
    for i, msg in enumerate(messages):
        role = msg["role"].upper()
        content = msg.get("content", "")
        tool_name = msg.get("tool_name")

        role_label = {
            "USER": f"{Style.GREEN}USER{Style.RESET}",
            "ASSISTANT": f"{Style.BLUE}ASSISTANT{Style.RESET}",
            "TOOL": f"{Style.YELLOW}TOOL{Style.RESET}",
            "SYSTEM": f"{Style.MAGENTA}SYSTEM{Style.RESET}",
        }.get(role, role)

        tool_info = f" [{Style.DIM}{tool_name}{Style.RESET}]" if tool_name else ""
        print(f"  {Style.BOLD}#{i+1}{Style.RESET} {role_label}{tool_info}")

        # Truncate very long content for display
        if len(content) > width:
            content_preview = content[:width - 6] + "..."
        else:
            content_preview = content

        for line in content_preview.split("\n"):
            print(f"    {Style.GRAY}{line}{Style.RESET}" if not line.strip() else f"    {line}")

        print()


def render_welcome() -> None:
    """Render welcome banner."""
    width = min(_term_width(), 80)
    print()
    print(f"{'=' * width}")
    print(f"{Style.BOLD}{Style.CYAN}  MemTrace-CLI{Style.RESET}  {Style.DIM}— Agent Memory Engine{Style.RESET}")
    print(f"  {Style.GRAY}Lightweight terminal AI agent shared memory{Style.RESET}")
    print(f"{'=' * width}")
    print()
    print(f"  {Style.BOLD}Commands:{Style.RESET}")
    print(f"    {Style.GREEN}memtrace capture{Style.RESET}  <command>   Capture an agent session")
    print(f"    {Style.GREEN}memtrace search{Style.RESET}   <query>     Search across memory")
    print(f"    {Style.GREEN}memtrace list{Style.RESET}                 List recent sessions")
    print(f"    {Style.GREEN}memtrace show{Style.RESET}    <id>        Show session details")
    print(f"    {Style.GREEN}memtrace stats{Style.RESET}               Show memory statistics")
    print(f"    {Style.GREEN}memtrace export{Style.RESET}  <id>        Export session")
    print(f"    {Style.GREEN}memtrace dashboard{Style.RESET}           Open TUI dashboard")
    print(f"    {Style.GREEN}memtrace tags{Style.RESET}                List all tags")
    print()


def render_dashboard(store: MemoryStore) -> None:
    """
    Simple paginated TUI dashboard.
    
    Uses a read-evaluate loop with basic terminal interaction.
    No external dependencies required.
    """
    search_engine = MemorySearch(store)
    page = 0
    page_size = 10

    try:
        while True:
            os.system("clear" if os.name == "posix" else "cls")
            render_welcome()

            # Stats bar
            stats = store.stats()
            print(
                f"  {Style.BOLD}📊 {stats['sessions']}{Style.RESET} sessions · "
                f"{stats['messages']} messages · "
                f"{stats['active_sessions']} active · "
                f"{_format_size(stats['db_size_bytes'])}"
            )
            print()

            # Recent sessions
            sessions = store.list_sessions(limit=page_size, offset=page * page_size)
            render_sessions(store, sessions, title=f" RECENT SESSIONS (page {page + 1}) ")

            # Menu
            print(f"  {Style.BOLD}Options:{Style.RESET}")
            print(f"    {Style.GREEN}[n]{Style.RESET} next page    {Style.GREEN}[p]{Style.RESET} prev page")
            print(f"    {Style.GREEN}[s]{Style.RESET} search       {Style.GREEN}[v]{Style.RESET} view session")
            print(f"    {Style.GREEN}[q]{Style.RESET} quit")
            print()

            choice = input(f"  {Style.BOLD}>{Style.RESET} ").strip().lower()

            if choice == "q":
                break
            elif choice == "n":
                page += 1
            elif choice == "p":
                page = max(0, page - 1)
            elif choice == "s":
                query = input(f"  {Style.BOLD}Search:{Style.RESET} ").strip()
                if query:
                    results = search_engine.search(query, limit=20)
                    render_search_results(results)
                    input(f"  {Style.GRAY}Press Enter to continue...{Style.RESET}")
            elif choice == "v":
                sid = input(f"  {Style.BOLD}Session ID:{Style.RESET} ").strip()
                if sid:
                    render_session_detail(store, sid)
                    input(f"  {Style.GRAY}Press Enter to continue...{Style.RESET}")
            elif choice and choice.isdigit():
                sid = choice
                render_session_detail(store, sid)
                input(f"  {Style.GRAY}Press Enter to continue...{Style.RESET}")

    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        print(f"\n  {Style.GREEN}Bye!{Style.RESET}\n")