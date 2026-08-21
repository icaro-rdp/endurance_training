"""Unit and integration tests for the modernized MCP Server."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from main.mcp_server import _extract_text_result, create_mcp_server
from main.utils.kb_engine import KBEngine


class TestMCPServer(unittest.IsolatedAsyncioTestCase):
    """Test suite for the MCP Server tools, resources, and error handling."""

    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.kb_dir = Path(self.temp_dir.name) / "Knowledge_base"
        self.kb_dir.mkdir(parents=True)
        self.db_path = Path(self.temp_dir.name) / "main" / ".kb_index.sqlite"
        self.db_path.parent.mkdir(parents=True)

        taxonomy_content = """# Taxonomy

### 1. `hiit`
High intensity interval training.
  - `Long_intervals`
  - `VO2max`

### 2. `physiology`
Human exercise physiology.
  - `Cardiac_hypertrophy`
  - `VO2max`
"""
        (self.kb_dir / "TAXONOMY.md").write_text(taxonomy_content, encoding="utf-8")

        article_dir = self.kb_dir / "Articles"
        article_dir.mkdir(parents=True)
        doc_content = """---
title: "HIIT Intervals for VO2max"
category: "hiit"
topics:
  - "VO2max"
  - "Long_intervals"
summary: "Guide to interval prescription for maximizing aerobic power."
author: "Empirical Cycling"
language: "en"
source_type: "article"
---

# HIIT Intervals for VO2max

High intensity intervals of 4x8 minutes trigger substantial aerobic adaptations.

## Physiology & Mechanisms

