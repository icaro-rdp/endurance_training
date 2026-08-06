"""
SQLite FTS5 Full-Text Search Engine with BM25 ranking and on-demand auto-indexing.
"""

import os
import re
import json
import sqlite3
from pathlib import Path
from main.kb_engine.frontmatter import FrontmatterManager

class FTSSearchEngine:
    def __init__(self, kb_dir: Path, db_path: Path):
        self.kb_dir = kb_dir
        self.db_path = db_path
        self.fm_manager = FrontmatterManager(kb_dir)

    def is_index_stale(self) -> bool:
        if not self.db_path.exists():
            return True
        db_mtime = self.db_path.stat().st_mtime
        for root, _, files in os.walk(self.kb_dir):
            for file in files:
                if file.endswith(".md") and file not in ["INDEX.md", "TAXONOMY.md"]:
                    f_mtime = (Path(root) / file).stat().st_mtime
                    if f_mtime > db_mtime:
                        return True
        return False

    def build_index(self) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS kb_chunks")
        cursor.execute("DROP TABLE IF EXISTS kb_fts")

        cursor.execute("""
        CREATE TABLE kb_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            category TEXT,
            topics TEXT,
            source TEXT,
            rel_path TEXT,
            abs_path TEXT,
            start_line INTEGER,
            end_line INTEGER,
            content TEXT
        )
        """)

        cursor.execute("""
        CREATE VIRTUAL TABLE kb_fts USING fts5(
            title,
            category,
            topics,
            content,
            content='kb_chunks',
            content_rowid='id'
        )
        """)

        chunk_count = 0
        for root, _, files in os.walk(self.kb_dir):
            for file in files:
                if file.endswith(".md") and file not in ["INDEX.md", "TAXONOMY.md"]:
                    file_path = Path(root) / file
                    fm, body = self.fm_manager.parse_document(file_path)

                    rel_path = str(file_path.relative_to(self.kb_dir))
                    raw_sections = re.split(r"\n(?=##?\s+)", body)
                    line_offset = file_path.read_text(encoding="utf-8", errors="replace").find(body)
                    line_start_base = body[:line_offset].count("\n") + 1 if "---\n" in body else 1

                    line_curr = line_start_base
                    for section in raw_sections:
                        section_str = section.strip()
                        if not section_str:
                            continue
                        
                        start_line = line_curr
                        lines_count = section_str.count("\n") + 1
                        end_line = start_line + lines_count - 1
                        line_curr = end_line + 1

                        cursor.execute("""
                        INSERT INTO kb_chunks (title, category, topics, source, rel_path, abs_path, start_line, end_line, content)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            fm.get("title", file_path.stem),
                            fm.get("category", "general"),
                            json.dumps(fm.get("topics", [])),
                            fm.get("source", ""),
                            rel_path,
                            str(file_path),
                            start_line,
                            end_line,
                            section_str
                        ))
                        chunk_id = cursor.lastrowid
                        cursor.execute("""
                        INSERT INTO kb_fts (rowid, title, category, topics, content)
                        VALUES (?, ?, ?, ?, ?)
                        """, (chunk_id, fm.get("title", file_path.stem), fm.get("category", "general"), json.dumps(fm.get("topics", [])), section_str))
                        chunk_count += 1

        conn.commit()
        conn.close()
        return chunk_count

    def search(self, query: str, category: str = None, topic: str = None, top_k: int = 5):
        if self.is_index_stale():
            self.build_index()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        fts_query = re.sub(r'[^\w\s]', ' ', query).strip()
        if not fts_query:
            fts_tokens = ["*"]
        else:
            fts_tokens = [f'"{token}"' for token in fts_query.split() if len(token) > 1]
        
        fts_match = " OR ".join(fts_tokens) if fts_tokens else "*"

        sql = """
        SELECT c.id, c.title, c.category, c.topics, c.source, c.rel_path, c.abs_path, c.start_line, c.end_line, c.content, bm25(kb_fts) as rank
        FROM kb_fts f
        JOIN kb_chunks c ON f.rowid = c.id
        WHERE kb_fts MATCH ?
        """
        params = [fts_match]

        if category:
            sql += " AND c.category = ?"
            params.append(category)
        if topic:
            sql += " AND c.topics LIKE ?"
            params.append(f"%{topic}%")

        sql += " ORDER BY rank LIMIT ?"
        params.append(top_k)

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "title": row[1],
                "category": row[2],
                "topics": json.loads(row[3]) if row[3] else [],
                "source": row[4],
                "rel_path": row[5],
                "abs_path": row[6],
                "start_line": row[7],
                "end_line": row[8],
                "content": row[9],
                "bm25_score": round(row[10], 4)
            })

        conn.close()
        return results
