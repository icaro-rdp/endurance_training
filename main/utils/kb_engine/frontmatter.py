"""
Frontmatter parsing, inferencing, and standardization module.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .errors import InvalidKnowledgeSourceError
from .taxonomy import TaxonomyRegistry

_STRING_FIELDS = ("title", "author", "language", "category", "source", "summary")
_PROVENANCE_LINE = re.compile(
    r"^(?:source|author|authors|date|language|category):", re.IGNORECASE
)


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

    def determine_category(self, file_path: Path) -> str:
        parts = file_path.relative_to(self.kb_dir).parts
        cat_map = self.taxonomy.category_map()
        for part in parts:
            if part in cat_map:
                return cat_map[part]
        return "general"

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

    def infer_metadata(self, content: str, file_path: Path) -> dict[str, Any]:
        category = self.determine_category(file_path)
        lines = content.splitlines()

        title = file_path.stem.replace("-", " ").replace("_", " ").title()
        source = ""
        date = ""
        author = ""

        for line in lines[:10]:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        for line in lines[:15]:
            if "Source:" in line or "**Source:**" in line or "_Source:" in line:
                source = re.sub(r"[\*_`]", "", line).replace("Source:", "").strip()
            if "Date:" in line or "**Date:**" in line:
                date = re.sub(r"[\*_`]", "", line).replace("Date:", "").strip()
            if "Author:" in line or "**Author:**" in line or "By:" in line:
                author = (
                    re.sub(r"[\*_`]", "", line)
                    .replace("Author:", "")
                    .replace("By:", "")
                    .strip()
                )

        rel_path = self._relative_path(file_path)
        if not self.taxonomy.valid_category(category):
            raise InvalidKnowledgeSourceError(
                rel_path,
                "no canonical category could be inferred; add reviewed "
                "frontmatter manually",
            )
        missing_provenance = [
            field
            for field, value in (("source", source), ("author", author), ("date", date))
            if not value
        ]
        if missing_provenance:
            raise InvalidKnowledgeSourceError(
                rel_path,
                "required provenance could not be inferred: "
                f"{', '.join(missing_provenance)}; add reviewed frontmatter manually",
            )
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            raise InvalidKnowledgeSourceError(
                rel_path,
                "inferred date is not in YYYY-MM-DD form; add reviewed frontmatter "
                "manually",
            )

        # Infer topics
        text = (title + " " + content[:2000]).lower()
        topic_kws = self.taxonomy.topic_keywords()
        topics = [t for t, kws in topic_kws.items() if any(kw in text for kw in kws)]
        if not topics:
            raise InvalidKnowledgeSourceError(
                self._relative_path(file_path),
                "no canonical topic could be inferred; add reviewed frontmatter "
                "manually",
            )

        # Extract summary
        summary_lines = []
        for line in lines:
            line_s = line.strip()
            unformatted_line = re.sub(r"[*_`]", "", line_s)
            if (
                line_s
                and not _PROVENANCE_LINE.match(unformatted_line)
                and not line_s.startswith("#")
                and not line_s.startswith("*")
                and not line_s.startswith("-")
                and not line_s.startswith("_")
                and not line_s.startswith("|")
                and not line_s.startswith("---")
                and not line_s.startswith("<")
            ):
                summary_lines.append(line_s)
                if len(summary_lines) >= 2:
                    break

        summary = (
            " ".join(summary_lines)[:300]
            if summary_lines
            else f"Document detailing {title}."
        )
        summary = re.sub(r"\s+", " ", summary).replace('"', "'").strip()

        return {
            "title": title,
            "language": "en",
            "category": category,
            "topics": topics[:5],
            "source": source,
            "author": author,
            "date": date,
            "summary": summary,
        }

    def standardize_file(self, file_path: Path) -> bool:
        rel_path = self._relative_path(file_path)
        content = self.read_source(file_path)
        parsed = parse_frontmatter(content, rel_path)
        fm, body = parsed.metadata, parsed.body
        if fm:
            return False

        source_body = body if parsed.has_frontmatter else content
        new_fm = self.infer_metadata(source_body, file_path)
        fm_yaml = yaml.dump(new_fm, sort_keys=False, allow_unicode=True).strip()
        new_content = f"---\n{fm_yaml}\n---\n\n{source_body}"

        try:
            file_path.write_text(new_content, encoding="utf-8")
        except OSError as error:
            raise InvalidKnowledgeSourceError(
                rel_path, f"standardized frontmatter could not be written: {error}"
            ) from error

        return True
