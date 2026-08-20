"""
Unified Deep Facade Class: KBEngine
"""

import os
from collections.abc import Sequence
from pathlib import Path

from .errors import (
    InvalidKnowledgeBaseError,
    InvalidKnowledgeSourceError,
    KnowledgeBaseNotFoundError,
)
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
        kb_dir: Path | None = None,
        db_path: Path | None = None,
        index_file: Path | None = None,
    ) -> None:
        self.kb_dir = _resolve_kb_dir(kb_dir)
        default_db_path = self.kb_dir.parent / "main" / ".kb_index.sqlite"
        configured_index_file = Path(index_file or self.kb_dir / "INDEX.md")
        if configured_index_file.is_symlink():
            raise InvalidKnowledgeSourceError(
                "INDEX.md", "symbolic-link sitemap paths are not allowed"
            )
        self.index_file = configured_index_file.resolve()
        if self.index_file != self.kb_dir / "INDEX.md":
            raise InvalidKnowledgeSourceError(
                "INDEX.md", "the sitemap must be stored at Knowledge_base/INDEX.md"
            )

        self.taxonomy = TaxonomyRegistry(self.kb_dir)
        self.frontmatter = FrontmatterManager(self.kb_dir, self.taxonomy)
        self.index = PassageIndex(self.kb_dir, Path(db_path or default_db_path))
        self.db_path = self.index.db_path
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

    def validate(self, source_rel_path: str | None = None) -> ValidationReport:
        return self.validator.validate_health(source_rel_path=source_rel_path)

    def standardize(self) -> int:
        count = 0
        for file_path in iter_kb_documents(self.kb_dir):
            if self.frontmatter.standardize_file(file_path):
                count += 1
        return count


def _resolve_kb_dir(configured: Path | None) -> Path:
    if configured is not None:
        candidate = Path(configured).expanduser().resolve()
    else:
        environment_path = os.environ.get("ENDURANCE_KB_DIR", "").strip()
        working_tree_candidate = Path.cwd() / "Knowledge_base"
        if environment_path:
            candidate = Path(environment_path).expanduser().resolve()
        elif working_tree_candidate.is_dir():
            candidate = working_tree_candidate.resolve()
        else:
            candidate = DEFAULT_KB_DIR.resolve()

    if not candidate.is_dir():
        raise KnowledgeBaseNotFoundError(candidate)
    if not (candidate / "TAXONOMY.md").is_file():
        raise InvalidKnowledgeBaseError(candidate)
    return candidate
