import os
from pathlib import Path
from typing import Iterator, Set, Optional

def iter_kb_documents(kb_dir: Path, exclude: Optional[Set[str]] = None) -> Iterator[Path]:
    """Yield all KB document paths, excluding meta-files."""
    if exclude is None:
        exclude = {"INDEX.md", "TAXONOMY.md"}
    for root, _, files in os.walk(kb_dir):
        for file in sorted(files):
            if file.endswith(".md") and file not in exclude:
                yield Path(root) / file
