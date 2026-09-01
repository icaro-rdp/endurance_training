"""
Validator and Sitemap Builder sub-module.
"""

import re
from pathlib import Path
from typing import Any, TypedDict

from .errors import InvalidKnowledgeSourceError, KnowledgeSourceNotFoundError
from .frontmatter import FrontmatterManager, parse_frontmatter
from .taxonomy import TaxonomyRegistry
from .walker import iter_kb_documents

REQUIRED_FM_KEYS = ["title", "category", "topics", "summary"]


class ValidationReport(TypedDict):
    total_docs: int
    errors: list[str]
    warnings: list[str]
    is_healthy: bool


class KBValidator:
    def __init__(self, kb_dir: Path, index_file: Path, taxonomy: TaxonomyRegistry):
        self.kb_dir = kb_dir
        self.index_file = index_file
        self.taxonomy = taxonomy
        self.fm_manager = FrontmatterManager(kb_dir, taxonomy)

    def build_sitemap(self) -> str:
        docs: list[dict[str, Any]] = []
        for file_path in iter_kb_documents(self.kb_dir):
            fm, _ = self.fm_manager.parse_document(file_path)
            if fm:
                fm["file_path"] = file_path
                fm["rel_path"] = str(file_path.relative_to(self.kb_dir))
                docs.append(fm)

        categories: dict[str, list[dict[str, Any]]] = {}
        for doc in docs:
            cat = doc.get("category", "general")
            categories.setdefault(cat, []).append(doc)

        lines = [
            "# Master Knowledge Base Index",
            "",
            "Welcome to the **Endurance Training Knowledge Base**. This document "
            "is the primary sitemap for LLMs and researchers.",
            "",
            "---",
            "",
            "## Quick Links",
            "- 📖 [Taxonomy & Definitions](TAXONOMY.md)",
            "",
            "---",
            "",
            "## Document Catalog by Category",
            "",
        ]

        cat_order = self.taxonomy.category_order()
        sorted_cats = sorted(
            categories.keys(),
            key=lambda c: cat_order.index(c) if c in cat_order else 99,
        )

        for cat in sorted_cats:
            cat_docs = categories[cat]
            lines.append(f"### Category: `{cat.upper()}`")
            lines.append(f"Total documents: {len(cat_docs)}")
            lines.append("")

            for doc in sorted(cat_docs, key=lambda d: d.get("title", "")):
                rel = doc["rel_path"]
                title = doc.get("title", doc["rel_path"])
                topics = ", ".join(doc.get("topics", []))
                summary = doc.get("summary", "")
                link_target = f"<{rel}>" if " " in rel else rel

                lines.append(f"- **[{title}]({link_target})** (`{rel}`)")
                if topics:
                    lines.append(f"  - **Topics**: {topics}")
                if summary:
                    lines.append(f"  - **Summary**: {summary}")
                lines.append("")

            lines.append("---")
            lines.append("")

        sitemap_content = "\n".join(lines)
        try:
            if (
                not self.index_file.exists()
                or self.index_file.read_text(encoding="utf-8") != sitemap_content
            ):
                self.index_file.write_text(sitemap_content, encoding="utf-8")
            self.taxonomy.generate_taxonomy_markdown(self.kb_dir)
        except OSError as error:
            raise InvalidKnowledgeSourceError(
                "INDEX.md", f"sitemap could not be written: {error}"
            ) from error

        return sitemap_content

    def validate_health(self, source_rel_path: str | None = None) -> ValidationReport:
        errors: list[str] = []
        warnings: list[str] = []
        documents = tuple(iter_kb_documents(self.kb_dir))
        if source_rel_path is not None:
            by_relative_path = {
                path.relative_to(self.kb_dir).as_posix(): path for path in documents
            }
            try:
                documents = (by_relative_path[source_rel_path],)
            except KeyError as error:
                raise KnowledgeSourceNotFoundError(source_rel_path) from error

        total_docs = len(documents)

        index_text = (
            self.index_file.read_text(encoding="utf-8")
            if self.index_file.exists()
            else ""
        )

        valid_categories = self.taxonomy.categories()
        valid_topics = set(self.taxonomy.topics())

        for file_path in documents:
            rel_path = file_path.relative_to(self.kb_dir)

            try:
                content = self.fm_manager.read_source(file_path)
                parsed = parse_frontmatter(content, rel_path.as_posix())
            except InvalidKnowledgeSourceError as error:
                errors.append(str(error))
                continue
            if not parsed.has_frontmatter:
                errors.append(f"[{rel_path}] Missing YAML frontmatter header ('---').")
                continue
            fm, body = parsed.metadata, parsed.body

            for key in REQUIRED_FM_KEYS:
                if key not in fm or not fm[key]:
                    errors.append(
                        f"[{rel_path}] Missing required frontmatter key '{key}'."
                    )

            language = fm.get("language")
            if language is not None and (
                not isinstance(language, str)
                or language.strip().casefold() not in {"en", "english"}
            ):
                errors.append(f"[{rel_path}] Language must be the English value 'en'.")

            category = fm.get("category")
            if category and (
                not isinstance(category, str) or category not in valid_categories
            ):
                warnings.append(
                    f"[{rel_path}] Category '{category}' is not in the "
                    "predefined taxonomy list."
                )

            topics = fm.get("topics")
            if topics and not isinstance(topics, list):
                warnings.append(
                    f"[{rel_path}] Topics must be a YAML list of canonical values."
                )
            elif isinstance(topics, list):
                for topic in topics:
                    if not isinstance(topic, str) or topic not in valid_topics:
                        warnings.append(
                            f"[{rel_path}] Topic '{topic}' is not in the canonical "
                            "taxonomy list."
                        )

            if (
                str(rel_path) not in index_text
                and str(file_path.name) not in index_text
            ):
                warnings.append(f"[{rel_path}] File not indexed in INDEX.md.")

            link_pattern = re.compile(r"\[.*?\]\((?!http|file)(.*?)\)")
            for match in link_pattern.finditer(body):
                link_target = match.group(1).split("#")[0]
                if link_target:
                    resolved_path = (file_path.parent / link_target).resolve()
                    if not resolved_path.exists():
                        warnings.append(
                            f"[{rel_path}] Broken relative link: '{link_target}'"
                        )

        if total_docs == 0:
            errors.append("The Knowledge Base contains no curated Markdown sources.")

        return {
            "total_docs": total_docs,
            "errors": errors,
            "warnings": warnings,
            "is_healthy": len(errors) == 0,
        }
