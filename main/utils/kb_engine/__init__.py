"""
Knowledge Base Deep Engine Package
"""

from .engine import KBEngine
from .errors import (
    IndexNotBuiltError,
    InvalidIndexError,
    InvalidSearchError,
    StaleIndexError,
    UnsupportedLanguageError,
)
from .models import EvidencePassage, EvidenceSearchResult, IndexStatus
from .taxonomy import TaxonomyRegistry

__all__ = [
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
