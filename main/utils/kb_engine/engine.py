"""
Unified Deep Facade Class: KBEngine
"""

from collections.abc import Sequence
from pathlib import Path

from .frontmatter import FrontmatterManager
from .fts import PassageIndex
from .models import (
    EvidencePassage,
    EvidenceSearchResult,
    IndexStatus,
)
from .taxonomy import TaxonomyRegistry
from .validator import KBValidator, ValidationReport
from .walker import iter_kb_documents

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_KB_DIR = PROJECT_ROOT / "Knowledge_base"


class KBEngine:
    def __init__(
        self,
        kb_dir: Path = DEFAULT_KB_DIR,
        db_path: Path | None = None,
        index_file: Path | None = None,
    ) -> None:
        self.kb_dir = Path(kb_dir).resolve()
        default_db_path = self.kb_dir.parent / "main" / ".kb_index.sqlite"
        self.db_path = Path(db_path or default_db_path).resolve()
        self.index_file = Path(index_file or self.kb_dir / "INDEX.md").resolve()

        self.taxonomy = TaxonomyRegistry(self.kb_dir)
        self.frontmatter = FrontmatterManager(self.kb_dir, self.taxonomy)
        self.index = PassageIndex(self.kb_dir, self.db_path)
        self.validator = KBValidator(self.kb_dir, self.index_file, self.taxonomy)

    def search(
        self,
        query: str,
        category: str | None = None,
        topic: str | None = None,
        source_slug: str | None = None,
        top_k: int = 5,
    ) -> tuple[EvidenceSearchResult, ...]:
        return self.index.search(
            query=query,
            category=category,
            topic=topic,
            source_slug=source_slug,
            limit=top_k,
        )

    def format_llm_context(self, results: Sequence[EvidenceSearchResult]) -> str:
        if not results:
            return "No relevant Knowledge Base entries found."

        output = [f"=== Knowledge Base Context ({len(results)} relevant entries) ===\n"]
        for index, result in enumerate(results, 1):
            passage = result.passage
            locator = f"{passage.rel_path}#L{passage.start_line}-L{passage.end_line}"
            output.append(f"[{index}] {passage.title} ({passage.category.upper()})")
            output.append(f"Source Link: [{locator}]({passage.citation})")
            output.append(f"Section: {passage.section_path}")
            if passage.topics:
                output.append(f"Topics: {', '.join(passage.topics)}")
            output.append("Excerpt:")
            output.append(passage.content)
            output.append("-" * 50)

        return "\n".join(output)

    def build_index(self) -> IndexStatus:
        return self.index.synchronize()

    def get_passage(self, chunk_id: str) -> EvidencePassage | None:
        return self.index.get_passage(chunk_id)

    def get_kb_status(self) -> IndexStatus:
        return self.index.status()

    def build_sitemap(self) -> str:
        return self.validator.build_sitemap()

    def validate(self) -> ValidationReport:
        return self.validator.validate_health()

    def standardize(self, force: bool = False) -> int:
        count = 0
        for file_path in iter_kb_documents(self.kb_dir):
            if self.frontmatter.standardize_file(file_path, force=force):
                count += 1
        return count
