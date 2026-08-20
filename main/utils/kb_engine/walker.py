import os
from collections.abc import Iterator
from pathlib import Path


def iter_kb_documents(kb_dir: Path, exclude: set[str] | None = None) -> Iterator[Path]:
    """Yield all curated KB document paths, excluding meta-files and raw transcripts."""
    if exclude is None:
        exclude = {"INDEX.md", "TAXONOMY.md"}
    for root, dirs, files in os.walk(kb_dir):
        # Exclude raw_transcripts and hidden directories from curated index walk
        dirs[:] = sorted(
            d
            for d in dirs
            if d not in {"raw_transcripts", "_summary"} and not d.startswith(".")
        )
        for file in sorted(files):
            if file.endswith(".md") and file not in exclude:
                yield Path(root) / file
