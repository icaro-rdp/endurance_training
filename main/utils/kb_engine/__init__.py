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
    KnowledgeBaseNotFoundError,
    KnowledgeSourceNotFoundError,
    StaleIndexError,
    UnsupportedLanguageError,
)
from .models import EvidencePassage, EvidenceSearchResult, IndexStatus
from .taxonomy import TaxonomyRegistry

__all__ = [
    "CorpusChangedDuringSyncError",
    "EmptyCorpusError",
    "EvidencePassage",
    "EvidenceSearchResult",
    "IndexNotBuiltError",
    "IndexStatus",
    "InvalidIndexError",
    "InvalidIndexPathError",
    "InvalidKnowledgeBaseError",
    "InvalidKnowledgeSourceError",
    "InvalidSearchError",
    "KBEngine",
    "KnowledgeBaseNotFoundError",
    "KnowledgeSourceNotFoundError",
    "StaleIndexError",
    "TaxonomyRegistry",
    "UnsupportedLanguageError",
]
