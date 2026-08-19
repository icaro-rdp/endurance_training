import os
from pathlib import Path
from typing import Iterator, Set, Optional

def iter_kb_documents(kb_dir: Path, exclude: Optional[Set[str]] = None) -> Iterator[Path]:
    """Yield all curated KB document paths, excluding meta-files and raw transcripts."""
    if exclude is None:
        exclude = {"INDEX.md", "TAXONOMY.md"}
    for root, dirs, files in os.walk(kb_dir):
        # Exclude raw_transcripts and hidden directories from curated index walk
        dirs[:] = [d for d in dirs if d != "raw_transcripts" and not d.startswith(".")]
        for file in sorted(files):
            if file.endswith(".md") and file not in exclude:
                yield Path(root) / file
