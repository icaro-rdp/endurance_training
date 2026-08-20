"""CLI boundary tests for workspace discovery and actionable errors."""

from __future__ import annotations

import contextlib
import hashlib
import io
import tempfile
import unittest
from pathlib import Path

from main.cli import main


class TestKnowledgeBaseCLI(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp_dir.cleanup)
        self.root = Path(self._temp_dir.name)
        self.kb_dir = self.root / "Knowledge_base"
        self.kb_dir.mkdir()
        (self.kb_dir / "TAXONOMY.md").write_text(
            "# Taxonomy\n\n### 1. `physiology`\n  - `VO2max`\n",
            encoding="utf-8",
        )
        (self.kb_dir / "INDEX.md").write_text("# Empty index\n", encoding="utf-8")

    def _write_source(self, body: str = "Evidence body.") -> Path:
        source = self.kb_dir / "Articles" / "source.md"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            """---
title: CLI Source
language: en
category: physiology
topics: [VO2max]
source: Test journal
author: Test Researcher
date: 2026-08-20
summary: A CLI fixture.
---

# CLI Source

"""
            + body,
            encoding="utf-8",
        )
        return source

    def _run(self, *args: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = main(list(args))
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def test_missing_workspace_is_a_domain_error_without_traceback(self) -> None:
        exit_code, _stdout, stderr = self._run(
            "--kb-dir", str(self.root / "missing"), "status"
        )

        self.assertEqual(exit_code, 2)
        self.assertIn("knowledge_base_not_found", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_explicit_workspace_builds_and_reports_real_document_count(self) -> None:
        self._write_source("VO2max evidence for explicit workspace discovery.")
        database = self.root / "passages.sqlite"

        build_code, build_output, build_error = self._run(
            "--kb-dir",
            str(self.kb_dir),
            "--db-path",
            str(database),
            "build-index",
        )
        status_code, status_output, status_error = self._run(
            "--kb-dir",
            str(self.kb_dir),
            "--db-path",
            str(database),
            "status",
        )

        self.assertEqual((build_code, status_code), (0, 0))
        self.assertEqual((build_error, status_error), ("", ""))
        self.assertIn("1 English sources", build_output)
        self.assertIn('"document_count": 1', status_output)
        self.assertIn('"state": "fresh"', status_output)

    def test_targeted_validation_prints_every_warning_for_that_source(self) -> None:
        links = "\n".join(
            f"[Missing {index}](missing-{index}.md)" for index in range(20)
        )
        self._write_source(links)

        exit_code, stdout, stderr = self._run(
            "--kb-dir",
            str(self.kb_dir),
            "validate",
            "--source",
            "Articles/source.md",
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr, "")
        self.assertIn("missing-0.md", stdout)
        self.assertIn("missing-19.md", stdout)
        self.assertNotIn("more warnings", stdout)

    def test_malformed_yaml_build_is_an_actionable_domain_error(self) -> None:
        source = self._write_source()
        source.write_text(
            "---\n- title\n- category\n---\n\nMalformed body.\n",
            encoding="utf-8",
        )

        exit_code, _stdout, stderr = self._run(
            "--kb-dir", str(self.kb_dir), "build-index"
        )

        self.assertEqual(exit_code, 2)
        self.assertIn("invalid_source", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_untyped_category_cannot_publish_over_the_previous_index(self) -> None:
        source = self._write_source()
        database = self.root / "passages.sqlite"
        build_code, _output, _error = self._run(
            "--kb-dir",
            str(self.kb_dir),
            "--db-path",
            str(database),
            "build-index",
        )
        self.assertEqual(build_code, 0)
        original_database = hashlib.sha256(database.read_bytes()).digest()
        source.write_text(
            source.read_text(encoding="utf-8").replace(
                "category: physiology", "category: [physiology]"
            ),
            encoding="utf-8",
        )

        exit_code, _stdout, stderr = self._run(
            "--kb-dir",
            str(self.kb_dir),
            "--db-path",
            str(database),
            "build-index",
        )

        self.assertEqual(exit_code, 2)
        self.assertIn("invalid_source", stderr)
        self.assertEqual(
            hashlib.sha256(database.read_bytes()).digest(), original_database
        )

    def test_index_path_cannot_overwrite_a_knowledge_source(self) -> None:
        source = self._write_source("Source content that must survive.")
        original = source.read_bytes()

        exit_code, _stdout, stderr = self._run(
            "--kb-dir",
            str(self.kb_dir),
            "--db-path",
            str(source),
            "build-index",
        )

        self.assertEqual(exit_code, 2)
        self.assertIn("invalid_index_path", stderr)
        self.assertEqual(source.read_bytes(), original)

    def test_unwritable_index_parent_is_an_actionable_domain_error(self) -> None:
        self._write_source()
        parent_file = self.root / "not-a-directory"
        parent_file.write_text("preserve me", encoding="utf-8")

        exit_code, _stdout, stderr = self._run(
            "--kb-dir",
            str(self.kb_dir),
            "--db-path",
            str(parent_file / "index.sqlite"),
            "build-index",
        )

        self.assertEqual(exit_code, 2)
        self.assertIn("invalid_index_path", stderr)
        self.assertNotIn("Traceback", stderr)
        self.assertEqual(parent_file.read_text(encoding="utf-8"), "preserve me")


if __name__ == "__main__":
    unittest.main()
