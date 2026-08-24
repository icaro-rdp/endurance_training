"""
Knowledge Base Deep Engine Package
"""

from .engine import KBEngine
from .errors import (
    CorpusChangedDuringSyncError,
    EmptyCorpusError,
    IndexNotBuiltError,
    InvalidIndexError,
    InvalidIndexPathError,
    InvalidKnowledgeBaseError,
    InvalidKnowledgeSourceError,
    InvalidSearchError,
    KBEngineError,
    KnowledgeBaseNotFoundError,
    KnowledgeSourceNotFoundError,
    StaleIndexError,
    UnsupportedLanguageError,
)
from .models import (
    EvidencePassage,
    EvidenceSearchResult,
    IndexBuildMetrics,
    IndexStatus,
)
from .taxonomy import TaxonomyRegistry

__all__ = [
    "CorpusChangedDuringSyncError",
    "EmptyCorpusError",
    "EvidencePassage",
    "EvidenceSearchResult",
    "IndexNotBuiltError",
    "IndexBuildMetrics",
    "IndexStatus",
    "InvalidIndexError",
    "InvalidIndexPathError",
    "InvalidKnowledgeBaseError",
    "InvalidKnowledgeSourceError",
    "InvalidSearchError",
    "KBEngine",
    "KBEngineError",
    "KnowledgeBaseNotFoundError",
    "KnowledgeSourceNotFoundError",
    "StaleIndexError",
    "TaxonomyRegistry",
    "UnsupportedLanguageError",
]
