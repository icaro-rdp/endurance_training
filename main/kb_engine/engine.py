"""
Unified Deep Facade Class: KBEngine
"""

import os
from pathlib import Path
from main.kb_engine.frontmatter import FrontmatterManager
from main.kb_engine.fts import FTSSearchEngine
from main.kb_engine.validator import KBValidator

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_KB_DIR = PROJECT_ROOT / "Knowledge_base"
DEFAULT_DB_PATH = PROJECT_ROOT / ".kb_index.sqlite"
DEFAULT_INDEX_FILE = DEFAULT_KB_DIR / "INDEX.md"

class KBEngine:
    def __init__(
        self,
        kb_dir: Path = DEFAULT_KB_DIR,
        db_path: Path = DEFAULT_DB_PATH,
        index_file: Path = DEFAULT_INDEX_FILE
    ):
        self.kb_dir = Path(kb_dir).resolve()
        self.db_path = Path(db_path).resolve()
        self.index_file = Path(index_file).resolve()

        self.frontmatter = FrontmatterManager(self.kb_dir)
        self.fts = FTSSearchEngine(self.kb_dir, self.db_path)
        self.validator = KBValidator(self.kb_dir, self.index_file)

    def search(self, query: str, category: str = None, topic: str = None, top_k: int = 5):
        return self.fts.search(query=query, category=category, topic=topic, top_k=top_k)

    def format_llm_context(self, results: list) -> str:
        if not results:
            return "No relevant Knowledge Base entries found."

        output = [f"=== Knowledge Base Context ({len(results)} relevant entries) ===\n"]
        for i, r in enumerate(results, 1):
            file_link = f"file://{r['abs_path']}#L{r['start_line']}-L{r['end_line']}"
            output.append(f"[{i}] {r['title']} ({r['category'].upper()})")
            output.append(f"Source Link: [{r['rel_path']}#L{r['start_line']}]({file_link})")
            if r['topics']:
                output.append(f"Topics: {', '.join(r['topics'])}")
            output.append("Excerpt:")
            output.append(r['content'].strip())
            output.append("-" * 50)

        return "\n".join(output)

    def build_index(self) -> int:
        return self.fts.build_index()

    def build_sitemap(self) -> str:
        return self.validator.build_sitemap()

    def validate(self) -> dict:
        return self.validator.validate_health()

    def standardize(self, force: bool = False) -> int:
        count = 0
        for root, _, files in os.walk(self.kb_dir):
            for file in files:
                if file.endswith(".md") and file not in ["INDEX.md", "TAXONOMY.md"]:
                    file_path = Path(root) / file
                    if self.frontmatter.standardize_file(file_path, force=force):
                        count += 1
        return count
