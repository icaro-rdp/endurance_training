"""
Unified Deep Facade Class: KBEngine
"""

import os
from pathlib import Path
from main.utils.kb_engine.frontmatter import FrontmatterManager
from main.utils.kb_engine.fts import FTSSearchEngine
from main.utils.kb_engine.validator import KBValidator
from main.utils.kb_engine.taxonomy import TaxonomyRegistry
from main.utils.kb_engine.walker import iter_kb_documents

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
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

        self.taxonomy = TaxonomyRegistry(self.kb_dir)
        self.frontmatter = FrontmatterManager(self.kb_dir, self.taxonomy)
        self.fts = FTSSearchEngine(self.kb_dir, self.db_path, self.taxonomy)
        self.validator = KBValidator(self.kb_dir, self.index_file, self.taxonomy)

    def search(self, query: str, category: str = None, topic: str = None, top_k: int = 5):
        return self.fts.search(query=query, category=category, topic=topic, top_k=top_k)

    def format_llm_context(self, results: list) -> str:
        if not results:
            return "No relevant Knowledge Base entries found."

        output = [f"=== Knowledge Base Context ({len(results)} relevant entries) ===\n"]
        for i, r in enumerate(results, 1):
            abs_path = self.kb_dir / r['rel_path']
            file_link = f"file://{abs_path}#L{r['start_line']}-L{r['end_line']}"
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
        for file_path in iter_kb_documents(self.kb_dir):
            if self.frontmatter.standardize_file(file_path, force=force):
                count += 1
        return count
