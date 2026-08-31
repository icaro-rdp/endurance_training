"""
Frontmatter parsing and source management module.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .errors import InvalidKnowledgeSourceError
from .taxonomy import TaxonomyRegistry

_STRING_FIELDS = ("title", "author", "language", "category", "source", "summary")


@dataclass(frozen=True, slots=True)
class ParsedDocument:
    """One consistently parsed Markdown source and its frontmatter boundary."""

    metadata: dict[str, Any]
    body: str
    content_start: int
    has_frontmatter: bool


def parse_frontmatter(content: str, rel_path: str) -> ParsedDocument:
    """Parse and shape-check one optional YAML frontmatter mapping."""

    lines = content.splitlines(keepends=True)
    if not lines or lines[0].rstrip() != "---":
        return ParsedDocument({}, content, 0, False)

    try:
        end = next(
            index for index in range(1, len(lines)) if lines[index].rstrip() == "---"
        )
    except StopIteration as error:
        raise InvalidKnowledgeSourceError(
            rel_path, "YAML frontmatter is not closed with `---`"
        ) from error

    try:
        loaded = yaml.safe_load("".join(lines[1:end]))
    except yaml.YAMLError as error:
        raise InvalidKnowledgeSourceError(
            rel_path, f"YAML syntax error: {error}"
        ) from error
    if loaded is None:
        metadata: dict[str, Any] = {}
    elif not isinstance(loaded, dict):
        raise InvalidKnowledgeSourceError(
            rel_path, "YAML frontmatter must be a mapping"
        )
    elif any(not isinstance(key, str) for key in loaded):
        raise InvalidKnowledgeSourceError(
            rel_path, "YAML frontmatter keys must be strings"
        )
    else:
        metadata = dict(loaded)

    for field in _STRING_FIELDS:
        if field in metadata and not isinstance(metadata[field], str):
            raise InvalidKnowledgeSourceError(
                rel_path, f"frontmatter `{field}` must be a string"
            )
    if "topics" in metadata and (
        not isinstance(metadata["topics"], list)
        or not all(isinstance(topic, str) for topic in metadata["topics"])
    ):
        raise InvalidKnowledgeSourceError(
            rel_path, "frontmatter `topics` must be a list of strings"
        )

    return ParsedDocument(
        metadata=metadata,
        body="".join(lines[end + 1 :]),
        content_start=end + 1,
        has_frontmatter=True,
    )


class FrontmatterManager:
    def __init__(self, kb_dir: Path, taxonomy: TaxonomyRegistry):
        self.kb_dir = kb_dir
        self.taxonomy = taxonomy

    def parse_document(self, file_path: Path) -> tuple[dict[str, Any], str]:
        rel_path = self._relative_path(file_path)
        content = self.read_source(file_path)
        parsed = parse_frontmatter(content, rel_path)
        return parsed.metadata, parsed.body

    def _relative_path(self, file_path: Path) -> str:
        root = self.kb_dir.resolve()
        try:
            lexical_path = file_path.absolute().relative_to(root).as_posix()
        except ValueError:
            lexical_path = file_path.name
        if file_path.is_symlink():
            raise InvalidKnowledgeSourceError(
                lexical_path, "symbolic-link sources are not allowed"
            )
        try:
            file_path.resolve().relative_to(root)
        except ValueError as error:
            raise InvalidKnowledgeSourceError(
                lexical_path, "source resolves outside Knowledge_base"
            ) from error
        return lexical_path

    def read_source(self, file_path: Path) -> str:
        rel_path = self._relative_path(file_path)
        try:
            source_bytes = file_path.read_bytes()
        except OSError as error:
            raise InvalidKnowledgeSourceError(
                rel_path, f"source could not be read: {error}"
            ) from error
        try:
            return source_bytes.decode("utf-8")
        except UnicodeDecodeError as error:
            raise InvalidKnowledgeSourceError(
                rel_path, "source is not valid UTF-8"
            ) from error
