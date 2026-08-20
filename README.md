# Endurance Training Repository & LLM Knowledge Base

This repository contains endurance training research, articles, podcast episode notes, training plan materials, and an **LLM-Powered Knowledge Base** built according to [Slite's 2026 LLM Knowledge Base Guide](https://slite.com/learn/llm-knowledge-base) and Karpathy's **Markdown Wiki** architecture.

---

## 📚 Knowledge Base Structure

- [`Knowledge_base/INDEX.md`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/INDEX.md) — Master Sitemaps and Document Catalog.
- [`Knowledge_base/TAXONOMY.md`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/TAXONOMY.md) — Domain Taxonomy, Categories, Tags, and Frontmatter rules.
- [`Knowledge_base/Episodes/Empirical_cycling_podcast/`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Episodes/Empirical_cycling_podcast/) — 201 curated reference guides organized into 5 core pillars:
  - `physiology/` — Bioenergetics, mitochondrial signaling, cardiac remodeling, lactate shuttling.
  - `nutrition/` — Intra-ride fueling, hydration, carbohydrate ratios, RED-S, ergogenic aids.
  - `training/` — On-bike zones, intervals, base, threshold, periodization, recovery, racecraft.
  - `strength/` — Heavy compound lifting, squat mechanics, sets & reps, sprint power.
  - `metrics/` — FTP testing, Critical Power, W', durability, power vs HR, data analytics.
- [`Knowledge_base/Articles/`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Articles/) — Curated research articles and coaching papers.
- [`Knowledge_base/Books/`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Books/) — Major endurance training reference texts and chapter indexes ([`Books/_summary/INDEX.md`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Books/_summary/INDEX.md)).

---

## 🛠 Unified CLI (`main/cli.py`)

The repository includes a deep facade CLI for searching, indexing, validating, and maintaining the Knowledge Base.

### 1. Full-Text Hybrid Search (`search`)

Query the Knowledge Base using SQLite FTS5 with BM25 ranking and exact line-citation links:

```bash
# Basic natural language search (LLM-ready excerpt output)
python3 main/cli.py search "VO2max cardiac hypertrophy preload"

# Filter by category and topic
python3 main/cli.py search "carbohydrate ratio" --category nutrition --topic Carbohydrate_ratio

# Limit results and format as plain text or JSON
python3 main/cli.py search "FTP test protocol" --top 3 --format plain
python3 main/cli.py search "over-unders" --format json

# Force index rebuild before search
python3 main/cli.py search "lactate clearance" --reindex
```

### 2. Build Index & Sitemap (`build-index`)

Rebuilds the SQLite FTS5 search index (`.kb_index.sqlite`) and updates the master sitemap in [`Knowledge_base/INDEX.md`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/INDEX.md):

```bash
python3 main/cli.py build-index
```

### 3. Health & Diagnostic Validator (`validate`)

Runs automated health checks across all documents in `Knowledge_base/` to verify YAML frontmatter schema, category compliance against `TAXONOMY.md`, broken markdown links, and sitemap coverage:

```bash
python3 main/cli.py validate
```

### 4. Frontmatter Standardization (`standardize`)

Scans all `.md` files and ensures canonical YAML frontmatter (`title`, `category`, `topics`, `summary`, `source`, `author`, `date`):

```bash
# Preview / standardize missing frontmatter
python3 main/cli.py standardize

# Force re-infer and standardize all files
python3 main/cli.py standardize --force
```

---

## 🔌 Model Context Protocol (MCP) Server & Practical Guide

The repository includes a stdio MCP Server (`main/mcp_server.py`) compliant with the Model Context Protocol (2024-11-05). It allows external AI tools like **Claude Desktop**, **Cursor**, **Antigravity CLI / AGY**, and **ChatGPT** to search and query your Knowledge Base natively.

### Registered Tools

| Tool Name               | Parameters                                                    | Description                                                                                           |
| :---------------------- | :------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------- |
| `search_knowledge_base` | `query`, `category` _(opt)_, `topic` _(opt)_, `top_k` _(opt)_ | Hybrid BM25 full-text search returning ranked excerpts with exact line citations (`file://...#L...`). |
| `get_kb_index`          | _None_                                                        | Retrieves the Master Sitemap (`INDEX.md`) and domain taxonomy.                                        |
| `get_document`          | `rel_path`                                                    | Retrieves the full contents of a specific document in `Knowledge_base/`.                              |
| `validate_kb`           | _None_                                                        | Runs diagnostic audit on frontmatters, links, and indexing health.                                    |

---

### Setup Instructions by Client

#### 1. Claude Desktop App

Add the server to your `claude_desktop_config.json`:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "endurance-kb": {
      "command": "python3",
      "args": [
        "/Users/icaroredepaolini/Personale/training/endurance_training/main/mcp_server.py"
      ]
    }
  }
}
```

_Restart Claude Desktop after saving._

#### 2. Cursor IDE

1. Open Cursor Settings (`Cmd + ,` or `Ctrl + ,`).
2. Go to **Features** -> **MCP Servers** -> **Add New MCP Server**.
3. Add:
   - **Name**: `endurance-kb`
   - **Type**: `stdio`
   - **Command**: `python3 /Users/icaroredepaolini/Personale/training/endurance_training/main/mcp_server.py`

Or add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "endurance-kb": {
      "command": "python3",
      "args": [
        "/Users/icaroredepaolini/Personale/training/endurance_training/main/mcp_server.py"
      ]
    }
  }
}
```

#### 3. Antigravity CLI / AGY

Add to `~/.gemini/antigravity-cli/mcp/settings.json`:

```json
{
  "mcpServers": {
    "endurance-kb": {
      "command": "python3",
      "args": [
        "/Users/icaroredepaolini/Personale/training/endurance_training/main/mcp_server.py"
      ]
    }
  }
}
```

#### 4. Custom Python Client (JSON-RPC Subprocess)

```python
import subprocess
import json

proc = subprocess.Popen(
    ["python3", "main/mcp_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

# Initialize Handshake
proc.stdin.write(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}) + "\n")
proc.stdin.flush()
init_resp = proc.stdout.readline()

# Tool Execution
query_req = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "search_knowledge_base",
        "arguments": {"query": "Zone 2 fat oxidation", "top_k": 2}
    }
}
proc.stdin.write(json.dumps(query_req) + "\n")
proc.stdin.flush()
response = json.loads(proc.stdout.readline())

print(response["result"]["content"][0]["text"])
proc.terminate()
```

---

### Example Natural Language Prompts

Once connected in Claude or Cursor, ask prompts such as:

- **Interval Selection**: _"Using the endurance-kb tool, search for the best interval duration for VO2max and summarize the evidence on 4x8min vs 4x4min."_
- **Fueling Strategy**: _"Check the Knowledge Base for the recommended glucose to fructose ratio during long endurance efforts."_
- **Subthreshold Protocol**: _"Use get_document to retrieve `Books/Norwegian Singles Method Subthreshold.md` and explain how subthreshold sessions are monitored without a lab cart."_

### Testing the MCP Server Locally

```bash
python3 main/mcp_server.py --test
```

---

## 🚴 Endurance Training Plan Source

- `laTeX/training_plan.tex` — Main LaTeX source for the endurance training plan.
- `laTeX/training_plan.pdf` — Generated PDF version of the training plan.


