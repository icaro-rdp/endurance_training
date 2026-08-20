#!/usr/bin/env python3
"""
Citation-Stable, Structure-Aware Chunker Prototype (Issue #5)
Repository: icaro-rdp/endurance_training

Demonstrates passage chunking across distinct corpus shapes in English and Italian:
- Short articles
- Podcast notes
- Structured books
- Converted large books with weak/missing Markdown headings
"""

import hashlib
import os
import re
from pathlib import Path
from typing import Any, ClassVar

try:
    import yaml
except ImportError:
    yaml = None


def parse_simple_yaml(yaml_str: str) -> dict[str, str]:
    """Fallback simple YAML frontmatter parser for environments without PyYAML."""
    res = {}
    for line in yaml_str.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            val = parts[1].strip().strip("\"'")
            if val and not val.startswith("-"):
                res[key] = val
    return res


class Chunk:
    """Represents a citation-stable Evidence Passage chunk."""

    def __init__(
        self,
        chunk_id: str,
        source_file: str,
        title: str,
        author: str,
        language: str,
        category: str,
        section_hierarchy: list[str],
        start_line: int,
        end_line: int,
        content: str,
    ):
        self.chunk_id = chunk_id
        self.source_file = source_file
        self.title = title
        self.author = author
        self.language = language
        self.category = category
        self.section_hierarchy = section_hierarchy
        self.start_line = start_line
        self.end_line = end_line
        self.content = content.strip()
        self.word_count = len(self.content.split())
        self.char_count = len(self.content)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "source_file": self.source_file,
            "title": self.title,
            "author": self.author,
            "language": self.language,
            "category": self.category,
            "section_hierarchy": self.section_hierarchy,
            "section_path": " > ".join(self.section_hierarchy) if self.section_hierarchy else "Root",
            "start_line": self.start_line,
            "end_line": self.end_line,
            "word_count": self.word_count,
            "char_count": self.char_count,
            "citation": f"[{self.title} ({' > '.join(self.section_hierarchy)})](file://{os.path.abspath(self.source_file)}#L{self.start_line}-L{self.end_line})",
            "content": self.content,
        }

    def __repr__(self) -> str:
        sec_str = " > ".join(self.section_hierarchy) if self.section_hierarchy else "Root"
        return f"<Chunk {self.chunk_id} [{self.language}] L{self.start_line}-{self.end_line} ({self.word_count}w) '{sec_str}'>"


