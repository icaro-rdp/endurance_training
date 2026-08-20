"""Deterministic corpus manifests for explicit Corpus Synchronization."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path

from .models import CorpusManifest
from .walker import iter_kb_documents


def build_corpus_manifest(kb_dir: Path) -> CorpusManifest:
    """Hash curated sources and taxonomy, excluding every Derived Index."""

    root = kb_dir.resolve()
    document_paths = sorted(iter_kb_documents(root), key=_relative_path(root))
    hashed_paths = [*document_paths]
    taxonomy_path = root / "TAXONOMY.md"
    if taxonomy_path.is_file():
        hashed_paths.append(taxonomy_path)

    digest = hashlib.sha256()
    for path in sorted(hashed_paths, key=_relative_path(root)):
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
        digest.update(b"\0")

    return CorpusManifest(
        digest=digest.hexdigest(),
        document_count=len(document_paths),
        source_paths=tuple(
            path.relative_to(root).as_posix() for path in document_paths
        ),
    )


def _relative_path(root: Path) -> Callable[[Path], str]:
    return lambda path: path.relative_to(root).as_posix()
