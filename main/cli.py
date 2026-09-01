#!/usr/bin/env python3
"""
Unified CLI for the Endurance Training Knowledge Base.
"""

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from main.utils.kb_engine import KBEngine
from main.utils.kb_engine.classifier import create_model_adapter
from main.utils.kb_engine.errors import KBEngineError


def handle_search(engine: KBEngine, args: argparse.Namespace) -> None:
    """Run a search command and render the selected output format."""
    if ";;" in args.query or "||" in args.query:
        delimiter = ";;" if ";;" in args.query else "||"
        sub_queries = [q.strip() for q in args.query.split(delimiter) if q.strip()]
        results = engine.multi_search(
            sub_queries,
            category=args.category,
            topic=args.topic,
            source_slug=args.source,
            top_k=args.top,
        )
    else:
        results = engine.search(
            args.query,
            category=args.category,
            topic=args.topic,
            source_slug=args.source,
            top_k=args.top,
        )

    if args.format == "json":
        print(json.dumps([result.to_dict() for result in results], indent=2))
    elif args.format == "plain":
        for result in results:
            passage = result.passage
            print(
                f"[{passage.category}] {passage.title} "
                f"({passage.rel_path}:L{passage.start_line}-L{passage.end_line}) "
                f"- Score: {result.lexical_score}"
            )
    else:
        print(engine.format_llm_context(results))


def handle_build_index(engine: KBEngine, _args: argparse.Namespace) -> None:
    """Synchronize the sitemap and Derived Index."""
    print("Rebuilding Sitemap and Taxonomy...")
    engine.build_sitemap()
    print("Synchronizing Knowledge Sources into the passage index...")
    status = engine.build_index()
    print(
        f"Index synchronized: {status.document_count} English sources, "
        f"{status.passage_count} Evidence Passages."
    )
    metrics = engine.last_index_build_metrics
    if metrics is not None:
        print(
            "Build work: "
            f"reused {metrics.reused_source_count} sources / "
            f"{metrics.reused_passage_count} passages; "
            f"rebuilt {metrics.rebuilt_source_count} sources / "
            f"embedded {metrics.embedded_passage_count} passages."
        )
        print(
            "Build timing: "
            f"{metrics.total_seconds:.2f}s total "
            f"(manifest {metrics.manifest_seconds:.2f}s, "
            f"chunking {metrics.chunking_seconds:.2f}s, "
            f"model setup {metrics.model_initialization_seconds:.2f}s, "
            f"embedding {metrics.embedding_seconds:.2f}s, "
            f"vector insert {metrics.vector_insertion_seconds:.2f}s, "
            f"SQLite/FTS {metrics.sqlite_fts_seconds:.2f}s, "
            f"validation {metrics.validation_seconds:.2f}s, "
            f"replacement {metrics.replacement_seconds:.2f}s)."
        )


def handle_status(engine: KBEngine, _args: argparse.Namespace) -> None:
    """Render Derived Index freshness status."""
    print(json.dumps(engine.get_kb_status().to_dict(), indent=2))


def handle_validate(engine: KBEngine, args: argparse.Namespace) -> int:
    """Render Knowledge Base validation diagnostics."""
    res = engine.validate(source_rel_path=args.source)

    print("==========================================")
    print("      Knowledge Base Diagnostic Audit     ")
    print("==========================================")
    print(f"Total Documents Checked: {res['total_docs']}")
    print(f"Errors Found:             {len(res['errors'])}")
    print(f"Warnings Found:           {len(res['warnings'])}")
    print("------------------------------------------\n")

    if res["errors"]:
        print("ERRORS:")
        for err in res["errors"]:
            print(f"  ❌ {err}")
        print()

    if res["warnings"]:
        print("WARNINGS:")
        warning_limit = len(res["warnings"]) if args.source else 15
        for warn in res["warnings"][:warning_limit]:
            print(f"  ⚠️  {warn}")
        if len(res["warnings"]) > warning_limit:
            print(f"  ... and {len(res['warnings']) - 15} more warnings.")
        print()

    if res["is_healthy"] and not res["warnings"]:
        print("🎉 100% HEALTHY! Knowledge Base passes all diagnostic checks.")
    elif res["is_healthy"]:
        print("✅ PASSED: No blocking errors found.")

    return 0 if res["is_healthy"] else 1


