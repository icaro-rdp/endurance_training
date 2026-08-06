#!/usr/bin/env python3
"""
CLI Adapter for dynamic Knowledge Base sitemap generation via KBEngine.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from main.kb_engine import KBEngine

def main():
    engine = KBEngine()
    engine.build_sitemap()
    print(f"Generated {engine.index_file} successfully.")

if __name__ == "__main__":
    main()
