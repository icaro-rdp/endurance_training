# Endurance Training Repository & LLM Knowledge Base

This repository contains endurance training research, articles, podcast episode notes, training plan materials, and an **LLM-Powered Knowledge Base** built according to [Slite's 2026 LLM Knowledge Base Guide](https://slite.com/learn/llm-knowledge-base) and Karpathy's **Markdown Wiki** architecture.

---

## 📚 Knowledge Base Structure

- [`Knowledge_base/INDEX.md`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/INDEX.md) — Master Sitemaps and Document Catalog.
- [`Knowledge_base/TAXONOMY.md`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/TAXONOMY.md) — Domain Taxonomy, Categories, Tags, and Frontmatter rules.
- [`Knowledge_base/Articles/`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Articles/) — Curated research articles covering HIIT, metrics, nutrition, physiology, strength, training, and Zone 2.
- [`Knowledge_base/Episodes/`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Episodes/) — Empirical Cycling podcast notes and workout design guides.
- [`Knowledge_base/Books/`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Books/) — Major endurance training reference texts and chapter indexes ([`Books/_summary/INDEX.md`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Books/_summary/INDEX.md)).

---

## 🛠 Tools & Utilities

### 1. Hybrid SQLite FTS5 Search Engine
Search the Knowledge Base instantly with BM25 ranking and LLM context formatting:
```bash
python3 main/kb_search.py "VO2max cardiac hypertrophy" --top 5
```

### 2. Frontmatter Linter & Index Generator
Standardize frontmatter across all `.md` files and update `INDEX.md`:
```bash
python3 main/standardize_frontmatter.py
python3 main/build_index.py
```

### 3. Knowledge Base Health Validator
Run diagnostic checks on frontmatters, categories, links, and index coverage:
```bash
python3 main/validate_kb.py
```

---

## 🔌 Model Context Protocol (MCP) Server & Practical Guide

The repository includes a stdio MCP Server (`main/mcp_server.py`) compliant with the Model Context Protocol (2024-11-05). It allows external AI tools like **Claude Desktop**, **Cursor**, **Antigravity CLI / AGY**, and **ChatGPT** to search and query your Knowledge Base natively.

### Registered Tools

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `search_knowledge_base` | `query`, `category` *(opt)*, `topic` *(opt)*, `top_k` *(opt)* | Hybrid BM25 full-text search returning ranked excerpts with exact line citations (`file://...#L...`). |
| `get_kb_index` | *None* | Retrieves the Master Sitemap (`INDEX.md`) and domain taxonomy. |
| `get_document` | `rel_path` | Retrieves the full contents of a specific document in `Knowledge_base/`. |
| `validate_kb` | *None* | Runs diagnostic audit on frontmatters, links, and indexing health. |

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
*Restart Claude Desktop after saving.*

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

- **Interval Selection**: *"Using the endurance-kb tool, search for the best interval duration for VO2max and summarize the evidence on 4x8min vs 4x4min."*
- **Fueling Strategy**: *"Check the Knowledge Base for the recommended glucose to fructose ratio during long endurance efforts."*
- **Subthreshold Protocol**: *"Use get_document to retrieve `Books/Norwegian Singles Method Subthreshold.md` and explain how subthreshold sessions are monitored without a lab cart."*

### Testing the MCP Server Locally
```bash
python3 main/mcp_server.py --test
```

---

## 🚴 Endurance Training Plan Source
- `laTeX/training_plan.tex` — main LaTeX source for the endurance training plan.
- `laTeX/training_plan.pdf` — generated PDF version of the training plan.
