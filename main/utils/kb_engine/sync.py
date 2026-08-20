"""Deterministic corpus manifests for explicit Corpus Synchronization."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path

from .errors import CorpusChangedDuringSyncError, InvalidKnowledgeSourceError
from .models import CorpusManifest
from .walker import iter_kb_documents


def build_corpus_manifest(kb_dir: Path) -> CorpusManifest:
    """Hash curated sources and taxonomy, excluding every Derived Index."""

    root = kb_dir.resolve()
    if not root.is_dir() or not (root / "TAXONOMY.md").is_file():
        raise CorpusChangedDuringSyncError
    document_paths = sorted(iter_kb_documents(root), key=_relative_path(root))
    taxonomy_path = root / "TAXONOMY.md"
    hashed_paths = [*document_paths, taxonomy_path]

    digest = hashlib.sha256()
    document_path_set = set(document_paths)
    source_digests: list[tuple[str, str]] = []
    for path in sorted(hashed_paths, key=_relative_path(root)):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise InvalidKnowledgeSourceError(
                relative, "symbolic-link sources are not allowed"
            )
        try:
            source_bytes = path.read_bytes()
        except FileNotFoundError as error:
            raise CorpusChangedDuringSyncError from error
        except OSError as error:
            raise InvalidKnowledgeSourceError(
                relative, f"source could not be read: {error}"
            ) from error
        file_digest = hashlib.sha256(source_bytes)
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_digest.digest())
        digest.update(b"\0")
        if path in document_path_set:
            source_digests.append((relative, file_digest.hexdigest()))

    return CorpusManifest(
        digest=digest.hexdigest(),
        source_digests=tuple(source_digests),
    )


def _relative_path(root: Path) -> Callable[[Path], str]:
    return lambda path: path.relative_to(root).as_posix()
