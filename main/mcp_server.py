#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server for Endurance Training Knowledge Base.
Exposes KBEngine capabilities over standard I/O (stdio JSON-RPC).
"""

import sys
import json
import asyncio
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from main.kb_engine import KBEngine

engine = KBEngine()

TOOLS_LIST = [
    {
        "name": "search_knowledge_base",
        "description": "Perform full-text hybrid search across endurance training articles, podcasts, and books. Returns ranked snippets with exact file references.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query or question"},
                "category": {"type": "string", "description": "Optional category filter: metrics, hiit, zone2, strength, nutrition, physiology, periodization, book"},
                "topic": {"type": "string", "description": "Optional topic tag filter e.g. VO2max, FTP, Double_threshold"},
                "top_k": {"type": "integer", "description": "Number of top results to return (default 5)"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_kb_index",
        "description": "Get the Master Knowledge Base sitemap, catalog, and taxonomy structure.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_document",
        "description": "Retrieve full contents of a specific document in the Knowledge Base.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "rel_path": {"type": "string", "description": "Relative path e.g. Articles/KIW Articles/hiit/hiit-4x8-vs-4x4-vs-4x16.md"}
            },
            "required": ["rel_path"]
        }
    },
    {
        "name": "validate_kb",
        "description": "Run diagnostic check on Knowledge Base health, YAML frontmatters, and broken links.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]

def handle_tool_call(name: str, args: dict):
    if name == "search_knowledge_base":
        query = args.get("query", "")
        category = args.get("category")
        topic = args.get("topic")
        top_k = int(args.get("top_k", 5))

        results = engine.search(query=query, category=category, topic=topic, top_k=top_k)
        text = engine.format_llm_context(results)
        return [{"type": "text", "text": text}]

    elif name == "get_kb_index":
        if engine.index_file.exists():
            content = engine.index_file.read_text(encoding="utf-8")
        else:
            content = engine.build_sitemap()
        return [{"type": "text", "text": content}]

    elif name == "get_document":
        rel_path = args.get("rel_path", "").lstrip("/")
        doc_path = engine.kb_dir / rel_path
        if doc_path.exists() and doc_path.is_file():
            content = doc_path.read_text(encoding="utf-8")
            return [{"type": "text", "text": content}]
        else:
            return [{"type": "text", "text": f"Error: Document {rel_path} not found."}]

    elif name == "validate_kb":
        res = engine.validate()
        status = "PASSED" if res["is_healthy"] else "FAILED"
        text = f"Status: {status}\nTotal Docs: {res['total_docs']}\nErrors: {len(res['errors'])}\nWarnings: {len(res['warnings'])}"
        return [{"type": "text", "text": text}]

    else:
        raise ValueError(f"Unknown tool: {name}")

async def run_stdio_server():
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
    writer = sys.stdout.buffer

    def send_json(data):
        raw = json.dumps(data).encode("utf-8")
        writer.write(raw + b"\n")
        writer.flush()

    while True:
        try:
            line = await reader.readline()
            if not line:
                break
            req = json.loads(line.decode("utf-8"))
            method = req.get("method")
            req_id = req.get("id")

            if method == "initialize":
                send_json({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "endurance-kb-mcp", "version": "1.0.0"}
                    }
                })
            elif method == "notifications/initialized":
                pass
            elif method == "tools/list":
                send_json({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": TOOLS_LIST}
                })
            elif method == "tools/call":
                params = req.get("params", {})
                t_name = params.get("name")
                t_args = params.get("arguments", {})
                try:
                    res_content = handle_tool_call(t_name, t_args)
                    send_json({
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {"content": res_content}
                    })
                except Exception as e:
                    send_json({
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32603, "message": str(e)}
                    })
        except Exception as e:
            pass

def main():
    if "--test" in sys.argv:
        print("Testing MCP Tool Calls via KBEngine...")
        res = handle_tool_call("search_knowledge_base", {"query": "Zone 2 fat oxidation", "top_k": 2})
        print("search_knowledge_base:", res[0]["text"][:250], "...\n")
        res_idx = handle_tool_call("get_kb_index", {})
        print("get_kb_index:", res_idx[0]["text"][:150], "...\n")
        print("MCP Server tools verified successfully!")
        sys.exit(0)

    asyncio.run(run_stdio_server())

if __name__ == "__main__":
    main()
