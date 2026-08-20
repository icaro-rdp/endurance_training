"""
Knowledge Base Deep Engine Package
"""

from .engine import KBEngine
from .errors import (
    CorpusChangedDuringSyncError,
    IndexNotBuiltError,
    InvalidIndexError,
    InvalidSearchError,
    StaleIndexError,
    UnsupportedLanguageError,
)
from .models import EvidencePassage, EvidenceSearchResult, IndexStatus
from .taxonomy import TaxonomyRegistry

__all__ = [
    "CorpusChangedDuringSyncError",
    "EvidencePassage",
    "EvidenceSearchResult",
    "IndexNotBuiltError",
    "IndexStatus",
    "InvalidIndexError",
    "InvalidSearchError",
    "KBEngine",
    "StaleIndexError",
    "TaxonomyRegistry",
    "UnsupportedLanguageError",
]
