#!/usr/bin/env python3
"""
CLI Adapter for Knowledge Base diagnostic validation via KBEngine.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from main.kb_engine import KBEngine

def main():
    engine = KBEngine()
    res = engine.validate()

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

if __name__ == "__main__":
    main()
