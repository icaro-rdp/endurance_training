"""Integrity checks for the English passage-retrieval benchmark."""

from __future__ import annotations

import json
import re
import unittest
from collections import Counter
from pathlib import Path

from main.utils.kb_engine.chunker import StructureAwareChunker
from main.utils.kb_engine.walker import iter_kb_documents

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KB_DIR = PROJECT_ROOT / "Knowledge_base"
BENCHMARK_PATH = PROJECT_ROOT / "docs" / "prototypes" / "003-retrieval-benchmark.json"


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _normalized(value: str) -> str:
    without_markdown = re.sub(r"[*_`]", "", value)
    return re.sub(r"\s+", " ", without_markdown).strip().casefold()


class TestRetrievalBenchmark(unittest.TestCase):
    def test_gold_labels_resolve_to_current_evidence_passages(self) -> None:
        benchmark = json.loads(
            BENCHMARK_PATH.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
        )
        queries = benchmark["queries"]
        summary = benchmark["dataset_summary"]
        self.assertIsInstance(queries, list)
        self.assertIsInstance(summary, dict)

        query_ids: set[str] = set()
        categories: Counter[str] = Counter()
        gold_count = 0
        positive_count = 0
        gold_sources: set[str] = set()
        languages: set[str] = set()
        curated_paths = {
            path.relative_to(KB_DIR).as_posix() for path in iter_kb_documents(KB_DIR)
        }
        chunker = StructureAwareChunker(KB_DIR)
        passage_cache = {}

        for query in queries:
            self.assertIsInstance(query, dict)
            query_id = str(query["id"])
            self.assertNotIn(query_id, query_ids)
            query_ids.add(query_id)
            language = str(query["language"])
            self.assertEqual(language, "en")
            languages.add(language)
            categories[str(query["category"])] += 1

            gold_passages = query["gold_passages"]
            self.assertIsInstance(gold_passages, list)
            positive_count += bool(gold_passages)
            for gold in gold_passages:
                self.assertIsInstance(gold, dict)
                rel_path = str(gold["rel_path"])
                self.assertIn(rel_path, curated_paths)
                gold_sources.add(rel_path)
                gold_count += 1
                self.assertIn(int(gold["relevance_score"]), {1, 2, 3})

                source_path = KB_DIR / rel_path
                passages = passage_cache.setdefault(
                    rel_path, chunker.chunk_document(source_path)
                )
                matching = [
                    passage
                    for passage in passages
                    if passage.start_line == int(gold["start_line"])
                    and passage.end_line == int(gold["end_line"])
                ]
                self.assertEqual(len(matching), 1, f"unresolved gold range: {rel_path}")
                passage = matching[0]
                self.assertEqual(passage.title, gold["title"])
                self.assertIn(
                    _normalized(str(gold["target_snippet"])),
                    _normalized(passage.content),
                )

        self.assertEqual(len(queries), summary["query_count"])
        self.assertEqual(positive_count, summary["positive_query_count"])
        self.assertEqual(
            len(queries) - positive_count,
            summary["negative_query_count"],
        )
        self.assertEqual(gold_count, summary["gold_passage_count"])
        self.assertEqual(len(gold_sources), summary["unique_gold_source_count"])
        self.assertEqual(sorted(languages), summary["languages"])
        self.assertEqual(dict(categories), summary["category_counts"])


if __name__ == "__main__":
    unittest.main()
