"""Structure-aware Markdown chunking for citation-stable Evidence Passages."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import yaml

from .errors import UnsupportedLanguageError
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
_FENCE = re.compile(r"^\s*(`{3,}|~{3,})")


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

    def chunk_document(self, file_path: Path) -> tuple[EvidencePassage, ...]:
        path = file_path.resolve()
        try:
            path.relative_to(self.kb_dir)
        except ValueError as error:
            raise ValueError(
                f"Knowledge Source is outside the Knowledge Base: {path}"
            ) from error

        lines = path.read_text(encoding="utf-8").splitlines()
        metadata = self._extract_metadata(path, lines)
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

    def _extract_metadata(self, path: Path, lines: list[str]) -> _SourceMetadata:
        frontmatter, content_start = self._frontmatter(lines)
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

        declared_language = _string_value(frontmatter.get("language"))
        declared_language = declared_language or self._inline_value(
            body_sample, "Language"
        )
        if declared_language and declared_language.casefold() not in {"en", "english"}:
            raise UnsupportedLanguageError(rel_path, declared_language)
        language = "en"

        category = _string_value(frontmatter.get("category")) or "general"
        if source_type == "book" and category.casefold() in {
            "general",
            "book",
            "books",
        }:
            category = "book"

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
    def _frontmatter(lines: list[str]) -> tuple[dict[str, object], int]:
        if not lines or lines[0].strip() != "---":
            return {}, 0
        try:
            end = next(
                index for index in range(1, len(lines)) if lines[index].strip() == "---"
            )
        except StopIteration as error:
            raise ValueError("Unclosed YAML frontmatter") from error
        loaded = yaml.safe_load("\n".join(lines[1:end])) or {}
        if not isinstance(loaded, dict):
            raise ValueError("YAML frontmatter must be a mapping")
        if any(not isinstance(key, str) for key in loaded):
            raise ValueError("YAML frontmatter keys must be strings")
        return {str(key): value for key, value in loaded.items()}, end + 1

    @staticmethod
    def _source_type(relative: Path) -> str:
        root = relative.parts[0].lower() if relative.parts else ""
        return {
            "articles": "article",
            "episodes": "podcast",
            "books": "book",
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
        for line in lines:
            match = _H1.match(line)
            if match:
                return match.group(1).strip()
        return ""

    def _parse_sections(
        self, lines: list[str], metadata: _SourceMetadata
    ) -> tuple[_Section, ...]:
        sections: list[_Section] = []
        heading_stack: list[tuple[int, str]] = []
        hierarchy: tuple[str, ...] = (metadata.title,)
        current: list[tuple[int, str]] = []
        active_fence: str | None = None

        for index in range(metadata.content_start, len(lines)):
            line_number = index + 1
            line = lines[index]
            fence = _fence_marker(line)
            if fence and (active_fence is None or active_fence == fence):
                active_fence = fence if active_fence is None else None
                heading = None
            else:
                heading = None if active_fence else self._parse_heading(line)
            if heading:
                self._append_section(sections, hierarchy, current)
                current = []
                level, heading_title = heading
                while heading_stack and heading_stack[-1][0] >= level:
                    heading_stack.pop()
                heading_stack.append((level, heading_title))
                hierarchy = self._hierarchy(metadata.title, heading_stack)
            current.append((line_number, line))

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
        active_fence: str | None = None

        def flush() -> None:
            nonlocal current
            trimmed = _trim_blank_lines(current)
            if not trimmed:
                current = []
                return
            nonempty = [line.strip() for _, line in trimmed if line.strip()]
            atomic = (
                any(_fence_marker(line) for line in nonempty)
                or all(line.startswith("|") for line in nonempty)
                or all(line.startswith(">") for line in nonempty)
            )
            blocks.append(_line_block(trimmed, atomic=atomic))
            current = []

        for item in lines:
            stripped = item[1].strip()
            fence = _fence_marker(stripped)
            if fence and (active_fence is None or active_fence == fence):
                active_fence = fence if active_fence is None else None
                current.append(item)
                continue
            if not stripped and active_fence is None:
                flush()
            else:
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


def _fence_marker(line: str) -> str | None:
    match = _FENCE.match(line)
    return match.group(1)[0] if match else None


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
