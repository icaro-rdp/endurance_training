"""
Unified Deep Facade Class: KBEngine
"""

import os
from collections.abc import Sequence
from pathlib import Path

from main.utils.kb_engine.classifier import (
    DocumentTaggingResult,
    LocalLLMClassifier,
    MLXAdapter,
    ModelAdapter,
)
from main.utils.kb_engine.errors import (
    InvalidKnowledgeBaseError,
    InvalidKnowledgeSourceError,
    KnowledgeBaseNotFoundError,
)
from main.utils.kb_engine.frontmatter import KnowledgeSource
from main.utils.kb_engine.fts import PassageIndex
from main.utils.kb_engine.hybrid import (
    DEFAULT_EVIDENCE_SELECTION_POLICY,
    reciprocal_rank_fusion,
    select_relevant_passages,
)
from main.utils.kb_engine.models import (
    EvidencePassage,
    EvidenceSearchResult,
    IndexBuildMetrics,
    IndexStatus,
)
from main.utils.kb_engine.taxonomy import TaxonomyRegistry
from main.utils.kb_engine.validator import KBValidator, ValidationReport
from main.utils.kb_engine.walker import iter_kb_documents

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_KB_DIR = PROJECT_ROOT / "Knowledge_base"


class KBEngine:
    """Facade for retrieval, validation, and Knowledge Source classification."""

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
        self.index = PassageIndex(self.kb_dir, Path(db_path or default_db_path))
        self.db_path = self.index.db_path
        self.validator = KBValidator(self.kb_dir, self.index_file, self.taxonomy)

    def search(
        self,
        query: str,
        category: str | None = None,
        topic: str | None = None,
        source_slug: str | None = None,
        top_k: int = DEFAULT_EVIDENCE_SELECTION_POLICY.maximum_passages,
    ) -> tuple[EvidenceSearchResult, ...]:
        """Search for relevant Evidence Passages."""
        return self.index.search(
            query=query,
            category=category,
            topic=topic,
            source_slug=source_slug,
            limit=top_k,
        )

    def multi_search(
        self,
        queries: Sequence[str],
        category: str | None = None,
        topic: str | None = None,
        source_slug: str | None = None,
        top_k: int = DEFAULT_EVIDENCE_SELECTION_POLICY.maximum_passages,
    ) -> tuple[EvidenceSearchResult, ...]:
        """Fuse Evidence Passages retrieved for multiple query intents."""
        ranking_lists = []
        for q in queries:
            clean_q = q.strip()
            if clean_q:
                res = self._search_hybrid_candidates(
                    clean_q,
                    category=category,
                    topic=topic,
                    source_slug=source_slug,
                )
                if res:
                    ranking_lists.append(res)

        if not ranking_lists:
            return ()
        fused = reciprocal_rank_fusion(
            ranking_lists,
            k=60,
            limit=DEFAULT_EVIDENCE_SELECTION_POLICY.candidate_limit,
        )
        retained = select_relevant_passages(fused)
        return retained[
            : min(top_k, DEFAULT_EVIDENCE_SELECTION_POLICY.maximum_passages)
        ]

    def _search_hybrid_candidates(
        self,
        query: str,
        category: str | None = None,
        topic: str | None = None,
        source_slug: str | None = None,
    ) -> tuple[EvidenceSearchResult, ...]:
        """Retrieve the bounded hybrid pool before final multi-query selection."""
        return self.index.search(
            query=query,
            category=category,
            topic=topic,
            source_slug=source_slug,
            limit=DEFAULT_EVIDENCE_SELECTION_POLICY.candidate_limit,
            retain_evidence=False,
        )

    def format_llm_context(self, results: Sequence[EvidenceSearchResult]) -> str:
        """Format retrieved evidence for grounded synthesis by an LLM."""
        if not results:
            return "insufficient_evidence: No relevant Knowledge Base entries found."

        output = [
            f"=== Knowledge Base Context ({len(results)} relevant entries) ===",
            "Instruction: Always report and cite the sources in the final output.\n",
        ]
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
        """Synchronize the Derived Index with current Knowledge Sources."""
        return self.index.synchronize()

    @property
    def last_index_build_metrics(self) -> IndexBuildMetrics | None:
        """Return metrics from the latest index synchronization."""
        return self.index.last_build_metrics

    def get_passage(self, chunk_id: str) -> EvidencePassage | None:
        """Return one Evidence Passage by stable identifier."""
        return self.index.get_passage(chunk_id)

    def get_kb_status(self) -> IndexStatus:
        """Return Derived Index freshness status."""
        return self.index.status()

    def build_sitemap(self) -> str:
        """Rebuild the Knowledge Base sitemap."""
        return self.validator.build_sitemap()

    def validate(self, source_rel_path: str | None = None) -> ValidationReport:
        """Validate the Knowledge Base or one exact source."""
        return self.validator.validate_health(source_rel_path=source_rel_path)

    def get_knowledge_source(self, file_path: Path | str) -> KnowledgeSource:
        """Load a single KnowledgeSource with domain invariant enforcement."""
        return KnowledgeSource.from_path(
            file_path=Path(file_path),
            kb_dir=self.kb_dir,
            taxonomy=self.taxonomy,
        )

    def classify_content(
        self,
        content: str,
        title: str | None = None,
        adapter: ModelAdapter | None = None,
    ) -> DocumentTaggingResult:
        """Classify markdown content string directly."""
        return self._classifier(adapter).classify_content(content, title=title)

    def classify_document(
        self,
        file_path: Path | str,
        adapter: ModelAdapter | None = None,
    ) -> DocumentTaggingResult:
        """Classify a Knowledge Source document without modifying it."""
        return self._classifier(adapter).classify_document(
            file_path,
            kb_dir=self.kb_dir,
        )

    def apply_tags(
        self,
        file_path: Path | str,
        dry_run: bool = False,
        adapter: ModelAdapter | None = None,
    ) -> DocumentTaggingResult:
        """Classify a document and apply changes to frontmatter unless dry_run."""
        return self._classifier(adapter).apply_tags_to_file(
            file_path, dry_run=dry_run, kb_dir=self.kb_dir
        )

    def apply_tags_all(
        self,
        directory: Path | str | None = None,
        dry_run: bool = False,
        adapter: ModelAdapter | None = None,
    ) -> list[tuple[KnowledgeSource, DocumentTaggingResult]]:
        """Batch classify and optionally apply tags to curated documents."""
        results: list[tuple[KnowledgeSource, DocumentTaggingResult]] = []
        classifier = self._classifier(adapter)

        target_dir = Path(directory) if directory else self.kb_dir
        for doc_path in iter_kb_documents(self.kb_dir):
            if directory:
                try:
                    doc_path.resolve().relative_to(target_dir.resolve())
                except ValueError:
                    continue
            source = self.get_knowledge_source(doc_path)
            res = classifier.classify_source(source)
            if not dry_run:
                source.update_metadata(
                    category=res.category,
                    topics=res.topics,
                    summary=res.summary,
                )
                source.save(dry_run=False)
            results.append((source, res))
        return results

    def tag_sources(
        self,
        path: Path | str | None,
        recursive: bool,
        dry_run: bool,
        adapter: ModelAdapter | None = None,
    ) -> list[tuple[KnowledgeSource, DocumentTaggingResult]]:
        """Classify one source or all sources below a Knowledge Base directory."""
        if recursive:
            directory = self._resolve_tag_directory(path)
            return self.apply_tags_all(
                directory=directory,
                dry_run=dry_run,
                adapter=adapter,
            )
        if path is None:
            raise InvalidKnowledgeSourceError(
                "<missing>",
                "specify a document path or use --all",
            )

        source = self.get_knowledge_source(self._resolve_source_path(path))
        result = self.apply_tags(
            source.file_path or self.kb_dir / source.rel_path,
            dry_run=dry_run,
            adapter=adapter,
        )
        return [(source, result)]

    def _classifier(self, adapter: ModelAdapter | None) -> LocalLLMClassifier:
        return LocalLLMClassifier(
            adapter=adapter or MLXAdapter(),
            taxonomy=self.taxonomy,
            kb_dir=self.kb_dir,
        )

    def _resolve_source_path(self, path: Path | str) -> Path:
        raw_path = Path(path)
        candidate = raw_path if raw_path.is_absolute() else self.kb_dir / raw_path
        if not candidate.is_file():
            raise InvalidKnowledgeSourceError(str(path), "source file does not exist")
        return candidate.resolve()

    def _resolve_tag_directory(self, path: Path | str | None) -> Path | None:
        if path is None:
            return None
        raw_path = Path(path)
        candidate = raw_path if raw_path.is_absolute() else self.kb_dir / raw_path
        if not candidate.is_dir():
            raise InvalidKnowledgeSourceError(
                str(path),
                "--all requires a Knowledge Base directory",
            )
        resolved = candidate.resolve()
        try:
            resolved.relative_to(self.kb_dir)
        except ValueError as error:
            raise InvalidKnowledgeSourceError(
                str(path),
                "directory resolves outside Knowledge_base",
            ) from error
        return resolved


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
