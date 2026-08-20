"""Contract tests for citation-stable, structure-aware Markdown chunking."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from main.utils.kb_engine.chunker import StructureAwareChunker
from main.utils.kb_engine.errors import UnsupportedLanguageError
from main.utils.kb_engine.models import ChunkingPolicy, EvidencePassage

PASSAGE_FIELDS = (
    "chunk_id",
    "source_slug",
    "rel_path",
    "title",
    "author",
    "language",
    "source_type",
    "category",
    "topics",
    "source",
    "section_hierarchy",
    "start_line",
    "end_line",
    "content",
    "word_count",
    "char_count",
    "citation",
    "size_status",
)


class TestStructureAwareChunker(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp_dir.cleanup)
        self.kb_dir = Path(self._temp_dir.name) / "Knowledge_base"
        self.kb_dir.mkdir()

    def _write(self, rel_path: str, content: str) -> Path:
        path = self.kb_dir / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def _chunker(
        self,
        *,
        target_words: int = 30,
        min_words: int = 1,
        max_words: int = 60,
    ) -> StructureAwareChunker:
        return StructureAwareChunker(
            self.kb_dir,
            ChunkingPolicy(
                target_words=target_words,
                min_words=min_words,
                max_words=max_words,
            ),
        )

    @staticmethod
    def _snapshot(
        passages: tuple[EvidencePassage, ...],
    ) -> tuple[tuple[object, ...], ...]:
        return tuple(
            tuple(getattr(passage, field) for field in PASSAGE_FIELDS)
            for passage in passages
        )

    def test_frontmatter_is_excluded_and_source_lines_are_exact(self) -> None:
        content = "\n".join(
            (
                "---",
                "title: Frontmatter Offsets",
                "author: Ada Athlete",
                "language: en",
                "source_type: article",
                "category: physiology",
                "topics: [VO2max, Mitochondrial_density]",
                "source: Lab notebook",
                "---",
                "",
                "First cited body line.",
                "Second cited body line.",
            )
        )
        path = self._write("Articles/offsets.md", content)

        passages = self._chunker(max_words=100).chunk_document(path)

        self.assertIsInstance(passages, tuple)
        self.assertEqual(len(passages), 1)
        passage = passages[0]
        self.assertIsInstance(passage, EvidencePassage)
        self.assertEqual((passage.start_line, passage.end_line), (11, 12))
        self.assertEqual(
            passage.content,
            "First cited body line.\nSecond cited body line.",
        )
        source_lines = content.splitlines()
        self.assertEqual(
            passage.content,
            "\n".join(source_lines[passage.start_line - 1 : passage.end_line]),
        )
        self.assertEqual(passage.title, "Frontmatter Offsets")
        self.assertEqual(passage.author, "Ada Athlete")
        self.assertEqual(passage.language, "en")
        self.assertEqual(passage.source_type, "article")
        self.assertEqual(passage.category, "physiology")
        self.assertEqual(passage.topics, ("VO2max", "Mitochondrial_density"))
        self.assertEqual(passage.source, "Lab notebook")
        self.assertEqual(passage.rel_path, "Articles/offsets.md")
        self.assertEqual(passage.word_count, len(passage.content.split()))
        self.assertEqual(passage.char_count, len(passage.content))
        self.assertIn("#L11-L12", passage.citation)
        self.assertEqual(passage.size_status, "within_policy")

    def test_nested_heading_hierarchy_resets_when_a_parent_changes(self) -> None:
        content = "\n".join(
            (
                "# Endurance Guide",
                "",
                "Opening context.",
                "",
                "## Physiology",
                "",
                "### Mitochondria",
                "",
                "Unique adaptation evidence.",
                "",
                "## Training",
                "",
                "Unique interval prescription.",
            )
        )
        path = self._write("Articles/hierarchy.md", content)

        passages = self._chunker(max_words=100).chunk_document(path)

        adaptation = next(
            passage
            for passage in passages
            if "Unique adaptation evidence" in passage.content
        )
        prescription = next(
            passage
            for passage in passages
            if "Unique interval prescription" in passage.content
        )
        self.assertEqual(
            adaptation.section_hierarchy[-3:],
            ("Endurance Guide", "Physiology", "Mitochondria"),
        )
        self.assertEqual(
            prescription.section_hierarchy[-2:],
            ("Endurance Guide", "Training"),
        )
        self.assertNotIn("Mitochondria", prescription.section_hierarchy)

    def test_chunk_id_survives_blank_lines_inserted_before_unchanged_content(
        self,
    ) -> None:
        original = "\n".join(
            (
                "# Stable Section",
                "",
                "The evidence text remains byte-for-byte identical.",
            )
        )
        shifted = "\n\n" + original
        path = self._write("Articles/stable.md", original)
        chunker = self._chunker(max_words=100)

        before = next(
            passage
            for passage in chunker.chunk_document(path)
            if "byte-for-byte" in passage.content
        )
        path.write_text(shifted, encoding="utf-8")
        after = next(
            passage
            for passage in chunker.chunk_document(path)
            if "byte-for-byte" in passage.content
        )

        self.assertEqual(before.content, after.content)
        self.assertEqual(before.section_hierarchy, after.section_hierarchy)
        self.assertEqual(before.chunk_id, after.chunk_id)
        self.assertEqual(after.start_line, before.start_line + 2)
        self.assertEqual(after.end_line, before.end_line + 2)
        self.assertNotEqual(before.citation, after.citation)

    def test_relative_source_identity_prevents_same_basename_collisions(self) -> None:
        article_path = self._write(
            "Articles/shared.md",
            "# Shared\n\nArticle-specific evidence.",
        )
        book_path = self._write(
            "Books/shared.md",
            "# Shared\n\nBook-specific evidence.",
        )
        chunker = self._chunker(max_words=100)

        article = chunker.chunk_document(article_path)[0]
        book = chunker.chunk_document(book_path)[0]

        self.assertEqual(article.rel_path, "Articles/shared.md")
        self.assertEqual(book.rel_path, "Books/shared.md")
        self.assertFalse(Path(article.rel_path).is_absolute())
        self.assertFalse(Path(book.rel_path).is_absolute())
        self.assertNotEqual(article.source_slug, book.source_slug)
        self.assertNotEqual(article.chunk_id, book.chunk_id)

    def test_language_defaults_to_english_without_metadata(self) -> None:
        path = self._write(
            "Articles/aerobic-threshold.md",
            "\n".join(
                (
                    "# Aerobic Threshold",
                    "",
                    "Aerobic training improves endurance performance.",
                )
            ),
        )

        passages = self._chunker(max_words=100).chunk_document(path)

        self.assertGreater(len(passages), 0)
        self.assertTrue(all(passage.language == "en" for passage in passages))

    def test_declared_non_english_source_is_rejected(self) -> None:
        path = self._write(
            "Articles/non-english.md",
            "---\ntitle: Unsupported Source\nlanguage: fr\n---\n\nEvidence.",
        )

        with self.assertRaises(UnsupportedLanguageError) as caught:
            self._chunker(max_words=100).chunk_document(path)

        self.assertEqual(caught.exception.code, "unsupported_language")
        self.assertIn("English sources only", str(caught.exception))

    def test_books_category_is_normalized_to_singular_taxonomy_value(self) -> None:
        path = self._write(
            "Books/manual.md",
            "\n".join(
                (
                    "---",
                    "title: Training Manual",
                    "category: Books",
                    "---",
                    "",
                    "Book evidence belongs to the canonical category.",
                )
            ),
        )

        passages = self._chunker(max_words=100).chunk_document(path)

        self.assertGreater(len(passages), 0)
        self.assertTrue(all(passage.category == "book" for passage in passages))

    def test_oversized_single_line_is_split_without_exceeding_max_words(self) -> None:
        words = [f"token{index:02d}" for index in range(1, 28)]
        path = self._write("Articles/long-line.md", " ".join(words))
        policy = ChunkingPolicy(target_words=8, min_words=3, max_words=10)

        passages = StructureAwareChunker(self.kb_dir, policy).chunk_document(path)

        self.assertGreater(len(passages), 1)
        self.assertTrue(
            all(passage.word_count <= policy.max_words for passage in passages)
        )
        self.assertTrue(
            all(
                (passage.start_line, passage.end_line) == (1, 1) for passage in passages
            )
        )
        self.assertTrue(
            all(passage.size_status != "oversized_atomic_block" for passage in passages)
        )
        observed_words = {
            word for passage in passages for word in passage.content.split()
        }
        self.assertEqual(observed_words, set(words))

    def test_oversized_fenced_code_is_preserved_and_diagnosed(self) -> None:
        code_words = " ".join(f"value{index:02d}" for index in range(1, 16))
        content = f"```text\n{code_words}\n```"
        path = self._write("Articles/atomic-code.md", content)
        policy = ChunkingPolicy(target_words=6, min_words=3, max_words=8)

        passages = StructureAwareChunker(self.kb_dir, policy).chunk_document(path)

        self.assertEqual(len(passages), 1)
        passage = passages[0]
        self.assertEqual(passage.content, content)
        self.assertEqual((passage.start_line, passage.end_line), (1, 3))
        self.assertGreater(passage.word_count, policy.max_words)
        self.assertEqual(passage.size_status, "oversized_atomic_block")

    def test_tilde_fenced_code_is_atomic_and_ignores_internal_headings(self) -> None:
        code_words = " ".join(f"value{index:02d}" for index in range(1, 16))
        content = f"~~~text\n## Not a document heading\n{code_words}\n~~~"
        path = self._write("Articles/tilde-code.md", content)
        policy = ChunkingPolicy(target_words=6, min_words=3, max_words=8)

        passages = StructureAwareChunker(self.kb_dir, policy).chunk_document(path)

        self.assertEqual(len(passages), 1)
        passage = passages[0]
        self.assertEqual(passage.content, content)
        self.assertEqual(passage.section_hierarchy, ("tilde-code",))
        self.assertEqual(passage.size_status, "oversized_atomic_block")

    def test_longer_fence_is_not_closed_by_shorter_nested_fence(self) -> None:
        code_words = " ".join(f"value{index:02d}" for index in range(1, 16))
        content = (
            f"````markdown\n```\n## Not a document heading\n{code_words}\n```\n````"
        )
        path = self._write("Articles/outer-fence.md", content)
        policy = ChunkingPolicy(target_words=6, min_words=3, max_words=8)

        passages = StructureAwareChunker(self.kb_dir, policy).chunk_document(path)

        self.assertEqual(len(passages), 1)
        passage = passages[0]
        self.assertEqual(passage.content, content)
        self.assertEqual((passage.start_line, passage.end_line), (1, 6))
        self.assertEqual(passage.section_hierarchy, ("outer-fence",))
        self.assertEqual(passage.size_status, "oversized_atomic_block")

    def test_table_adjacent_to_heading_remains_a_separate_atomic_block(self) -> None:
        table = "\n".join(
            (
                "| Metric | Evidence |",
                "| --- | --- |",
                "| Threshold | "
                + " ".join(f"value{index:02d}" for index in range(1, 12))
                + " |",
            )
        )
        content = f"# Table Evidence\n{table}"
        path = self._write("Articles/atomic-table.md", content)
        policy = ChunkingPolicy(target_words=6, min_words=3, max_words=8)

        passages = StructureAwareChunker(self.kb_dir, policy).chunk_document(path)

        table_passage = next(
            passage for passage in passages if "| Metric" in passage.content
        )
        self.assertEqual(table_passage.content, table)
        self.assertEqual((table_passage.start_line, table_passage.end_line), (2, 4))
        self.assertEqual(table_passage.size_status, "oversized_atomic_block")

    def test_blockquote_adjacent_to_heading_remains_a_separate_atomic_block(
        self,
    ) -> None:
        quote = "> " + " ".join(f"value{index:02d}" for index in range(1, 16))
        content = f"# Quoted Evidence\n{quote}"
        path = self._write("Articles/atomic-quote.md", content)
        policy = ChunkingPolicy(target_words=6, min_words=3, max_words=8)

        passages = StructureAwareChunker(self.kb_dir, policy).chunk_document(path)

        quote_passage = next(
            passage for passage in passages if passage.content.startswith(">")
        )
        self.assertEqual(quote_passage.content, quote)
        self.assertEqual((quote_passage.start_line, quote_passage.end_line), (2, 2))
        self.assertEqual(quote_passage.size_status, "oversized_atomic_block")

    def test_chunking_is_deterministic_across_instances(self) -> None:
        path = self._write(
            "Episodes/deterministic.md",
            "\n".join(
                (
                    "---",
                    "title: Deterministic Notes",
                    "language: en",
                    "topics: [FTP]",
                    "---",
                    "",
                    "# Threshold",
                    "",
                    "Alpha beta gamma delta epsilon zeta eta theta.",
                    "",
                    "## Intervals",
                    "",
                    "Iota kappa lambda mu nu xi omicron pi.",
                )
            ),
        )
        policy = ChunkingPolicy(target_words=8, min_words=2, max_words=12)

        first = StructureAwareChunker(self.kb_dir, policy).chunk_document(path)
        second = StructureAwareChunker(self.kb_dir, policy).chunk_document(path)

        self.assertIsInstance(first, tuple)
        self.assertTrue(all(isinstance(passage, EvidencePassage) for passage in first))
        self.assertEqual(self._snapshot(first), self._snapshot(second))


if __name__ == "__main__":
    unittest.main()