These intervals promote eccentric cardiac hypertrophy and maximize stroke volume.
"""
        (article_dir / "vo2max_guide.md").write_text(doc_content, encoding="utf-8")

        # Build index
        engine = KBEngine(kb_dir=self.kb_dir, db_path=self.db_path)
        engine.build_index()

        self.server, self.engine = create_mcp_server(
            kb_dir=self.kb_dir, db_path=self.db_path
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    async def test_tools_and_resources_registered(self) -> None:
        tools = await self.server.list_tools()
        tool_names = {t.name for t in tools}
        expected_tools = {
            "search_passages",
            "search_knowledge_base",
            "search_multi_passages",
            "get_passage",
            "get_document",
            "get_kb_status",
            "get_taxonomy",
            "get_sitemap",
            "get_kb_index",
            "validate_kb",
        }
        self.assertTrue(expected_tools.issubset(tool_names))

        resources = await self.server.list_resources()
        resource_uris = {str(r.uri) for r in resources}
        expected_resources = {
            "endurance-kb://sitemap",
            "endurance-kb://taxonomy",
            "endurance-kb://status",
        }
        self.assertTrue(expected_resources.issubset(resource_uris))

    async def test_search_passages_tool(self) -> None:
        res = await self.server.call_tool(
            "search_passages",
            {"query": "eccentric cardiac hypertrophy", "top_k": 5},
        )
        text = _extract_text_result(res)
        self.assertIn("Knowledge Base Context", text)
        self.assertIn("HIIT Intervals for VO2max", text)
        self.assertIn("Source Link:", text)
        self.assertIn("#L", text)

    async def test_search_multi_passages_tool(self) -> None:
        res = await self.server.call_tool(
            "search_multi_passages",
            {"queries": ["eccentric cardiac hypertrophy", "4x8 VO2max intervals"], "top_k": 5},
        )
        text = _extract_text_result(res)
        self.assertIn("Knowledge Base Context", text)
        self.assertIn("HIIT Intervals for VO2max", text)

    async def test_search_knowledge_base_legacy_alias(self) -> None:
        res = await self.server.call_tool(
            "search_knowledge_base",
            {"query": "intervals", "top_k": 2},
        )
        text = _extract_text_result(res)
        self.assertIn("Knowledge Base Context", text)
        self.assertIn("HIIT Intervals for VO2max", text)

    async def test_search_passages_with_filters(self) -> None:
        # Match category
        res = await self.server.call_tool(
            "search_passages",
            {"query": "intervals", "category": "hiit"},
        )
        text = _extract_text_result(res)
        self.assertIn("HIIT Intervals for VO2max", text)

        # Mismatched category
        res_empty = await self.server.call_tool(
            "search_passages",
            {"query": "intervals", "category": "physiology"},
        )
        text_empty = _extract_text_result(res_empty)
        self.assertIn("No relevant Knowledge Base entries found.", text_empty)

    async def test_get_passage_tool(self) -> None:
        # Search to find a valid chunk_id
        results = self.engine.search("hypertrophy", top_k=1)
        self.assertTrue(len(results) > 0)
        chunk_id = results[0].passage.chunk_id

        res = await self.server.call_tool("get_passage", {"chunk_id": chunk_id})
        text = _extract_text_result(res)
        self.assertIn(f"Passage ID: {chunk_id}", text)
        self.assertIn("HIIT Intervals for VO2max", text)
        self.assertIn("Empirical Cycling", text)
        self.assertIn("Source: Articles/vo2max_guide.md#L", text)

        # Non-existent chunk_id
        res_missing = await self.server.call_tool(
            "get_passage", {"chunk_id": "non_existent_id"}
        )
        text_missing = _extract_text_result(res_missing)
        self.assertIn("[passage_not_found]", text_missing)

    async def test_get_document_tool_and_security(self) -> None:
        # Valid document
        res = await self.server.call_tool(
            "get_document", {"rel_path": "Articles/vo2max_guide.md"}
        )
        text = _extract_text_result(res)
        self.assertIn("HIIT Intervals for VO2max", text)

        # Path traversal attack defense
        res_traversal = await self.server.call_tool(
            "get_document", {"rel_path": "../../../etc/passwd"}
        )
        text_traversal = _extract_text_result(res_traversal)
        self.assertIn("[access_denied]", text_traversal)

        # Missing document
        res_missing = await self.server.call_tool(
            "get_document", {"rel_path": "Articles/does_not_exist.md"}
        )
        text_missing = _extract_text_result(res_missing)
        self.assertIn("[source_not_found]", text_missing)

    async def test_get_kb_status_tool(self) -> None:
        res = await self.server.call_tool("get_kb_status", {})
        text = _extract_text_result(res)
        status_data = json.loads(text)
        self.assertEqual(status_data["state"], "fresh")
        self.assertTrue(status_data["is_fresh"])
        self.assertEqual(status_data["document_count"], 1)

    async def test_get_taxonomy_tool(self) -> None:
        res = await self.server.call_tool("get_taxonomy", {})
        text = _extract_text_result(res)
        tax_data = json.loads(text)
        self.assertIn("categories", tax_data)
        self.assertIn("hiit", tax_data["categories"])
        self.assertIn("physiology", tax_data["categories"])
        self.assertIn("VO2max", tax_data["topics_by_category"]["hiit"])

    async def test_get_sitemap_and_validate_kb(self) -> None:
        res_sitemap = await self.server.call_tool("get_sitemap", {})
        text_sitemap = _extract_text_result(res_sitemap)
        self.assertIn("Master Knowledge Base Index", text_sitemap)

        res_validate = await self.server.call_tool("validate_kb", {})
        text_validate = _extract_text_result(res_validate)
        self.assertIn("Validation Status:", text_validate)

    async def test_search_error_handling_when_index_stale(self) -> None:
        # Add another source without rebuilding index -> makes index stale
        (self.kb_dir / "Articles" / "new_article.md").write_text(
            """---
title: "New"
category: "hiit"
topics: ["VO2max"]
summary: "Summary"
author: "Author"
language: "en"
---
# New
Content
""",
            encoding="utf-8",
        )

        res = await self.server.call_tool(
            "search_passages", {"query": "hypertrophy"}
        )
        text = _extract_text_result(res)
        self.assertIn("[stale_index]", text)


if __name__ == "__main__":
    unittest.main()
