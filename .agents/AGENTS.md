# AI Agent Instructions for Endurance Training Knowledge Base

start each response with "using custom instructions:"

When working on tasks, answering user questions, or generating training plans in this repository, follow these instructions to ensure high-accuracy responses and zero hallucinations:

---

## 1. Always Consult the Knowledge Base First

Before generating endurance training guidance or answering questions about metrics, physiology, HIIT, Zone 2, strength, or periodization:

- Run a hybrid search query using `python3 main/cli.py search "<query>"` or call the MCP tool `search_knowledge_base`.
- Reference the master sitemap at [`Knowledge_base/INDEX.md`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/INDEX.md) and taxonomy at [`Knowledge_base/TAXONOMY.md`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/TAXONOMY.md).

## 2. Formatting & Citation Standards

- Cite exact file links with line ranges when referencing evidence (e.g. `[FTP Training Guide](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/Episodes/Empirical_cycling_podcast/training/threshold/FTP_training.md#L45-L70)`).
- Quote key scientific principles (e.g., cardiac stroke volume / preload mechanics, 4x8min interval benefits, double-threshold lactate boundaries).

## 3. Maintaining Knowledge Base Quality

When adding new research, articles, or podcast notes:

1. Include valid YAML frontmatter header conforming to [`Knowledge_base/TAXONOMY.md`](file:///Users/icaroredepaolini/Personale/training/endurance_training/Knowledge_base/TAXONOMY.md).
2. Run `python3 main/cli.py build-index` to update `INDEX.md`.
3. Run `python3 main/cli.py search --reindex "<query>"` to update the FTS5 index.
4. Run `python3 main/cli.py validate` to confirm zero schema or link errors.

