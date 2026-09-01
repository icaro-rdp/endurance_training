"""
Frontmatter parsing and KnowledgeSource domain module.
"""

import contextlib
import os
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from main.utils.kb_engine.errors import (
    InvalidKnowledgeSourceError,
    InvalidTaxonomyError,
)
from main.utils.kb_engine.taxonomy import TaxonomyRegistry

_STRING_FIELDS = ("title", "author", "language", "category", "source", "summary")
_STANDARD_KEY_ORDER = (
    "title",
    "language",
    "category",
    "topics",
    "source",
    "author",
    "date",
    "summary",
    "key_takeaways",
)
# PyYAML yields recursively heterogeneous scalar, sequence, and mapping values.
Frontmatter = dict[str, Any]


@dataclass(frozen=True, slots=True)
class ParsedDocument:
    """One consistently parsed Markdown source and its frontmatter boundary."""

    metadata: Frontmatter
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
        metadata: Frontmatter = {}
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


class KnowledgeSource:
    """
    Deep domain module encapsulating a curated Markdown Knowledge Source.
    Owns frontmatter validation, taxonomy alignment, and atomic updates.
    """

    def __init__(
        self,
        rel_path: str,
        metadata: Frontmatter,
        body: str,
        file_path: Path | None = None,
        taxonomy: TaxonomyRegistry | None = None,
        has_frontmatter: bool = True,
    ) -> None:
        self.rel_path = rel_path
        self.metadata = dict(metadata)
        self.body = body
        self.file_path = file_path
        self.taxonomy = taxonomy
        self.has_frontmatter = has_frontmatter

    @classmethod
    def from_path(
        cls,
        file_path: Path,
        kb_dir: Path,
        taxonomy: TaxonomyRegistry | None = None,
    ) -> "KnowledgeSource":
        """Read and validate a Knowledge Source from disk."""
        rel_path = cls._resolve_relative_path(file_path, kb_dir)
        content = cls._read_file(file_path, rel_path)
        parsed = parse_frontmatter(content, rel_path)
        return cls(
            rel_path=rel_path,
            metadata=parsed.metadata,
            body=parsed.body,
            file_path=file_path,
            taxonomy=taxonomy,
            has_frontmatter=parsed.has_frontmatter,
        )

    @classmethod
    def from_content(
        cls,
        content: str,
        rel_path: str = "unnamed.md",
        taxonomy: TaxonomyRegistry | None = None,
    ) -> "KnowledgeSource":
        """Create a Knowledge Source from an in-memory string."""
        parsed = parse_frontmatter(content, rel_path)
        return cls(
            rel_path=rel_path,
            metadata=parsed.metadata,
            body=parsed.body,
            file_path=None,
            taxonomy=taxonomy,
            has_frontmatter=parsed.has_frontmatter,
        )

    @property
    def title(self) -> str:
        """Return the source title or filename stem."""
        return str(self.metadata.get("title") or Path(self.rel_path).stem)

    @property
    def category(self) -> str:
        """Return the normalized source category."""
        cat = self.metadata.get("category", "")
        if self.taxonomy and cat:
            return self.taxonomy.normalize_category(cat) or cat
        return str(cat)

    @property
    def topics(self) -> list[str]:
        """Return normalized source topics."""
        raw_topics = self.metadata.get("topics") or []
        if not isinstance(raw_topics, list):
            return []
        if self.taxonomy:
            return [
                self.taxonomy.normalize_topic(t) or t
                for t in raw_topics
                if isinstance(t, str)
            ]
        return [str(t) for t in raw_topics]

    @property
    def summary(self) -> str:
        """Return the source summary."""
        return str(self.metadata.get("summary") or "")

    @property
    def language(self) -> str:
        """Return the declared language, defaulting legacy sources to English."""
        return str(self.metadata.get("language") or "en")

    @property
    def author(self) -> str | None:
        """Return the source author when present."""
        val = self.metadata.get("author")
        return str(val) if val is not None else None

    @property
    def source(self) -> str | None:
        """Return the provenance source when present."""
        val = self.metadata.get("source")
        return str(val) if val is not None else None

    @property
    def date(self) -> str | None:
        """Return the publication date when present."""
        val = self.metadata.get("date")
        return str(val) if val is not None else None

    @property
    def key_takeaways(self) -> list[str] | None:
        """Return deliberately curated key takeaways when present."""
        val = self.metadata.get("key_takeaways")
        if isinstance(val, list):
            return [str(item) for item in val]
        return None

    def update_metadata(
        self,
        *,
        category: str | None = None,
        topics: Sequence[str] | None = None,
        summary: str | None = None,
        title: str | None = None,
        key_takeaways: list[str] | None = None,
    ) -> None:
        """Update frontmatter fields with normalization and validation."""
        taxonomy = self._require_taxonomy()
        if category is not None:
            norm_cat = taxonomy.normalize_category(category)
            if not norm_cat or not taxonomy.valid_category(norm_cat):
                raise InvalidTaxonomyError(
                    f"Category '{category}' is not a valid canonical category."
                )
            self.metadata["category"] = norm_cat

        if topics is not None:
            normalized_topics: list[str] = []
            for topic in topics:
                norm_topic = taxonomy.normalize_topic(topic)
                if not norm_topic or norm_topic not in taxonomy.topics():
                    raise InvalidTaxonomyError(
                        f"Topic '{topic}' is not a valid canonical topic."
                    )
                if norm_topic not in normalized_topics:
                    normalized_topics.append(norm_topic)
            self.metadata["topics"] = normalized_topics

        if summary is not None:
            self.metadata["summary"] = summary.strip()

        if title is not None:
            self.metadata["title"] = title.strip()

        if key_takeaways is not None:
            self.metadata["key_takeaways"] = key_takeaways

    def to_markdown(self) -> str:
        """Render frontmatter and Markdown body into canonical string."""
        ordered_meta: Frontmatter = {}
        for key in _STANDARD_KEY_ORDER:
            if key in self.metadata:
                ordered_meta[key] = self.metadata[key]
        for key, value in self.metadata.items():
            if key not in ordered_meta:
                ordered_meta[key] = value

        yaml_dump = yaml.dump(
            ordered_meta,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
        ).strip()

        if self.body.startswith("\n"):
            return f"---\n{yaml_dump}\n---{self.body}"
        return f"---\n{yaml_dump}\n---\n{self.body}"

    def save(
        self,
        target_path: Path | None = None,
        dry_run: bool = False,
    ) -> None:
        """Atomically save the Knowledge Source to disk preserving permissions."""
        self._validate_taxonomy_metadata()
        if dry_run:
            return

        dest = target_path or self.file_path
        if dest is None:
            raise InvalidKnowledgeSourceError(
                self.rel_path, "cannot save KnowledgeSource without a file path"
            )

        content = self.to_markdown()
        dest_dir = dest.parent
        dest_dir.mkdir(parents=True, exist_ok=True)

        original_mode: int | None = None
        if dest.exists():
            original_mode = dest.stat().st_mode

        temp_fd, temp_name = tempfile.mkstemp(
            prefix="ks_atomic_", suffix=".tmp", dir=str(dest_dir)
        )
        try:
            with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                f.write(content)
            if original_mode is not None:
                os.chmod(temp_name, original_mode)
            os.replace(temp_name, str(dest))
        except OSError:
            with contextlib.suppress(OSError):
                Path(temp_name).unlink(missing_ok=True)
            raise

    def _require_taxonomy(self) -> TaxonomyRegistry:
        if self.taxonomy is None:
            raise InvalidTaxonomyError(
                "Knowledge Source persistence requires a taxonomy registry."
            )
        return self.taxonomy

    def _validate_taxonomy_metadata(self) -> None:
        taxonomy = self._require_taxonomy()
        category = self.metadata.get("category")
        if not isinstance(category, str) or category not in taxonomy.categories():
            raise InvalidTaxonomyError(
                f"Category '{category}' is not a valid canonical category."
            )

        topics = self.metadata.get("topics")
        valid_topics = set(taxonomy.topics())
        if not isinstance(topics, list) or any(
            not isinstance(topic, str) or topic not in valid_topics for topic in topics
        ):
            raise InvalidTaxonomyError(
                "Knowledge Source topics must contain only canonical values."
            )

    @staticmethod
    def _resolve_relative_path(file_path: Path, kb_dir: Path) -> str:
        root = kb_dir.resolve()
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

    @staticmethod
    def _read_file(file_path: Path, rel_path: str) -> str:
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


class FrontmatterManager:
    """Compatibility reader backed by the KnowledgeSource domain module."""

    def __init__(self, kb_dir: Path, taxonomy: TaxonomyRegistry) -> None:
        self.kb_dir = kb_dir
        self.taxonomy = taxonomy

    def parse_document(self, file_path: Path) -> tuple[Frontmatter, str]:
        """Return metadata and body for one validated Knowledge Source."""
        source = KnowledgeSource.from_path(file_path, self.kb_dir, self.taxonomy)
        return dict(source.metadata), source.body
