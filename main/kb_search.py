#!/usr/bin/env python3
"""
CLI Adapter for Knowledge Base Search via KBEngine.
"""

import sys
import json
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from main.kb_engine import KBEngine

def main():
    parser = argparse.ArgumentParser(description="Query the Endurance Training Knowledge Base.")
    parser.add_argument("query", type=str, help="Search query string")
    parser.add_argument("--category", type=str, default=None, help="Filter by category")
    parser.add_argument("--topic", type=str, default=None, help="Filter by topic")
    parser.add_argument("--top", "-n", type=int, default=5, help="Number of results to return")
    parser.add_argument("--format", type=str, choices=["llm", "json", "plain"], default="llm", help="Output format")
    parser.add_argument("--reindex", action="store_true", help="Force rebuild database index")

    args = parser.parse_args()

    engine = KBEngine()
    if args.reindex:
        count = engine.build_index()
        print(f"Reindexed {count} chunks.", file=sys.stderr)

    results = engine.search(args.query, category=args.category, topic=args.topic, top_k=args.top)

    if args.format == "json":
        print(json.dumps(results, indent=2))
    elif args.format == "plain":
        for r in results:
            print(f"[{r['category']}] {r['title']} ({r['rel_path']}:L{r['start_line']}) - Score: {r['bm25_score']}")
    else:
        print(engine.format_llm_context(results))

if __name__ == "__main__":
    main()
