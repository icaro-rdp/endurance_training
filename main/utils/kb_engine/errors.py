"""Domain errors exposed by the Knowledge Base facade."""


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


class InvalidSearchError(KBEngineError):
    """Raised when a retrieval request violates the public query contract."""

    code = "invalid_search"

    def __init__(self, message: str) -> None:
        super().__init__(message)


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
