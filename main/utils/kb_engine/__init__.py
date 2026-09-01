"""
Knowledge Base Deep Engine Package
"""

from .classifier import (
    DEFAULT_LOCAL_MODEL,
    DocumentTaggingResult,
    FakeModelAdapter,
    LocalLLMClassifier,
    MLXAdapter,
    ModelAdapter,
    OllamaAdapter,
    TopicTagger,
    apply_tags_to_file,
    classify_content,
    classify_document,
)
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
    InvalidTaxonomyError,
    KBEngineError,
    KnowledgeBaseNotFoundError,
    KnowledgeSourceNotFoundError,
    MissingDependencyError,
    ModelConnectionError,
    ModelInferenceError,
    StaleIndexError,
    UnsupportedLanguageError,
)
from .frontmatter import KnowledgeSource
from .models import (
    EvidencePassage,
    EvidenceSearchResult,
    IndexBuildMetrics,
    IndexStatus,
)
from .taxonomy import TaxonomyRegistry

__all__ = [
    "CorpusChangedDuringSyncError",
    "DEFAULT_LOCAL_MODEL",
    "DocumentTaggingResult",
    "EmptyCorpusError",
    "EvidencePassage",
    "EvidenceSearchResult",
    "FakeModelAdapter",
    "IndexNotBuiltError",
    "IndexBuildMetrics",
    "IndexStatus",
    "InvalidIndexError",
    "InvalidIndexPathError",
    "InvalidKnowledgeBaseError",
    "InvalidKnowledgeSourceError",
    "InvalidSearchError",
    "InvalidTaxonomyError",
    "KBEngine",
    "KBEngineError",
    "KnowledgeBaseNotFoundError",
    "KnowledgeSource",
    "KnowledgeSourceNotFoundError",
    "LocalLLMClassifier",
    "MLXAdapter",
    "MissingDependencyError",
    "ModelAdapter",
    "ModelConnectionError",
    "ModelInferenceError",
    "OllamaAdapter",
    "StaleIndexError",
    "TaxonomyRegistry",
    "TopicTagger",
    "UnsupportedLanguageError",
    "apply_tags_to_file",
    "classify_content",
    "classify_document",
]
