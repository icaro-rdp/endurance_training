"""
Validator and Sitemap Builder sub-module.
"""

import os
import re
import yaml
from pathlib import Path
from main.kb_engine.frontmatter import FrontmatterManager

REQUIRED_FM_KEYS = ["title", "category", "topics", "summary"]
VALID_CATEGORIES = ["metrics", "hiit", "zone2", "strength", "nutrition", "physiology", "periodization", "book", "general"]

class KBValidator:
    def __init__(self, kb_dir: Path, index_file: Path):
        self.kb_dir = kb_dir
        self.index_file = index_file
        self.fm_manager = FrontmatterManager(kb_dir)

    def build_sitemap(self) -> str:
        docs = []
        for root, _, files in os.walk(self.kb_dir):
            for file in files:
                if file.endswith(".md") and file not in ["INDEX.md", "TAXONOMY.md"]:
                    file_path = Path(root) / file
                    fm, _ = self.fm_manager.parse_document(file_path)
                    if fm:
                        fm["file_path"] = file_path
                        fm["rel_path"] = str(file_path.relative_to(self.kb_dir))
                        docs.append(fm)

        categories = {}
        for doc in docs:
            cat = doc.get("category", "general")
            categories.setdefault(cat, []).append(doc)

        lines = [
            "# Master Knowledge Base Index",
            "",
            "Welcome to the **Endurance Training Knowledge Base**. This document serves as the primary sitemap and entry point for LLMs and researchers.",
            "",
            "---",
            "",
            "## Quick Links",
            "- 📖 [Taxonomy & Definitions](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/TAXONOMY.md)",
            "- 📚 [Books Summaries](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Books/_summary/INDEX.md)",
            "",
            "---",
            "",
            "## Document Catalog by Category",
            ""
        ]

        cat_order = ["metrics", "hiit", "zone2", "strength", "nutrition", "physiology", "periodization", "book", "general"]
        sorted_cats = sorted(categories.keys(), key=lambda c: cat_order.index(c) if c in cat_order else 99)

        for cat in sorted_cats:
            cat_docs = categories[cat]
            lines.append(f"### Category: `{cat.upper()}`")
            lines.append(f"Total documents: {len(cat_docs)}")
            lines.append("")

            for doc in sorted(cat_docs, key=lambda d: d.get("title", "")):
                rel = doc["rel_path"]
                abs_path = str(doc["file_path"])
                title = doc.get("title", doc["rel_path"])
                topics = ", ".join(doc.get("topics", []))
                summary = doc.get("summary", "")

                lines.append(f"- **[{title}](file://{abs_path})** (`{rel}`)")
                if topics:
                    lines.append(f"  - **Topics**: {topics}")
                if summary:
                    lines.append(f"  - **Summary**: {summary}")
                lines.append("")

            lines.append("---")
            lines.append("")

        sitemap_content = "\n".join(lines)
        with open(self.index_file, "w", encoding="utf-8") as f:
            f.write(sitemap_content)

        return sitemap_content

    def validate_health(self) -> dict:
        errors = []
        warnings = []
        total_docs = 0

        index_text = self.index_file.read_text(encoding="utf-8") if self.index_file.exists() else ""

        for root, _, files in os.walk(self.kb_dir):
            for file in files:
                if file.endswith(".md") and file not in ["INDEX.md", "TAXONOMY.md"]:
                    total_docs += 1
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(self.kb_dir)

                    content = file_path.read_text(encoding="utf-8", errors="replace")

                    if not content.startswith("---\n"):
                        errors.append(f"[{rel_path}] Missing YAML frontmatter header ('---').")
                        continue

                    parts = content.split("---\n", 2)
                    if len(parts) < 3:
                        errors.append(f"[{rel_path}] Malformed YAML frontmatter.")
                        continue

                    try:
                        fm = yaml.safe_load(parts[1]) or {}
                    except Exception as e:
                        errors.append(f"[{rel_path}] YAML Syntax Error: {e}")
                        continue

                    for key in REQUIRED_FM_KEYS:
                        if key not in fm or not fm[key]:
                            errors.append(f"[{rel_path}] Missing required frontmatter key '{key}'.")

                    category = fm.get("category")
                    if category and category not in VALID_CATEGORIES:
                        warnings.append(f"[{rel_path}] Category '{category}' not in predefined taxonomy list.")

                    if str(rel_path) not in index_text and str(file_path.name) not in index_text:
                        warnings.append(f"[{rel_path}] File not indexed in INDEX.md.")

                    link_pattern = re.compile(r'\[.*?\]\((?!http|file)(.*?)\)')
                    for match in link_pattern.finditer(parts[2]):
                        link_target = match.group(1).split('#')[0]
                        if link_target:
                            resolved_path = (file_path.parent / link_target).resolve()
                            if not resolved_path.exists():
                                warnings.append(f"[{rel_path}] Broken relative link: '{link_target}'")

        return {
            "total_docs": total_docs,
            "errors": errors,
            "warnings": warnings,
            "is_healthy": len(errors) == 0
        }
