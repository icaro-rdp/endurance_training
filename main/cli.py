#!/usr/bin/env python3
"""
Unified CLI for the Endurance Training Knowledge Base.
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root directory to python path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from main.utils.kb_engine import KBEngine


def handle_search(engine: KBEngine, args):
    if getattr(args, 'reindex', False):
        count = engine.fts.build_index()
        print(f"Reindexed {count} chunks.", file=sys.stderr)

    results = engine.search(args.query, category=args.category, topic=args.topic, top_k=args.top)

    if args.format == "json":
        print(json.dumps(results, indent=2))
    elif args.format == "plain":
        for r in results:
            print(f"[{r['category']}] {r['title']} ({r['rel_path']}:L{r['start_line']}) - Score: {r['bm25_score']}")
    else:
        print(engine.format_llm_context(results))

def handle_build_index(engine: KBEngine, args):
    print("Rebuilding FTS5 Search Index...")
    count = engine.fts.build_index()
    print(f"Index built successfully! Indexed {count} text chunks.")

    print("\nRebuilding Sitemap...")
    engine.validator.build_sitemap()
    print("Sitemap rebuilt successfully!")

def handle_validate(engine: KBEngine, args):
    res = engine.validator.validate_health()

    print("==========================================")
    print("      Knowledge Base Diagnostic Audit     ")
    print("==========================================")
    print(f"Total Documents Checked: {res['total_docs']}")
    print(f"Errors Found:             {len(res['errors'])}")
    print(f"Warnings Found:           {len(res['warnings'])}")
    print("------------------------------------------\n")

    if res['errors']:
        print("ERRORS:")
        for err in res['errors']:
            print(f"  ❌ {err}")
        print()

    if res['warnings']:
        print("WARNINGS:")
        for warn in res['warnings'][:15]:
            print(f"  ⚠️  {warn}")
        if len(res['warnings']) > 15:
            print(f"  ... and {len(res['warnings']) - 15} more warnings.")
        print()

    if res['is_healthy'] and not res['warnings']:
        print("🎉 100% HEALTHY! Knowledge Base passes all diagnostic checks.")
    elif res['is_healthy']:
        print("✅ PASSED: No blocking errors found.")

    sys.exit(0 if res['is_healthy'] else 1)

def handle_standardize(engine: KBEngine, args):
    count = engine.standardize(force=args.force)
    print(f"Standardization complete! Updated frontmatter on {count} document(s).")

def main():
    parser = argparse.ArgumentParser(description="Endurance Training Knowledge Base CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # search
    parser_search = subparsers.add_parser("search", help="Search the knowledge base")
    parser_search.add_argument("query", type=str, help="Search query string")
    parser_search.add_argument("--category", type=str, default=None, help="Filter by category")
    parser_search.add_argument("--topic", type=str, default=None, help="Filter by topic")
    parser_search.add_argument("--top", "-n", type=int, default=5, help="Number of results to return")
    parser_search.add_argument("--format", type=str, choices=["llm", "json", "plain"], default="llm", help="Output format")
    parser_search.add_argument("--reindex", action="store_true", help="Force rebuild database index before searching")

    # build-index
    parser_build = subparsers.add_parser("build-index", help="Rebuild search index and sitemap")

    # validate
    parser_validate = subparsers.add_parser("validate", help="Run diagnostic health checks")

    # standardize
    parser_standardize = subparsers.add_parser("standardize", help="Standardize frontmatter")
    parser_standardize.add_argument("--force", action="store_true", help="Force re-generate frontmatter for all files")

    args = parser.parse_args()
    engine = KBEngine()

    if args.command == "search":
        handle_search(engine, args)
    elif args.command == "build-index":
        handle_build_index(engine, args)
    elif args.command == "validate":
        handle_validate(engine, args)
    elif args.command == "standardize":
        handle_standardize(engine, args)

if __name__ == "__main__":
    main()
