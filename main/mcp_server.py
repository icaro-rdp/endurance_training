#!/usr/bin/env python3
"""Model Context Protocol (MCP) Server for Endurance Training Knowledge Base.

Exposes KBEngine capabilities over stdio using the official MCP Python SDK.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.types import TextContent

try:
    from main.utils.kb_engine import KBEngine, KBEngineError
except ModuleNotFoundError:
    # Keep direct script execution working without mutating sys.path.
    from utils.kb_engine import (  # type: ignore[no-redef,import-not-found]
        KBEngine,
        KBEngineError,
    )


MAX_MCP_PASSAGES = 20


def _resolve_max_passages(max_passages: int | None) -> int:
    """Use server-side selection by default, with an explicit caller ceiling."""
    if max_passages is None:
        return MAX_MCP_PASSAGES
    return max(1, min(int(max_passages), MAX_MCP_PASSAGES))


def create_mcp_server(
    kb_dir: Path | None = None,
    db_path: Path | None = None,
) -> tuple[MCPServer, KBEngine]:
    """Create and configure the Endurance Knowledge Base MCP Server."""
    engine = KBEngine(kb_dir=kb_dir, db_path=db_path)
    server = MCPServer(
        name="endurance-knowledge-base",
        version="0.2.0",
        instructions=(
            "Endurance Training Knowledge Base retriever. "
            "Use search_passages to retrieve citation-backed Evidence Passages "
            "for training, physiology, nutrition, and planning. "
            "Passages contain exact source lines, section hierarchy, and source links."
        ),
    )

    @server.tool(
        name="search_passages",
        description=(
            "Search for citation-stable Evidence Passages across endurance "
            "training articles and podcasts using local hybrid retrieval. "
            "Explores a bounded candidate pool and returns only passages that "
            "meet the server-side relevance policy, or insufficient_evidence."
        ),
    )
    def search_passages(
        query: str,
        category: str | None = None,
        topic: str | None = None,
        source_slug: str | None = None,
        max_passages: int | None = None,
    ) -> str:
        """Search the Knowledge Base for evidence passages matching the athlete query.

        Args:
            query: The search term or athlete question in English.
            category: Optional category filter (e.g. training, physiology,
                nutrition, planning).
            topic: Optional topic filter (e.g. VO2max_and_aerobic_hiit,
                FTP_and_functional_metrics, Carbohydrate_fueling_and_gut_training).
            source_slug: Optional source slug filter (e.g.
                Fick_equation_and_cardiac_remodeling).
            max_passages: Optional explicit ceiling from 1 to 20. Omit to
                return every passage retained by the server-side policy.
        """
        try:
            results = engine.search(
                query=query,
                category=category,
                topic=topic,
                source_slug=source_slug,
                top_k=_resolve_max_passages(max_passages),
            )
            return engine.format_llm_context(results)
        except KBEngineError as exc:
            return f"Error: [{exc.code}] {exc}"
        except Exception as exc:
            return f"Unexpected search error: {exc}"

    @server.tool(
        name="search_knowledge_base",
        description=(
            "Alias for search_passages. Search endurance training evidence passages "
            "with exact line citations."
        ),
    )
    def search_knowledge_base(
        query: str,
        category: str | None = None,
        topic: str | None = None,
        max_passages: int | None = None,
    ) -> str:
        """Legacy alias for search_passages."""
        return search_passages(
            query=query,
            category=category,
            topic=topic,
            max_passages=max_passages,
        )

    @server.tool(
        name="search_multi_passages",
        description=(
            "Execute distinct sub-queries and merge results with Reciprocal Rank "
            "Fusion (RRF); use for compound or multi-faceted athlete questions."
        ),
    )
    def search_multi_passages(
        queries: list[str],
        category: str | None = None,
        topic: str | None = None,
        source_slug: str | None = None,
        max_passages: int | None = None,
    ) -> str:
        """Search the Knowledge Base using multiple sub-queries with rank fusion.

        Args:
            queries: List of search queries/sub-questions in English.
            category: Optional category filter.
            topic: Optional topic filter.
            source_slug: Optional source slug filter.
            max_passages: Optional explicit ceiling from 1 to 20. Omit to
                return every passage retained by the server-side policy.
        """
        try:
            results = engine.multi_search(
                queries=queries,
                category=category,
                topic=topic,
                source_slug=source_slug,
                top_k=_resolve_max_passages(max_passages),
            )
            return engine.format_llm_context(results)
        except KBEngineError as exc:
            return f"Error: [{exc.code}] {exc}"
        except Exception as exc:
            return f"Unexpected search error: {exc}"

    @server.tool(
        name="get_passage",
        description="Retrieve full details of an Evidence Passage by its chunk_id.",
    )
    def get_passage(chunk_id: str) -> str:
        """Retrieve a specific Evidence Passage by chunk ID.

        Args:
            chunk_id: Unique SHA-256 derived identifier for the passage.
        """
        try:
            passage = engine.get_passage(chunk_id.strip())
            if passage is None:
                return (
                    "Error: [passage_not_found] Passage with chunk_id "
                    f"'{chunk_id}' not found."
                )
            loc = f"{passage.rel_path}#L{passage.start_line}-L{passage.end_line}"
            return (
                f"Passage ID: {passage.chunk_id}\n"
                f"Source: {loc}\n"
                f"Citation Link: {passage.citation}\n"
                f"Title: {passage.title}\n"
                f"Author: {passage.author}\n"
                f"Category: {passage.category}\n"
                f"Topics: {', '.join(passage.topics)}\n"
                f"Section: {passage.section_path}\n"
                f"Size Status: {passage.size_status.value} "
                f"({passage.word_count} words)\n"
                f"\n--- Content ---\n"
                f"{passage.content}"
            )
        except KBEngineError as exc:
            return f"Error: [{exc.code}] {exc}"
        except Exception as exc:
            return f"Unexpected error retrieving passage: {exc}"

    @server.tool(
        name="get_document",
        description=(
            "Retrieve the full Markdown text of a curated Knowledge Source document. "
            "Path must be relative to Knowledge_base/."
        ),
    )
    def get_document(rel_path: str) -> str:
        """Retrieve full contents of a curated document with strict path containment.

        Args:
            rel_path: Relative path within Knowledge_base/ (e.g.
                'Articles/knowledgeIsWatts/hiit/hiit-4x8-vs-4x4-vs-4x16.md').
        """
        try:
            clean_rel = rel_path.strip().lstrip("/")
            doc_path = (engine.kb_dir / clean_rel).resolve()
            if not doc_path.is_relative_to(engine.kb_dir.resolve()):
                return (
                    "Error: [access_denied] Path "
                    f"'{rel_path}' is outside the Knowledge Base."
                )
            if not doc_path.is_file():
                return (
                    "Error: [source_not_found] Document "
                    f"'{rel_path}' not found in the Knowledge Base."
                )
            return doc_path.read_text(encoding="utf-8")
        except Exception as exc:
            return f"Error reading document '{rel_path}': {exc}"

    @server.tool(
        name="get_kb_status",
        description="Inspect freshness status and metadata of the Derived Index.",
    )
    def get_kb_status() -> str:
        """Inspect the current freshness state of the local passage index."""
        try:
            status = engine.get_kb_status()
            return json.dumps(status.to_dict(), indent=2)
        except Exception as exc:
            return f"Error retrieving index status: {exc}"

    @server.tool(
        name="get_taxonomy",
        description="Get canonical categories and allowed topics in Knowledge Base.",
    )
    def get_taxonomy() -> str:
        """Get canonical taxonomy categories and topics."""
        try:
            tax = engine.taxonomy
            cats = tax.categories()
            data: dict[str, Any] = {
                "categories": cats,
                "topics_by_category": {cat: tax.topics(cat) for cat in cats},
            }
            return json.dumps(data, indent=2)
        except Exception as exc:
            return f"Error retrieving taxonomy: {exc}"

    @server.tool(
        name="get_sitemap",
        description="Get Master Knowledge Base sitemap, catalog, and document listing.",
    )
    def get_sitemap() -> str:
        """Get the master catalog / sitemap."""
        try:
            if engine.index_file.exists():
                return engine.index_file.read_text(encoding="utf-8")
            return engine.build_sitemap()
        except Exception as exc:
            return f"Error retrieving sitemap: {exc}"

    @server.tool(
        name="get_kb_index",
        description="Alias for get_sitemap. Get the master catalog / sitemap.",
    )
    def get_kb_index() -> str:
        """Legacy alias for get_sitemap."""
        return get_sitemap()

    @server.tool(
        name="validate_kb",
        description=(
            "Run diagnostic validation on Knowledge Base health, frontmatter schemas, "
            "and link integrity."
        ),
    )
    def validate_kb() -> str:
        """Run health validation across the Knowledge Base."""
        try:
            res = engine.validate()
            status = "PASSED" if res["is_healthy"] else "FAILED"
            return (
                f"Validation Status: {status}\n"
                f"Total Documents: {res['total_docs']}\n"
                f"Errors: {len(res['errors'])}\n"
                f"Warnings: {len(res['warnings'])}"
            )
        except Exception as exc:
            return f"Error running validation: {exc}"

    # Resources
    @server.resource("endurance-kb://sitemap", name="Knowledge Base Sitemap")
    def resource_sitemap() -> str:
        if engine.index_file.exists():
            return engine.index_file.read_text(encoding="utf-8")
        return engine.build_sitemap()

    @server.resource("endurance-kb://taxonomy", name="Knowledge Base Taxonomy")
    def resource_taxonomy() -> str:
        taxonomy_file = engine.kb_dir / "TAXONOMY.md"
        if taxonomy_file.exists():
            return taxonomy_file.read_text(encoding="utf-8")
        return get_taxonomy()

    @server.resource("endurance-kb://status", name="Index Freshness Status")
    def resource_status() -> str:
        return get_kb_status()

    return server, engine


def _extract_text_result(res: Any) -> str:
    """Helper to extract text output from an MCP tool call result."""
    if hasattr(res, "content") and isinstance(res.content, list):
        for block in res.content:
            if isinstance(block, TextContent):
                return block.text
            if hasattr(block, "text") and isinstance(block.text, str):
                return block.text
    if hasattr(res, "structured_content") and isinstance(res.structured_content, dict):
        result_val = res.structured_content.get("result")
        if isinstance(result_val, str):
            return result_val
    return str(res)


def main() -> None:
    """Run MCP server in stdio mode, or execute diagnostic self-test with --test."""
    if "--test" in sys.argv:
        print("Testing MCP Server tools and resources...")
        server, _ = create_mcp_server()
        import asyncio

        async def run_test() -> None:
            tools = await server.list_tools()
            print(f"Registered tools ({len(tools)}): {[t.name for t in tools]}")
            resources = await server.list_resources()
            resource_names = [r.name for r in resources]
            print(f"Registered resources ({len(resources)}): {resource_names}")

            # Test search_passages
            res = await server.call_tool(
                "search_passages", {"query": "Zone 2 fat oxidation"}
            )
            print("\n--- Tool: search_passages ---")
            print(_extract_text_result(res)[:300], "...\n")

            # Test get_kb_status
            res_status = await server.call_tool("get_kb_status", {})
            print("--- Tool: get_kb_status ---")
            print(_extract_text_result(res_status), "\n")

            # Test get_taxonomy
            res_tax = await server.call_tool("get_taxonomy", {})
            print("--- Tool: get_taxonomy ---")
            print(_extract_text_result(res_tax)[:200], "...\n")

            # Test get_document containment
            res_doc = await server.call_tool(
                "get_document", {"rel_path": "../../../etc/passwd"}
            )
            print("--- Tool: get_document (traversal defense) ---")
            print(_extract_text_result(res_doc), "\n")

            print("MCP Server verified successfully!")

        asyncio.run(run_test())
        sys.exit(0)

    server, _ = create_mcp_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