def handle_tag(engine: KBEngine, args: argparse.Namespace) -> int:
    """Adapt tag arguments to the Knowledge Base facade and render results."""
    adapter = create_model_adapter(args.backend, args.model, args.ollama_host)
    is_dry_run = not args.apply
    tagged_list = engine.tag_sources(
        path=args.path,
        recursive=args.all,
        dry_run=is_dry_run,
        adapter=adapter,
    )

    if args.all:
        print(f"Processed {len(tagged_list)} documents.")
    for source, result in tagged_list:
        status = "Dry-run" if is_dry_run else "Applied"
        print(f"\n[{status}] {source.rel_path}")
        print(f"  Title:    {source.title}")
        print(f"  Category: {result.category}")
        print(f"  Topics:   {', '.join(result.topics)}")
        print(f"  Summary:  {result.summary}")
        if result.topic_evidence:
            print("  Evidence:")
            for topic, evidence in result.topic_evidence.items():
                print(f"    - {topic}: {evidence}")
    return 0


def _add_tag_arguments(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Path to Markdown article or directory (relative to KB or filesystem)",
    )
    p.add_argument(
        "--all",
        action="store_true",
        help="Classify all Markdown sources in Knowledge Base or directory",
    )
    mode_group = p.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview classification without modifying files (default)",
    )
    mode_group.add_argument(
        "--apply",
        action="store_true",
        help="Write classified metadata directly into YAML frontmatter",
    )
    p.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model identifier (e.g. mlx-community/Qwen2.5-7B-Instruct-4bit)",
    )
    p.add_argument(
        "--backend",
        choices=["mlx", "ollama"],
        default="mlx",
        help="Local inference backend (default: mlx)",
    )
    p.add_argument(
        "--ollama-host",
        type=str,
        default="http://localhost:11434",
        help="Ollama host URL (default: http://localhost:11434)",
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Endurance Knowledge Base command-line interface."""
    parser = argparse.ArgumentParser(
        description="Endurance Training Knowledge Base CLI"
    )
    parser.add_argument(
        "--kb-dir",
        type=Path,
        default=None,
        help=(
            "Knowledge Base directory (default: ENDURANCE_KB_DIR, then "
            "./Knowledge_base)"
        ),
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=None,
        help="Local SQLite Derived Index path",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # search
    parser_search = subparsers.add_parser("search", help="Search the knowledge base")
    parser_search.add_argument("query", type=str, help="Search query string")
    parser_search.add_argument(
        "--category", type=str, default=None, help="Filter by category"
    )
    parser_search.add_argument(
        "--topic", type=str, default=None, help="Filter by topic"
    )
    parser_search.add_argument(
        "--source", type=str, default=None, help="Filter by source slug"
    )
    parser_search.add_argument(
        "--top",
        "-n",
        type=int,
        default=20,
        help="Maximum number of retained passages to display (1 to 20; default: 20)",
    )
    parser_search.add_argument(
        "--format",
        type=str,
        choices=["llm", "json", "plain"],
        default="llm",
        help="Output format",
    )

    # build-index
    subparsers.add_parser("build-index", help="Rebuild search index and sitemap")

    # status
    subparsers.add_parser("status", help="Inspect Derived Index freshness")

    # validate
    parser_validate = subparsers.add_parser(
        "validate", help="Run diagnostic health checks"
    )
    parser_validate.add_argument(
        "--source",
        default=None,
        help="Validate one exact path relative to Knowledge_base",
    )

    # tag & auto-tag
    parser_tag = subparsers.add_parser(
        "tag",
        help="Classify canonical topics and bottom-up category using local LLM",
    )
    _add_tag_arguments(parser_tag)

    parser_autotag = subparsers.add_parser(
        "auto-tag",
        help="Classify canonical topics and bottom-up category using local LLM",
    )
    _add_tag_arguments(parser_autotag)

    args = parser.parse_args(argv)

    try:
        engine = KBEngine(kb_dir=args.kb_dir, db_path=args.db_path)
        if args.command == "search":
            handle_search(engine, args)
        elif args.command == "build-index":
            handle_build_index(engine, args)
        elif args.command == "status":
            handle_status(engine, args)
        elif args.command == "validate":
            return handle_validate(engine, args)
        elif args.command in ("tag", "auto-tag"):
            return handle_tag(engine, args)
    except KBEngineError as error:
        print(f"{error.code}: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
