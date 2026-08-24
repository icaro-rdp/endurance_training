# Quickstart Guide

This guide walks you through setting up the **Endurance Training Knowledge Base** and connecting its Model Context Protocol (MCP) server to LLM clients (Claude Desktop, Cursor, Claude Code, Codex, Antigravity, etc.).

---

## 1. Prerequisites

Ensure you have the following installed on your machine:

- **OS**: macOS, Linux, or Windows 11 with WSL2 (native Windows cmd/PowerShell is not directly supported).
- **Git**: 2.30 or newer.
- **Python**: 3.10 or newer with SQLite support (FTS5 enabled by default in standard builds).
- **uv**: Fast Python package installer and runner ([installation guide](https://docs.astral.sh/uv/getting-started/installation/)).

---

## 2. Clone and Install

Clone the repository and install dependencies into a locked virtual environment:

```bash
git clone https://github.com/icaro-rdp/endurance_training.git
cd endurance_training
uv sync --locked
```

---

## 3. Build the Local Knowledge Index

Build the local SQLite FTS5 & vector index and verify its freshness status:

```bash
# Build the index from markdown sources
uv run endurance-kb build-index

# Verify index freshness
uv run endurance-kb status
```

You should see `"state": "fresh"` and `"is_fresh": true` in the output.

---

## 4. Test Search via CLI

Verify that local search is functioning:

```bash
uv run endurance-kb search "VO2max cardiac hypertrophy preload"
```

You should receive formatted Evidence Passages with exact line numbers and citations (e.g., `#L45-L78`).

---

## 5. Verify the MCP Server Standalone

The project includes an MCP server (`main/mcp_server.py`) exposing the Knowledge Base over standard I/O (stdio). Run the built-in diagnostic test to verify that tools and resources initialize properly:

```bash
uv run endurance-kb-mcp --test
```

If all tests pass, you are ready to connect it to your LLM clients.

---

## 6. Connect to LLM Clients & Coding Assistants

The MCP server runs over `stdio`. Replace `/absolute/path/to/endurance_training` with the absolute path to your cloned repository.

### Option A: Claude Desktop

Open your Claude Desktop configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows (WSL)**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add the `endurance-kb` server under `mcpServers`:

```json
{
  "mcpServers": {
    "endurance-kb": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/endurance_training",
        "run",
        "endurance-kb-mcp"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

> **Alternative (using the virtual environment binary directly):**
> ```json
> {
>   "mcpServers": {
>     "endurance-kb": {
>       "command": "/absolute/path/to/endurance_training/.venv/bin/endurance-kb-mcp",
>       "cwd": "/absolute/path/to/endurance_training",
>       "env": {
>         "PYTHONUNBUFFERED": "1"
>       }
>     }
>   }
> }
> ```

Restart Claude Desktop. You will see the hammer icon indicating active MCP tools.

---

### Option B: Cursor IDE

In Cursor, you can configure MCP globally or per-project:

1. Open **Cursor Settings** (`Cmd + ,` or `Ctrl + ,`) -> **Features** -> **MCP Servers**.
2. Click **+ Add New MCP Server**.
3. Fill in:
   - **Name**: `endurance-kb`
   - **Type**: `command`
   - **Command**: `uv --directory /absolute/path/to/endurance_training run endurance-kb-mcp`

Alternatively, create `.cursor/mcp.json` in your workspace root:

```json
{
  "mcpServers": {
    "endurance-kb": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/endurance_training",
        "run",
        "endurance-kb-mcp"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

---

### Option C: Claude Code (CLI)

Add the MCP server to Claude Code with:

```bash
claude mcp add endurance-kb -- uv --directory /absolute/path/to/endurance_training run endurance-kb-mcp
```

Or configure it in `~/.claude.json` / `.claude/mcp.json`.

---

### Option D: OpenAI Codex / Custom MCP Clients / Other IDEs (VS Code, Roo, Cline, Antigravity)

Use the standard stdio configuration parameters:

- **Server Name**: `endurance-kb`
- **Command / Executable**: `uv` (or absolute path to `uv`, e.g. `/usr/local/bin/uv` or `~/.cargo/bin/uv`)
- **Arguments**: `["--directory", "/absolute/path/to/endurance_training", "run", "endurance-kb-mcp"]`
- **Working Directory**: `/absolute/path/to/endurance_training`
- **Environment Variables**: `{"PYTHONUNBUFFERED": "1"}`

---

## 7. Example Queries to Try with Your LLM

Once connected, you can ask your LLM queries such as:

- *"What does the endurance knowledge base say about the difference between 4x8 min and 4x4 min VO2max intervals?"*
- *"Search the knowledge base for carbohydrate intake ratios during long endurance rides."*
- *"Check the freshness status and document count of the endurance training knowledge base."*
- *"What are the physiological adaptations of eccentric cardiac hypertrophy in cyclists?"*

The LLM will automatically invoke `search_passages` or `get_passage` and reference exact line ranges (e.g. `[FTP_training.md#L45-L70]`).

---

## 8. Available MCP Tools Reference

| Tool Name | Purpose | Key Arguments |
|---|---|---|
| `search_passages` | Lexical BM25 search over citation-stable Evidence Passages | `query`, `category`, `topic`, `source_slug`, `top_k` |
| `search_multi_passages` | Multi-query search merged with Reciprocal Rank Fusion (RRF) | `queries`, `category`, `topic`, `source_slug`, `top_k` |
| `search_knowledge_base` | Legacy alias for `search_passages` | `query`, `category`, `topic`, `top_k` |
| `get_passage` | Fetch passage metadata and full text by `chunk_id` | `chunk_id` |
| `get_document` | Read full Markdown source with path containment | `rel_path` (e.g. `Articles/...`) |
| `get_kb_status` | Check index freshness (`fresh`/`stale`/`missing`) | *(none)* |
| `get_taxonomy` | Return canonical categories and topics list | *(none)* |
| `get_sitemap` | Return master catalog and source list | *(none)* |
| `validate_kb` | Run full health and frontmatter checks | *(none)* |

---

## 9. Troubleshooting MCP Connection

- **Command not found (`uv`)**: When launching GUI apps like Claude Desktop or Cursor on macOS/Linux, GUI apps may not inherit your shell's `PATH`. Replace `"command": "uv"` with the absolute path to `uv` (find it by running `which uv` in your terminal, e.g. `/usr/local/bin/uv` or `/Users/username/.local/bin/uv` or `/Users/username/.cargo/bin/uv`).
- **Relative Path Errors**: Always use absolute paths (starting with `/`) in MCP client configurations.
- **Index Stale Warning**: If you edit Markdown documents or taxonomy, run `uv run endurance-kb build-index` to regenerate the search index.
- **Output Buffering**: Ensure `"PYTHONUNBUFFERED": "1"` is set in the `env` block of your MCP configuration so that stdio messages stream without delay.