class StructureAwareChunker:
    """Structure-aware Markdown chunker designed for endurance training KB sources."""

    ITALIAN_STOPWORDS: ClassVar[set[str]] = {
        "della", "degli", "delle", "dell", "nella", "negli", "nelle", "questo",
        "allenamento", "forza", "periodizzazione", "prestazione", "muscolare",
        "capitolo", "indice", "prefazione", "valutazione", "esercizi"
    }

    def __init__(self, target_words: int = 350, min_words: int = 80, max_words: int = 600, overlap_words: int = 50):
        self.target_words = target_words
        self.min_words = min_words
        self.max_words = max_words
        self.overlap_words = overlap_words

    def extract_metadata(self, lines: list[str], file_path: Path) -> tuple[dict[str, Any], int]:
        """Extract YAML frontmatter and inline document metadata."""
        metadata = {
            "title": file_path.stem.replace("_", " ").title(),
            "author": "Unknown",
            "category": "general",
            "language": "en",
            "source": file_path.name,
        }

        content_start_line = 1

        # Check for YAML frontmatter
        if lines and lines[0].strip() == "---":
            end_fm_idx = -1
            for idx in range(1, len(lines)):
                if lines[idx].strip() == "---":
                    end_fm_idx = idx
                    break

            if end_fm_idx > 0:
                fm_text = "\n".join(lines[1:end_fm_idx])
                try:
                    if yaml is not None:
                        parsed = yaml.safe_load(fm_text)
                    else:
                        parsed = parse_simple_yaml(fm_text)
                    if isinstance(parsed, dict):
                        for k in ["title", "author", "category", "language", "source"]:
                            if parsed.get(k):
                                metadata[k] = str(parsed[k]).strip()
                except (ValueError, TypeError, AttributeError):
                    pass
                content_start_line = end_fm_idx + 2

        # Check inline bold metadata fields (common in EPUB conversions)
        for line in lines[content_start_line - 1 : min(content_start_line + 40, len(lines))]:
            match_title = re.match(r"^\*\*Title:\*\*\s*(.+)$", line, re.IGNORECASE)
            if match_title:
                metadata["title"] = match_title.group(1).strip()

            match_author = re.match(r"^\*\*(?:Authors|Author):\*\*\s*(.+)$", line, re.IGNORECASE)
            if match_author:
                metadata["author"] = match_author.group(1).strip()

            match_lang = re.match(r"^\*\*Language:\*\*\s*(.+)$", line, re.IGNORECASE)
            if match_lang:
                metadata["language"] = match_lang.group(1).strip().lower()

            match_cat = re.match(r"^\*\*Category:\*\*\s*(.+)$", line, re.IGNORECASE)
            if match_cat:
                metadata["category"] = match_cat.group(1).strip().lower()

        # Heuristic language detection fallback
        if metadata["language"] not in ["en", "it"]:
            sample_text = " ".join(lines[content_start_line:content_start_line+200]).lower()
            tokens = set(re.findall(r"\b[a-zàèéìòù]+\b", sample_text))
            it_count = len(tokens.intersection(self.ITALIAN_STOPWORDS))
            if it_count >= 3 or " periodizzazione " in sample_text or " dell'" in sample_text:
                metadata["language"] = "it"
            else:
                metadata["language"] = "en"

        return metadata, content_start_line

    def _parse_heading(self, line: str) -> tuple[int, str] | None:
        """Identify standard Markdown headings or weak heading markers."""
        stripped = line.strip()
        if not stripped:
            return None

        # 1. Standard Markdown headings: #, ##, ###, ####
        md_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if md_match:
            level = len(md_match.group(1))
            title = md_match.group(2).strip()
            title = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", title)
            return level, title

        # 2. EPUB Chapter / Part Markers (Weak Heading Recovery)
        epub_cap = re.match(r"^\[(?:CAP\s+\d+|\*\*\d+\*\*|\*\*CAPITOLO\s+\d+\*\*)\]\([^\)]+\)\s*(?:\[([^\]]+)\]\([^\)]+\))?", stripped, re.IGNORECASE)
        if epub_cap:
            title_part = epub_cap.group(1) or stripped
            title_clean = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", title_part).strip("* ")
            return 1, f"Chapter {title_clean}" if not title_clean.lower().startswith(("cap", "chapter")) else title_clean

        epub_part = re.match(r"^\*\*\[(PARTE\s+\d+[^\]]*)\]\([^\)]+\)\*\*$", stripped, re.IGNORECASE)
        if epub_part:
            return 1, epub_part.group(1).strip()

        # 3. Bold Uppercase / Title Section Markers
        bold_match = re.match(r"^\*\*([A-Z0-9\s\–\—\-\:\’\?\!\,\.\'\(\)\/]+)\*\*$", stripped)
        if bold_match and len(bold_match.group(1).strip()) >= 3 and len(bold_match.group(1).strip()) <= 80:
            title_clean = bold_match.group(1).strip()
            if not title_clean.startswith("http") and not title_clean.startswith("Image"):
                return 2, title_clean

        return None

    def chunk_file(self, file_path: str) -> list[Chunk]:
        """Chunk a markdown file into citation-stable, structure-aware passages."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            lines = [line.rstrip("\n") for line in f]

        metadata, content_start_line = self.extract_metadata(lines, path)
        doc_slug = path.stem.lower().replace(" ", "_")

        # Parsing state
        heading_stack: list[tuple[int, str]] = []  # List of (level, title)
        sections: list[dict[str, Any]] = []

        current_section_lines: list[tuple[int, str]] = []
        current_section_hierarchy: list[str] = [metadata["title"]]
        current_start_line = content_start_line

        in_code_block = False

        for i in range(content_start_line - 1, len(lines)):
            line_no = i + 1
            line = lines[i]

            if line.strip().startswith("```"):
                in_code_block = not in_code_block

            if not in_code_block:
                heading = self._parse_heading(line)
                if heading:
                    level, title = heading

                    if current_section_lines:
                        sections.append({
                            "hierarchy": list(current_section_hierarchy),
                            "start_line": current_start_line,
                            "end_line": line_no - 1,
                            "lines": current_section_lines,
                        })
                        current_section_lines = []

                    while heading_stack and heading_stack[-1][0] >= level:
                        heading_stack.pop()
                    heading_stack.append((level, title))

                    current_section_hierarchy = [metadata["title"]] + [h[1] for h in heading_stack]
                    current_start_line = line_no

            current_section_lines.append((line_no, line))

        if current_section_lines:
            sections.append({
                "hierarchy": list(current_section_hierarchy),
                "start_line": current_start_line,
                "end_line": len(lines),
                "lines": current_section_lines,
            })

        chunks: list[Chunk] = []

        for sec in sections:
            sec_lines = sec["lines"]
            if not sec_lines:
                continue

            blocks: list[dict[str, Any]] = []
            curr_block_lines: list[tuple[int, str]] = []

            for line_no, line in sec_lines:
                if not line.strip() and curr_block_lines:
                    blocks.append({
                        "start_line": curr_block_lines[0][0],
                        "end_line": curr_block_lines[-1][0],
                        "text": "\n".join([l[1] for l in curr_block_lines]),
                        "words": sum(len(l[1].split()) for l in curr_block_lines)
                    })
                    curr_block_lines = []
                elif line.strip():
                    curr_block_lines.append((line_no, line))

            if curr_block_lines:
                blocks.append({
                    "start_line": curr_block_lines[0][0],
                    "end_line": curr_block_lines[-1][0],
                    "text": "\n".join([l[1] for l in curr_block_lines]),
                    "words": sum(len(l[1].split()) for l in curr_block_lines)
                })

            accum_blocks: list[dict[str, Any]] = []
            accum_words = 0

            for block in blocks:
                if block["text"].strip().startswith("![image]") and block["words"] < 5:
                    continue

                if accum_words + block["words"] > self.max_words and accum_words >= self.min_words:
                    chunk_text = "\n\n".join(b["text"] for b in accum_blocks)
                    s_line = accum_blocks[0]["start_line"]
                    e_line = accum_blocks[-1]["end_line"]

                    chunk_id = self._generate_chunk_id(doc_slug, s_line, e_line, chunk_text)
                    chunks.append(Chunk(
                        chunk_id=chunk_id,
                        source_file=str(path),
                        title=metadata["title"],
                        author=metadata["author"],
                        language=metadata["language"],
                        category=metadata["category"],
                        section_hierarchy=sec["hierarchy"],
                        start_line=s_line,
                        end_line=e_line,
                        content=chunk_text
                    ))

                    if accum_blocks and accum_blocks[-1]["words"] <= self.overlap_words:
                        accum_blocks = [accum_blocks[-1], block]
                        accum_words = accum_blocks[0]["words"] + block["words"]
                    else:
                        accum_blocks = [block]
                        accum_words = block["words"]
                else:
                    accum_blocks.append(block)
                    accum_words += block["words"]

            if accum_blocks:
                chunk_text = "\n\n".join(b["text"] for b in accum_blocks)
                s_line = accum_blocks[0]["start_line"]
                e_line = accum_blocks[-1]["end_line"]

                if chunks and len(chunk_text.split()) < self.min_words and chunks[-1].section_hierarchy == sec["hierarchy"]:
                    prev = chunks[-1]
                    merged_content = prev.content + "\n\n" + chunk_text
                    merged_end_line = e_line
                    merged_chunk_id = self._generate_chunk_id(doc_slug, prev.start_line, merged_end_line, merged_content)

                    chunks[-1] = Chunk(
                        chunk_id=merged_chunk_id,
                        source_file=str(path),
                        title=metadata["title"],
                        author=metadata["author"],
                        language=metadata["language"],
                        category=metadata["category"],
                        section_hierarchy=sec["hierarchy"],
                        start_line=prev.start_line,
                        end_line=merged_end_line,
                        content=merged_content
                    )
                else:
                    chunk_id = self._generate_chunk_id(doc_slug, s_line, e_line, chunk_text)
                    chunks.append(Chunk(
                        chunk_id=chunk_id,
                        source_file=str(path),
                        title=metadata["title"],
                        author=metadata["author"],
                        language=metadata["language"],
                        category=metadata["category"],
                        section_hierarchy=sec["hierarchy"],
                        start_line=s_line,
                        end_line=e_line,
                        content=chunk_text
                    ))

        return chunks

    def _generate_chunk_id(self, doc_slug: str, start_line: int, end_line: int, content: str) -> str:
        """Generate a deterministic, citation-stable chunk ID."""
        content_hash = hashlib.sha256(content.strip().encode("utf-8")).hexdigest()[:8]
        return f"{doc_slug}#L{start_line:04d}-L{end_line:04d}-{content_hash}"


def run_prototype_demo():
    """Run chunker on representative files across 4 corpus shapes."""
    sample_files = [
        # 1. Short Article (English)
        "Knowledge_base/Articles/knowledgeIsWatts/hiit/hiit-4x8-vs-4x4-vs-4x16.md",
        # 2. Podcast Notes (English)
        "Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_training.md",
        # 3. Structured Book (English)
        "Knowledge_base/Books/Training for the Uphill Athlete.md",
        # 4. Large Converted Book with Weak Headings (English)
        "Knowledge_base/Books/Training and Racing with a Power Meter.md",
        # 5. Large Converted Book with Weak Headings (Italian)
        "Knowledge_base/Books/Periodizzazione dell'allenamento sportivo.md",
    ]

    chunker = StructureAwareChunker(target_words=350, min_words=80, max_words=600)

    print("=" * 80)
    print("CITATION-STABLE STRUCTURE-AWARE CHUNKER DEMONSTRATION")
    print("=" * 80)

    total_chunks_processed = 0

    for file_path in sample_files:
        p = Path(file_path)
        if not p.exists():
            print(f"Skipping missing file: {file_path}")
            continue

        print(f"\nProcessing File: {file_path}")
        chunks = chunker.chunk_file(file_path)
        total_chunks_processed += len(chunks)

        print(f"  -> Generated {len(chunks)} chunks.")

        sample_idx = min(2, len(chunks) - 1) if chunks else 0
        if chunks:
            c = chunks[sample_idx]
            print("\n  --- Sample Chunk Output ---")
            print(f"  Chunk ID       : {c.chunk_id}")
            print(f"  Title          : {c.title}")
            print(f"  Author         : {c.author}")
            print(f"  Language       : {c.language}")
            print(f"  Category       : {c.category}")
            print(f"  Hierarchy Path : {' > '.join(c.section_hierarchy)}")
            print(f"  Line Range     : L{c.start_line}-L{c.end_line}")
            print(f"  Stats          : {c.word_count} words / {c.char_count} chars")
            print(f"  Citation Link  : [{c.title}](file://{os.path.abspath(c.source_file)}#L{c.start_line}-L{c.end_line})")
            print("  Snippet        :")
            snippet_lines = c.content.split("\n")[:4]
            for sl in snippet_lines:
                print(f"    | {sl[:90]}")
            if len(c.content.split("\n")) > 4:
                print("    | ...")

    print("\n" + "=" * 80)
    print(f"DEMONSTRATION COMPLETE: {total_chunks_processed} total chunks generated across representative files.")
    print("=" * 80)


if __name__ == "__main__":
    run_prototype_demo()
