#!/usr/bin/env python3
"""
Unified CLI for the Endurance Training Knowledge Base.
"""

import argparse
import json
import sys

from main.utils.kb_engine import KBEngine
from main.utils.kb_engine.errors import KBEngineError


def handle_search(engine: KBEngine, args: argparse.Namespace) -> None:
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
    print("Synchronizing Knowledge Sources into the passage index...")
    status = engine.build_index()
    print(
        f"Index synchronized: {status.document_count} English sources, "
        f"{status.passage_count} Evidence Passages."
    )

    print("\nRebuilding Sitemap...")
    engine.build_sitemap()
    print("Sitemap rebuilt successfully!")


def handle_status(engine: KBEngine, _args: argparse.Namespace) -> None:
    print(json.dumps(engine.get_kb_status().to_dict(), indent=2))


def handle_validate(engine: KBEngine, _args: argparse.Namespace) -> int:
    res = engine.validate()

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
        for warn in res["warnings"][:15]:
            print(f"  ⚠️  {warn}")
        if len(res["warnings"]) > 15:
            print(f"  ... and {len(res['warnings']) - 15} more warnings.")
        print()

    if res["is_healthy"] and not res["warnings"]:
        print("🎉 100% HEALTHY! Knowledge Base passes all diagnostic checks.")
    elif res["is_healthy"]:
        print("✅ PASSED: No blocking errors found.")

    return 0 if res["is_healthy"] else 1


def handle_standardize(engine: KBEngine, args: argparse.Namespace) -> None:
    count = engine.standardize(force=args.force)
    print(f"Standardization complete! Updated frontmatter on {count} document(s).")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Endurance Training Knowledge Base CLI"
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
        "--top", "-n", type=int, default=5, help="Number of results to return"
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
    subparsers.add_parser("validate", help="Run diagnostic health checks")

    # standardize
    parser_standardize = subparsers.add_parser(
        "standardize", help="Standardize frontmatter"
    )
    parser_standardize.add_argument(
        "--force",
        action="store_true",
        help="Force re-generate frontmatter for all files",
    )

    args = parser.parse_args()
    engine = KBEngine()

    try:
        if args.command == "search":
            handle_search(engine, args)
        elif args.command == "build-index":
            handle_build_index(engine, args)
        elif args.command == "status":
            handle_status(engine, args)
        elif args.command == "validate":
            return handle_validate(engine, args)
        elif args.command == "standardize":
            handle_standardize(engine, args)
    except KBEngineError as error:
        print(f"{error.code}: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
