"""
Frontmatter parsing, inferencing, and standardization module.
"""

import os
import re
import yaml
from pathlib import Path

from .taxonomy import TaxonomyRegistry

class FrontmatterManager:
    def __init__(self, kb_dir: Path, taxonomy: TaxonomyRegistry):
        self.kb_dir = kb_dir
        self.taxonomy = taxonomy

    def determine_category(self, file_path: Path) -> str:
        parts = file_path.relative_to(self.kb_dir).parts
        cat_map = self.taxonomy.category_map()
        for part in parts:
            if part in cat_map:
                return cat_map[part]
        return "general"

    def parse_document(self, file_path: Path):
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        frontmatter = {}
        body = content

        if content.startswith("---\n"):
            parts = content.split("---\n", 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    body = parts[2]
                except Exception:
                    pass

        return frontmatter, body

    def infer_metadata(self, content: str, file_path: Path):
        category = self.determine_category(file_path)
        lines = content.splitlines()

        title = file_path.stem.replace("-", " ").replace("_", " ").title()
        source = ""
        date = ""
        author = ""

        for line in lines[:10]:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        for line in lines[:15]:
            if "Source:" in line or "**Source:**" in line or "_Source:" in line:
                source = re.sub(r"[\*_`]", "", line).replace("Source:", "").strip()
            if "Date:" in line or "**Date:**" in line:
                date = re.sub(r"[\*_`]", "", line).replace("Date:", "").strip()
            if "Author:" in line or "**Author:**" in line or "By:" in line:
                author = re.sub(r"[\*_`]", "", line).replace("Author:", "").replace("By:", "").strip()

        # Infer topics
        text = (title + " " + content[:2000]).lower()
        topic_kws = self.taxonomy.topic_keywords()
        topics = [t for t, kws in topic_kws.items() if any(kw in text for kw in kws)]
        if not topics:
            topics.append(category.capitalize())

        # Extract summary
        summary_lines = []
        for line in lines:
            line_s = line.strip()
            if (line_s and not line_s.startswith("#") and not line_s.startswith("*") 
                and not line_s.startswith("-") and not line_s.startswith("_") 
                and not line_s.startswith("|") and not line_s.startswith("---") 
                and not line_s.startswith("<")):
                summary_lines.append(line_s)
                if len(summary_lines) >= 2:
                    break

        summary = " ".join(summary_lines)[:300] if summary_lines else f"Document detailing {title}."
        summary = re.sub(r'\s+', ' ', summary).replace('"', "'").strip()

        return {
            "title": title,
            "category": category,
            "topics": topics[:5],
            "source": source or "Knowledge Base",
            "author": author or "Endurance Research",
            "date": date or "2025-01-01",
            "summary": summary
        }

    def standardize_file(self, file_path: Path, force: bool = False) -> bool:
        fm, body = self.parse_document(file_path)
        if fm and not force:
            return False

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        new_fm = self.infer_metadata(content, file_path)
        fm_yaml = yaml.dump(new_fm, sort_keys=False, allow_unicode=True).strip()
        new_content = f"---\n{fm_yaml}\n---\n\n" + (body if fm else content)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return True
