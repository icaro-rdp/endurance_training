#!/usr/bin/env python3
"""
CLI Adapter for Frontmatter Standardization via KBEngine.
"""

import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from main.kb_engine import KBEngine

def main():
    parser = argparse.ArgumentParser(description="Standardize frontmatter across Knowledge Base markdown files.")
    parser.add_argument("--force", action="store_true", help="Force re-generate frontmatter for all files")
    args = parser.parse_args()

    engine = KBEngine()
    count = engine.standardize(force=args.force)
    print(f"Standardization complete! Updated frontmatter on {count} document(s).")

if __name__ == "__main__":
    main()
