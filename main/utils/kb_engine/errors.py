"""Domain errors exposed by the Knowledge Base facade."""

from pathlib import Path


class KBEngineError(RuntimeError):
    """Base class for expected Knowledge Base failures."""

    code = "kb_error"


class IndexNotBuiltError(KBEngineError):
    """Raised when retrieval is attempted before Corpus Synchronization."""

    code = "missing_index"

    def __init__(self) -> None:
        super().__init__(
            "The Knowledge Base index is missing. Run `endurance-kb build-index`."
        )


class StaleIndexError(KBEngineError):
    """Raised when Knowledge Sources differ from the indexed corpus."""

    code = "stale_index"

    def __init__(self) -> None:
        super().__init__(
            "The Knowledge Base index is stale. Run `endurance-kb build-index`."
        )


class InvalidIndexError(KBEngineError):
    """Raised when the Derived Index exists but cannot be read safely."""

    code = "invalid_index"

    def __init__(self) -> None:
        super().__init__(
            "The Knowledge Base index is invalid. Run `endurance-kb build-index`."
        )


class InvalidIndexPathError(KBEngineError):
    """Raised when a Derived Index path could overwrite non-index data."""

    code = "invalid_index_path"

    def __init__(self, path: Path, detail: str) -> None:
        super().__init__(f"Derived Index path `{path}` is unsafe: {detail}")


class InvalidSearchError(KBEngineError):
    """Raised when a retrieval request violates the public query contract."""

    code = "invalid_search"

    def __init__(self, message: str) -> None:
        super().__init__(message)


class KnowledgeBaseNotFoundError(KBEngineError):
    """Raised when the configured Knowledge Base directory does not exist."""

    code = "knowledge_base_not_found"

    def __init__(self, path: Path) -> None:
        super().__init__(
            f"Knowledge Base directory not found: `{path}`. Run from the repository "
            "root, pass `--kb-dir`, or set `ENDURANCE_KB_DIR`."
        )


class InvalidKnowledgeBaseError(KBEngineError):
    """Raised when a directory is not a canonical Knowledge Base root."""

    code = "invalid_knowledge_base"

    def __init__(self, path: Path) -> None:
        super().__init__(
            f"Knowledge Base directory `{path}` has no TAXONOMY.md; select the "
            "canonical Knowledge_base root."
        )


class KnowledgeSourceNotFoundError(KBEngineError):
    """Raised when a requested relative Knowledge Source is not curated."""

    code = "source_not_found"

    def __init__(self, rel_path: str) -> None:
        super().__init__(
            f"Knowledge Source not found in the curated corpus: `{rel_path}`."
        )


class InvalidKnowledgeSourceError(KBEngineError):
    """Raised when a Knowledge Source cannot satisfy the ingestion contract."""

    code = "invalid_source"

    def __init__(self, rel_path: str, detail: str) -> None:
        super().__init__(f"Knowledge Source `{rel_path}` is invalid: {detail}")


class EmptyCorpusError(KBEngineError):
    """Raised when synchronization is attempted without curated sources."""

    code = "empty_corpus"

    def __init__(self) -> None:
        super().__init__("The Knowledge Base contains no curated Markdown sources.")


class CorpusChangedDuringSyncError(KBEngineError):
    """Raised when Knowledge Sources change during synchronization."""

    code = "corpus_changed_during_sync"

    def __init__(self) -> None:
        super().__init__(
            "Knowledge Sources changed during synchronization; run "
            "`endurance-kb build-index` again."
        )


class UnsupportedLanguageError(KBEngineError):
    """Raised when a non-English Knowledge Source enters the corpus."""

    code = "unsupported_language"

    def __init__(self, rel_path: str, language: str) -> None:
        super().__init__(
            f"Knowledge Source `{rel_path}` declares unsupported "
            f"language `{language}`; "
            "this Knowledge Base accepts English sources only."
        )


class ModelInferenceError(KBEngineError):
    """Raised when local AI model inference or output parsing fails."""

    code = "model_inference_error"

    def __init__(self, detail: str) -> None:
        super().__init__(detail)


class MissingDependencyError(KBEngineError):
    """Raised when an optional dependency required for inference is not installed."""

    code = "missing_dependency"

    def __init__(self, package: str, detail: str) -> None:
        super().__init__(f"Missing required dependency '{package}': {detail}")


class ModelConnectionError(KBEngineError):
    """Raised when communication with a local model backend daemon fails."""

    code = "model_connection_error"

    def __init__(self, host: str, detail: str) -> None:
        super().__init__(f"Failed to connect to model service at {host}: {detail}")


class InvalidTaxonomyError(KBEngineError):
    """Raised when a category or topic violates canonical taxonomy rules."""

    code = "invalid_taxonomy"

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
