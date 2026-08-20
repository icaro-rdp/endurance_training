"""Domain models for citation-stable Knowledge Base retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PassageSizeStatus(str, Enum):
    """Whether a passage satisfies the configured chunk-size policy."""

    WITHIN_POLICY = "within_policy"
    UNDERSIZED_SECTION = "undersized_section"
    OVERSIZED_ATOMIC_BLOCK = "oversized_atomic_block"


class IndexState(str, Enum):
    """Freshness state of the local Derived Index."""

    MISSING = "missing"
    FRESH = "fresh"
    STALE = "stale"
    INVALID = "invalid"


@dataclass(frozen=True, slots=True)
class ChunkingPolicy:
    """Word-count targets used when assembling Evidence Passages."""

    target_words: int = 350
    min_words: int = 80
    max_words: int = 600

    def __post_init__(self) -> None:
        if not 1 <= self.min_words <= self.target_words <= self.max_words:
            raise ValueError(
                "ChunkingPolicy requires 1 <= min_words <= target_words <= max_words"
            )


@dataclass(frozen=True, slots=True)
class EvidencePassage:
    """A bounded, attributable excerpt from one Knowledge Source."""

    chunk_id: str
    source_slug: str
    rel_path: str
    title: str
    author: str
    language: str
    source_type: str
    category: str
    topics: tuple[str, ...]
    source: str
    section_hierarchy: tuple[str, ...]
    start_line: int
    end_line: int
    content: str
    word_count: int
    char_count: int
    citation: str
    size_status: PassageSizeStatus

    @property
    def section_path(self) -> str:
        return " > ".join(self.section_hierarchy)

    def to_dict(self) -> dict[str, object]:
        return {
            "chunk_id": self.chunk_id,
            "source_slug": self.source_slug,
            "rel_path": self.rel_path,
            "title": self.title,
            "author": self.author,
            "language": self.language,
            "source_type": self.source_type,
            "category": self.category,
            "topics": list(self.topics),
            "source": self.source,
            "section_hierarchy": list(self.section_hierarchy),
            "section_path": self.section_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "content": self.content,
            "word_count": self.word_count,
            "char_count": self.char_count,
            "citation": self.citation,
            "size_status": self.size_status.value,
        }


@dataclass(frozen=True, slots=True)
class EvidenceSearchResult:
    """An Evidence Passage plus its lexical retrieval score."""

    passage: EvidencePassage
    lexical_score: float

    def to_dict(self) -> dict[str, object]:
        result = self.passage.to_dict()
        result["lexical_score"] = self.lexical_score
        return result


@dataclass(frozen=True, slots=True)
class CorpusManifest:
    """Deterministic identity of the current curated corpus."""

    digest: str
    document_count: int
    source_paths: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class IndexStatus:
    """Inspectable state of the local passage index."""

    state: IndexState
    document_count: int
    passage_count: int
    current_digest: str
    indexed_digest: str | None

    @property
    def is_fresh(self) -> bool:
        return self.state is IndexState.FRESH

    def to_dict(self) -> dict[str, object]:
        return {
            "state": self.state.value,
            "document_count": self.document_count,
            "passage_count": self.passage_count,
            "current_digest": self.current_digest,
            "indexed_digest": self.indexed_digest,
            "is_fresh": self.is_fresh,
        }
