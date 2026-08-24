"""Structure-aware Markdown chunking for citation-stable Evidence Passages."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .errors import (
    CorpusChangedDuringSyncError,
    InvalidKnowledgeSourceError,
    UnsupportedLanguageError,
)
from .frontmatter import parse_frontmatter
from .models import ChunkingPolicy, EvidencePassage, PassageSizeStatus

_MARKDOWN_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_LINK = re.compile(r"\[([^]]+)]\([^)]+\)")
_CHAPTER_HEADING = re.compile(
    r"^\[(?:\*\*\d+\*\*|\*\*CHAPTER\s+\d+\*\*)\]"
    r"\([^)]+\)(?:\s*\[([^]]+)\]\([^)]+\))?",
    re.IGNORECASE,
)
_PART_HEADING = re.compile(
    r"^\*\*\[(PART\s+\d+[^]]*)\]\([^)]+\)\*\*$",
    re.IGNORECASE,
)
_BOLD_HEADING = re.compile(r"^\*\*([^*]+)\*\*$")
_METADATA_HEADING = re.compile(
    r"^(TITLE|AUTHOR|AUTHORS|LANGUAGE|CATEGORY):",
    re.IGNORECASE,
)
_H1 = re.compile(r"^#\s+(.+?)\s*$")
_SETEXT_UNDERLINE = re.compile(r"^(=+|-+)$")
_FENCE_OPEN = re.compile(r"^\s*(`{3,}|~{3,})")
_FENCE_CLOSE = re.compile(r"^\s*(`{3,}|~{3,})\s*$")
_TABLE_DELIMITER_CELL = re.compile(r"^:?-{3,}:?$")

_BlockKind = Literal["prose", "table", "quote", "fence"]


@dataclass(frozen=True, slots=True)
class _SourceMetadata:
    source_slug: str
    rel_path: str
    title: str
    author: str
    language: str
    source_type: str
    category: str
    topics: tuple[str, ...]
    source: str
    content_start: int


@dataclass(frozen=True, slots=True)
class _LineBlock:
    start_line: int
    end_line: int
    content: str
    atomic: bool = False

    @property
    def word_count(self) -> int:
        return _word_count(self.content)


@dataclass(frozen=True, slots=True)
class _Section:
    hierarchy: tuple[str, ...]
    lines: tuple[tuple[int, str], ...]


@dataclass(frozen=True, slots=True)
class _DraftPassage:
    hierarchy: tuple[str, ...]
    start_line: int
    end_line: int
    content: str
    size_status: PassageSizeStatus

    @property
    def word_count(self) -> int:
        return _word_count(self.content)


class StructureAwareChunker:
    """Turn one curated Markdown source into bounded Evidence Passages."""

    def __init__(
        self,
        kb_dir: Path,
        policy: ChunkingPolicy | None = None,
    ) -> None:
        self.kb_dir = kb_dir.resolve()
        self.policy = policy or ChunkingPolicy()

    def chunk_document(
        self,
        file_path: Path,
        expected_digest: str | None = None,
    ) -> tuple[EvidencePassage, ...]:
        lexical_path = file_path.absolute()
        if lexical_path.is_symlink():
            try:
                rel_path = lexical_path.relative_to(self.kb_dir).as_posix()
            except ValueError:
                rel_path = lexical_path.name
            raise InvalidKnowledgeSourceError(
                rel_path, "symbolic-link sources are not allowed"
            )
        path = file_path.resolve()
        try:
            relative = path.relative_to(self.kb_dir)
        except ValueError as error:
            raise ValueError(
                f"Knowledge Source is outside the Knowledge Base: {path}"
            ) from error

        rel_path = relative.as_posix()
        try:
            source_bytes = path.read_bytes()
        except OSError as error:
            if expected_digest is not None:
                raise CorpusChangedDuringSyncError from error
            raise InvalidKnowledgeSourceError(
                rel_path, f"source could not be read: {error}"
            ) from error
        if (
            expected_digest is not None
            and hashlib.sha256(source_bytes).hexdigest() != expected_digest
        ):
            raise CorpusChangedDuringSyncError
        try:
            source_text = source_bytes.decode("utf-8")
        except UnicodeDecodeError as error:
            raise InvalidKnowledgeSourceError(
                rel_path, "source is not valid UTF-8"
            ) from error
        parsed = parse_frontmatter(source_text, rel_path)
        lines = source_text.splitlines()
        metadata = self._extract_metadata(
            path,
            lines,
            parsed.metadata,
            parsed.content_start,
        )
        sections = self._parse_sections(lines, metadata)
        drafts = [
            draft for section in sections for draft in self._chunk_section(section)
        ]
        drafts = self._coalesce_small_passages(drafts)

        occurrence_by_id: dict[str, int] = {}
        passages: list[EvidencePassage] = []
        for draft in drafts:
            base_id = self._passage_id(metadata, draft)
            occurrence = occurrence_by_id.get(base_id, 0) + 1
            occurrence_by_id[base_id] = occurrence
            chunk_id = base_id if occurrence == 1 else f"{base_id}-{occurrence}"
            content = draft.content.strip()
            citation = f"{path.as_uri()}#L{draft.start_line}-L{draft.end_line}"
            passages.append(
                EvidencePassage(
                    chunk_id=chunk_id,
                    source_slug=metadata.source_slug,
                    rel_path=metadata.rel_path,
                    title=metadata.title,
                    author=metadata.author,
                    language=metadata.language,
                    source_type=metadata.source_type,
                    category=metadata.category,
                    topics=metadata.topics,
                    source=metadata.source,
                    section_hierarchy=draft.hierarchy,
                    start_line=draft.start_line,
                    end_line=draft.end_line,
                    content=content,
                    word_count=draft.word_count,
                    char_count=len(content),
                    citation=citation,
                    size_status=draft.size_status,
                )
            )
        return tuple(passages)

    def _extract_metadata(
        self,
        path: Path,
        lines: list[str],
        frontmatter: Mapping[str, object],
        content_start: int,
    ) -> _SourceMetadata:
        relative = path.relative_to(self.kb_dir)
        rel_path = relative.as_posix()
        source_slug = relative.with_suffix("").as_posix()
        source_type = self._source_type(relative)
        body_sample = lines[content_start : content_start + 200]

        title = _string_value(frontmatter.get("title"))
        title = title or self._inline_value(body_sample, "Title")
        title = title or self._first_h1(body_sample) or path.stem.replace("_", " ")

        author = _string_value(frontmatter.get("author"))
        author = author or self._inline_value(body_sample, "Authors?") or "Unknown"

        if "language" in frontmatter:
            language_value = frontmatter["language"]
            if not isinstance(language_value, str):
                raise InvalidKnowledgeSourceError(
                    rel_path,
                    "frontmatter `language` must be a string (`en` or `English`)",
                )
            declared_language = language_value.strip()
        else:
            declared_language = self._inline_value(body_sample, "Language")
        if declared_language and declared_language.casefold() not in {"en", "english"}:
            raise UnsupportedLanguageError(rel_path, declared_language)
        if "language" in frontmatter and not declared_language:
            raise UnsupportedLanguageError(rel_path, declared_language)
        language = "en"

        category = _string_value(frontmatter.get("category")) or "general"

        raw_topics = frontmatter.get("topics")
        if isinstance(raw_topics, list):
            topics = tuple(
                str(topic).strip() for topic in raw_topics if str(topic).strip()
            )
        elif isinstance(raw_topics, str) and raw_topics.strip():
            topics = (raw_topics.strip(),)
        else:
            topics = ()

        source = _string_value(frontmatter.get("source")) or rel_path
        return _SourceMetadata(
            source_slug=source_slug,
            rel_path=rel_path,
            title=title,
            author=author,
            language=language,
            source_type=source_type,
            category=category,
            topics=topics,
            source=source,
            content_start=content_start,
        )

    @staticmethod
    def _source_type(relative: Path) -> str:
        root = relative.parts[0].lower() if relative.parts else ""
        return {
            "articles": "article",
            "episodes": "podcast",
        }.get(root, "article")

    @staticmethod
    def _inline_value(lines: Iterable[str], label_pattern: str) -> str:
        pattern = re.compile(
            rf"^\s*\*\*{label_pattern}:\*\*\s*(.+?)\s*$", re.IGNORECASE
        )
        for line in lines:
            match = pattern.match(line)
            if match:
                return match.group(1).strip()
        return ""

    @staticmethod
    def _first_h1(lines: Iterable[str]) -> str:
        source_lines = tuple(lines)
        active_fence: str | None = None
        for index, line in enumerate(source_lines):
            was_fenced = active_fence is not None
            active_fence, transitioned = _advance_fence(active_fence, line)
            if was_fenced or transitioned:
                continue
            match = _H1.match(line)
            if match:
                return match.group(1).strip()
            if index + 1 < len(source_lines):
                setext = _parse_setext_heading(line, source_lines[index + 1])
                if setext and setext[0] == 1:
                    return setext[1]
        return ""

    def _parse_sections(
        self, lines: list[str], metadata: _SourceMetadata
    ) -> tuple[_Section, ...]:
        sections: list[_Section] = []
        heading_stack: list[tuple[int, str]] = []
        hierarchy: tuple[str, ...] = (metadata.title,)
        current: list[tuple[int, str]] = []
        active_fence: str | None = None

        index = metadata.content_start
        while index < len(lines):
            line_number = index + 1
            line = lines[index]
            consumed_lines = 1
            active_fence, transitioned = _advance_fence(active_fence, line)
            heading = (
                None if active_fence or transitioned else self._parse_heading(line)
            )
            if (
                heading is None
                and not active_fence
                and not transitioned
                and index + 1 < len(lines)
            ):
                heading = _parse_setext_heading(line, lines[index + 1])
                if heading:
                    consumed_lines = 2
            if heading:
                self._append_section(sections, hierarchy, current)
                current = []
                level, heading_title = heading
                while heading_stack and heading_stack[-1][0] >= level:
                    heading_stack.pop()
                heading_stack.append((level, heading_title))
                hierarchy = self._hierarchy(metadata.title, heading_stack)
            current.append((line_number, line))
            if consumed_lines == 2:
                current.append((line_number + 1, lines[index + 1]))
            index += consumed_lines

        self._append_section(sections, hierarchy, current)
        return tuple(sections)

    @staticmethod
    def _append_section(
        sections: list[_Section],
        hierarchy: tuple[str, ...],
        lines: list[tuple[int, str]],
    ) -> None:
        trimmed = _trim_blank_lines(lines)
        if trimmed:
            sections.append(_Section(hierarchy=hierarchy, lines=tuple(trimmed)))

    @staticmethod
    def _hierarchy(title: str, heading_stack: list[tuple[int, str]]) -> tuple[str, ...]:
        headings = [heading for _, heading in heading_stack]
        if headings and _normalized_heading(headings[0]) == _normalized_heading(title):
            headings.pop(0)
        return (title, *headings)

    @staticmethod
    def _parse_heading(line: str) -> tuple[int, str] | None:
        stripped = line.strip()
        match = _MARKDOWN_HEADING.match(stripped)
        if match:
            return len(match.group(1)), _clean_heading(match.group(2))

        chapter = _CHAPTER_HEADING.match(stripped)
        if chapter:
            return 1, _clean_heading(chapter.group(1) or stripped)

        part = _PART_HEADING.match(stripped)
        if part:
            return 1, _clean_heading(part.group(1))

        bold = _BOLD_HEADING.match(stripped)
        if bold:
            candidate = bold.group(1).strip()
            if (
                3 <= len(candidate) <= 100
                and candidate.upper() == candidate
                and not _METADATA_HEADING.match(candidate)
            ):
                return 2, _clean_heading(candidate)
        return None

    def _chunk_section(self, section: _Section) -> tuple[_DraftPassage, ...]:
        blocks = [
            split
            for block in self._blocks(section.lines)
            for split in self._split_oversized_block(block)
        ]
        drafts: list[_DraftPassage] = []
        pending: list[_LineBlock] = []
        pending_words = 0

        def flush_pending() -> None:
            nonlocal pending, pending_words
            if pending:
                drafts.append(self._draft(section.hierarchy, pending))
                pending = []
                pending_words = 0

        for block in blocks:
            if block.atomic and block.word_count > self.policy.max_words:
                flush_pending()
                drafts.append(
                    self._draft(
                        section.hierarchy,
                        [block],
                        PassageSizeStatus.OVERSIZED_ATOMIC_BLOCK,
                    )
                )
                continue

            if pending and self._should_flush(pending_words, block.word_count):
                flush_pending()
            pending.append(block)
            pending_words += block.word_count

        flush_pending()
        return tuple(drafts)

    def _should_flush(self, pending_words: int, next_words: int) -> bool:
        proposed = pending_words + next_words
        return proposed > self.policy.max_words or (
            proposed > self.policy.target_words
            and pending_words >= self.policy.min_words
        )

    @staticmethod
    def _blocks(lines: tuple[tuple[int, str], ...]) -> tuple[_LineBlock, ...]:
        blocks: list[_LineBlock] = []
        current: list[tuple[int, str]] = []
        current_kind: _BlockKind | None = None
        active_fence: str | None = None

        def flush() -> None:
            nonlocal current, current_kind
            trimmed = _trim_blank_lines(current)
            if not trimmed:
                current = []
                current_kind = None
                return
            blocks.append(_line_block(trimmed, atomic=current_kind != "prose"))
            current = []
            current_kind = None

        for index, item in enumerate(lines):
            stripped = item[1].strip()
            was_fenced = active_fence is not None
            active_fence, transitioned = _advance_fence(active_fence, item[1])
            if was_fenced or transitioned:
                kind: _BlockKind = "fence"
            elif not stripped:
                flush()
                continue
            elif (
                stripped.startswith("|")
                or _starts_pipe_table(lines, index)
                or (current_kind == "table" and "|" in stripped)
            ):
                kind = "table"
            elif stripped.startswith(">"):
                kind = "quote"
            else:
                kind = "prose"

            if current and current_kind != kind:
                flush()
            current_kind = kind
            current.append(item)
        flush()
        return tuple(blocks)

    def _split_oversized_block(self, block: _LineBlock) -> tuple[_LineBlock, ...]:
        if block.atomic or block.word_count <= self.policy.max_words:
            return (block,)

        pieces: list[_LineBlock] = []
        pending_lines: list[tuple[int, str]] = []
        pending_words = 0

        def flush() -> None:
            nonlocal pending_lines, pending_words
            if not pending_lines:
                return
            pieces.append(_line_block(pending_lines))
            pending_lines = []
            pending_words = 0

        for offset, line in enumerate(
            block.content.splitlines(), start=block.start_line
        ):
            words = line.split()
            if len(words) > self.policy.max_words:
                flush()
                for start in range(0, len(words), self.policy.max_words):
                    content = " ".join(words[start : start + self.policy.max_words])
                    pieces.append(_line_block([(offset, content)]))
                continue
            if pending_lines and pending_words + len(words) > self.policy.max_words:
                flush()
            pending_lines.append((offset, line))
            pending_words += len(words)
        flush()
        return tuple(pieces)

    def _draft(
        self,
        hierarchy: tuple[str, ...],
        blocks: list[_LineBlock],
        status: PassageSizeStatus | None = None,
    ) -> _DraftPassage:
        content = "\n\n".join(block.content for block in blocks).strip()
        words = _word_count(content)
        if status is None:
            status = (
                PassageSizeStatus.UNDERSIZED_SECTION
                if words < self.policy.min_words
                else PassageSizeStatus.WITHIN_POLICY
            )
        return _DraftPassage(
            hierarchy=hierarchy,
            start_line=blocks[0].start_line,
            end_line=blocks[-1].end_line,
            content=content,
            size_status=status,
        )

    def _coalesce_small_passages(
        self, drafts: list[_DraftPassage]
    ) -> list[_DraftPassage]:
        merged: list[_DraftPassage] = []
        for draft in drafts:
            if not merged:
                merged.append(draft)
                continue
            previous = merged[-1]
            combined_words = previous.word_count + draft.word_count
            can_merge = (
                PassageSizeStatus.OVERSIZED_ATOMIC_BLOCK
                not in {previous.size_status, draft.size_status}
                and combined_words <= self.policy.max_words
                and (
                    previous.word_count < self.policy.min_words
                    or draft.word_count < self.policy.min_words
                )
            )
            if not can_merge:
                merged.append(draft)
                continue
            content = f"{previous.content}\n\n{draft.content}"
            merged[-1] = _DraftPassage(
                hierarchy=_common_prefix(previous.hierarchy, draft.hierarchy),
                start_line=previous.start_line,
                end_line=draft.end_line,
                content=content,
                size_status=(
                    PassageSizeStatus.UNDERSIZED_SECTION
                    if combined_words < self.policy.min_words
                    else PassageSizeStatus.WITHIN_POLICY
                ),
            )
        return merged

    @staticmethod
    def _passage_id(metadata: _SourceMetadata, draft: _DraftPassage) -> str:
        identity = "\0".join(
            (metadata.source_slug, " > ".join(draft.hierarchy), draft.content.strip())
        )
        digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
        return f"{metadata.source_slug}::{digest}"


def _trim_blank_lines(lines: list[tuple[int, str]]) -> list[tuple[int, str]]:
    start = 0
    end = len(lines)
    while start < end and not lines[start][1].strip():
        start += 1
    while end > start and not lines[end - 1][1].strip():
        end -= 1
    return lines[start:end]


def _line_block(lines: list[tuple[int, str]], *, atomic: bool = False) -> _LineBlock:
    return _LineBlock(
        start_line=lines[0][0],
        end_line=lines[-1][0],
        content="\n".join(line for _, line in lines),
        atomic=atomic,
    )


def _clean_heading(value: str) -> str:
    without_links = _LINK.sub(r"\1", value)
    return without_links.strip().strip("* ")


def _normalized_heading(value: str) -> str:
    return re.sub(r"\W+", "", value).casefold()


def _advance_fence(active: str | None, line: str) -> tuple[str | None, bool]:
    pattern = _FENCE_OPEN if active is None else _FENCE_CLOSE
    match = pattern.match(line)
    if not match:
        return active, False

    marker = match.group(1)
    if active is None:
        return marker, True
    if marker[0] == active[0] and len(marker) >= len(active):
        return None, True
    return active, False


def _common_prefix(left: tuple[str, ...], right: tuple[str, ...]) -> tuple[str, ...]:
    prefix: list[str] = []
    for left_item, right_item in zip(left, right, strict=False):
        if left_item != right_item:
            break
        prefix.append(left_item)
    return tuple(prefix) or (left[0],)


def _string_value(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def _word_count(content: str) -> int:
    return len(content.split())


def _starts_pipe_table(
    lines: tuple[tuple[int, str], ...],
    index: int,
) -> bool:
    header = lines[index][1].strip()
    if "|" not in header or _MARKDOWN_HEADING.match(header) or index + 1 >= len(lines):
        return False
    delimiter = lines[index + 1][1].strip().strip("|")
    cells = [cell.strip() for cell in delimiter.split("|")]
    return len(cells) >= 2 and all(
        _TABLE_DELIMITER_CELL.fullmatch(cell) for cell in cells
    )


def _parse_setext_heading(
    title_line: str,
    underline_line: str,
) -> tuple[int, str] | None:
    title = title_line.strip()
    underline = _SETEXT_UNDERLINE.fullmatch(underline_line.strip())
    if not title or not underline or _MARKDOWN_HEADING.match(title):
        return None
    level = 1 if underline.group(1).startswith("=") else 2
    return level, _clean_heading(title)
