"""
MemTrace-CLI: CLI entry point — multi-command dispatcher.

Provides the main 'memtrace' command with subcommands:
  capture, search, list, show, stats, export, tags, dashboard
"""

import argparse
import os
import sys
from pathlib import Path
from typing import NoReturn

from . import __version__
from .store import MemoryStore
from .session import SessionCapture
from .search import MemorySearch
from .tui import (
    render_stats,
    render_sessions,
    render_search_results,
    render_session_detail,
    render_welcome,
    render_dashboard,
)


def _get_store(args: argparse.Namespace) -> MemoryStore:
    """Create a MemoryStore from CLI args."""
    return MemoryStore(db_dir=args.db_dir)


def cmd_capture(args: argparse.Namespace) -> None:
    """Capture an agent session by wrapping a CLI command."""
    if not args.command:
        print("Usage: memtrace capture <command> [args...]")
        print("  e.g., memtrace capture claude -p 'hello'")
        sys.exit(1)

    store = _get_store(args)
    capture = SessionCapture(
        store=store,
        agent=args.agent,
        workspace=args.workspace,
        auto_tag=args.tag,
    )

    print(f"🧠 Capturing: {' '.join(args.command)}")
    print(f"   Agent: {args.agent}  Workspace: {args.workspace}")
    if args.tag:
        print(f"   Tags: {', '.join(args.tag)}")
    print()

    exit_code = capture.wrap_command(args.command)

    print(f"\n✅ Session captured: {capture.session_id or 'N/A'}")
    print(f"   Exit code: {exit_code}")
    sys.exit(exit_code)


def cmd_search(args: argparse.Namespace) -> None:
    """Search across captured memory."""
    store = _get_store(args)
    engine = MemorySearch(store)

    results = engine.search(
        query=args.query,
        agent=args.agent,
        workspace=args.workspace,
        tag=args.tag,
        days=args.days,
        limit=args.limit,
    )

    render_search_results(results)


def cmd_list(args: argparse.Namespace) -> None:
    """List recent sessions."""
    store = _get_store(args)

    sessions = store.list_sessions(
        agent=args.agent,
        workspace=args.workspace,
        limit=args.limit,
    )

    render_sessions(store, sessions, title=" SESSIONS ")
    print(f"  Tip: use '{Path(sys.argv[0]).name} show <id>' for details\n")


def cmd_show(args: argparse.Namespace) -> None:
    """Show detailed session view."""
    store = _get_store(args)
    render_session_detail(store, args.session_id)


def cmd_stats(args: argparse.Namespace) -> None:
    """Show memory store statistics."""
    store = _get_store(args)
    render_stats(store)


def cmd_export(args: argparse.Namespace) -> None:
    """Export a session to a file or stdout."""
    store = _get_store(args)
    engine = MemorySearch(store)

    output = engine.export_session(
        session_id=args.session_id,
        format=args.format,
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"✅ Exported to {args.output}")
    else:
        print(output)


def cmd_tags(args: argparse.Namespace) -> None:
    """List all tags with their usage counts."""
    store = _get_store(args)
    tags = store.list_all_tags()

    if not tags:
        print("\n  No tags found.\n")
        return

    print(f"\n  {len(tags)} tags:\n")
    for tag, count in tags:
        print(f"  #{tag:<20} {count} sessions")
    print()


def cmd_dashboard(args: argparse.Namespace) -> None:
    """Open the interactive TUI dashboard."""
    store = _get_store(args)
    render_dashboard(store)


def cmd_init(args: argparse.Namespace) -> None:
    """Initialize the memory store."""
    store = _get_store(args)
    stats = store.stats()
    print(f"✅ MemTrace store initialized at: {store.db_path}")
    print(f"   Sessions: {stats['sessions']}")
    print(f"   Messages: {stats['messages']}")


def cmd_delete(args: argparse.Namespace) -> None:
    """Delete a session."""
    store = _get_store(args)
    if args.yes or input(f"Delete session {args.session_id}? [y/N] ").lower() == "y":
        if store.delete_session(args.session_id):
            print(f"✅ Session {args.session_id} deleted.")
        else:
            print(f"❌ Session {args.session_id} not found.")


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="memtrace",
        description="🧠 MemTrace-CLI — Lightweight Terminal AI Agent Shared Memory Engine",
        epilog="Documentation: https://github.com/YOUR_USERNAME/MemTrace-CLI",
    )
    parser.add_argument(
        "--db-dir",
        default=None,
        help="Custom database directory (default: ~/.memtrace)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"MemTrace-CLI v{__version__}",
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # capture
    p_cap = sub.add_parser("capture", help="Capture an agent session")
    p_cap.add_argument("command", nargs=argparse.REMAINDER, help="Command to capture")
    p_cap.add_argument("--agent", default="cli", help="Agent name")
    p_cap.add_argument("--workspace", default="default", help="Workspace name")
    p_cap.add_argument("--tag", action="append", default=None, help="Tag to apply")
    p_cap.set_defaults(func=cmd_capture)

    # search
    p_search = sub.add_parser("search", help="Search across memory")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--agent", help="Filter by agent")
    p_search.add_argument("--workspace", help="Filter by workspace")
    p_search.add_argument("--tag", help="Filter by tag")
    p_search.add_argument("--days", type=int, default=None, help="Time range in days")
    p_search.add_argument("--limit", type=int, default=20, help="Max results")
    p_search.set_defaults(func=cmd_search)

    # list
    p_list = sub.add_parser("list", help="List sessions")
    p_list.add_argument("--agent", help="Filter by agent")
    p_list.add_argument("--workspace", help="Filter by workspace")
    p_list.add_argument("--limit", type=int, default=20, help="Max sessions")
    p_list.set_defaults(func=cmd_list)

    # show
    p_show = sub.add_parser("show", help="Show session details")
    p_show.add_argument("session_id", help="Session ID")
    p_show.set_defaults(func=cmd_show)

    # stats
    sub.add_parser("stats", help="Show memory statistics").set_defaults(func=cmd_stats)

    # export
    p_export = sub.add_parser("export", help="Export a session")
    p_export.add_argument("session_id", help="Session ID")
    p_export.add_argument("--format", default="markdown", choices=["markdown", "json", "text"], help="Export format")
    p_export.add_argument("-o", "--output", help="Output file (default: stdout)")
    p_export.set_defaults(func=cmd_export)

    # tags
    sub.add_parser("tags", help="List all tags").set_defaults(func=cmd_tags)

    # dashboard
    sub.add_parser("dashboard", help="Open interactive TUI dashboard").set_defaults(func=cmd_dashboard)

    # init
    sub.add_parser("init", help="Initialize the memory store").set_defaults(func=cmd_init)

    # delete
    p_del = sub.add_parser("delete", help="Delete a session")
    p_del.add_argument("session_id", help="Session ID to delete")
    p_del.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    p_del.set_defaults(func=cmd_delete)

    return parser


def main(argv: list[str] | None = None) -> None:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        # Show welcome if no command
        store = _get_store(args)
        render_welcome()
        return

    args.func(args)