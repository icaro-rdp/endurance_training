"""
Interactive Mass Auto-Tagging and Bottom-Up Category Reorganization Script.
Run directly via: uv run main/tag_kb_contents.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from tqdm import tqdm

from main.utils.kb_engine.classifier import LocalLLMClassifier, MLXAdapter
from main.utils.kb_engine.engine import KBEngine
from main.utils.kb_engine.errors import InvalidKnowledgeSourceError, KBEngineError
from main.utils.kb_engine.frontmatter import KnowledgeSource
from main.utils.kb_engine.taxonomy import TaxonomyRegistry

# ---------------------------------------------------------------------------
# MANUAL BATCH SCOPE — edit these folder names before running the script.
# Paths are relative to Knowledge_base. Raw transcripts must remain excluded.
# ---------------------------------------------------------------------------
FOLDERS_TO_PROCESS = [
    # "Articles",
    # "Episodes",
    "WIP",
]

FOLDERS_TO_SKIP = {
    "raw_transcripts",
    "_summary",
}

FILES_TO_SKIP = {
    "INDEX.md",
    "TAXONOMY.md",
}

# Batch report values are heterogeneous JSON-compatible scalars and collections.
ReportRow = dict[str, Any]


def discover_documents(kb_dir: Path) -> tuple[Path, ...]:
    """Return configured Markdown sources while pruning excluded subtrees."""
    resolved_kb_dir = kb_dir.resolve()
    discovered: set[Path] = set()

    for folder_name in FOLDERS_TO_PROCESS:
        configured_root = (resolved_kb_dir / folder_name).resolve()
        try:
            configured_root.relative_to(resolved_kb_dir)
        except ValueError as error:
            raise ValueError(
                f"Configured folder resolves outside Knowledge_base: {folder_name}"
            ) from error
        if not configured_root.is_dir():
            raise FileNotFoundError(
                f"Configured Knowledge Base folder does not exist: {folder_name}"
            )

        for root, directories, filenames in os.walk(configured_root):
            directories[:] = sorted(
                directory
                for directory in directories
                if directory not in FOLDERS_TO_SKIP and not directory.startswith(".")
            )
            for filename in sorted(filenames):
                if filename.endswith(".md") and filename not in FILES_TO_SKIP:
                    discovered.add(Path(root) / filename)

    return tuple(sorted(discovered))


def get_clean_filename(filename: str, source_group: str) -> str:
    """Strip redundant category/subfolder prefixes from filename."""
    if source_group == "knowledgeIsWatts":
        # Disambiguate collections with similar names
        if filename in {
            "hiit-infographics-collection.md",
            "hiit-infographics-collection-feb2025.md",
            "strength-infographics-collection.md",
        }:
            return filename
        clean = re.sub(
            r"^(?:hiit|metrics|nutrition|physiology|strength|training|zone2)-",
            "",
            filename,
        )
        return clean
    return filename


def clean_empty_dirs(root_dir: Path) -> None:
    """Remove empty subdirectories bottom-up, preserving excluded directories."""
    for dirpath, _dirnames, _filenames in os.walk(root_dir, topdown=False):
        p = Path(dirpath)
        if p == root_dir or any(part in FOLDERS_TO_SKIP for part in p.parts):
            continue
        try:
            if not any(p.iterdir()):
                p.rmdir()
        except OSError:
            pass


def main() -> None:
    """Reprocess configured Knowledge Base folders with the local classifier."""
    kb_dir = Path("Knowledge_base").resolve()
    if not kb_dir.is_dir():
        print(f"Error: Knowledge_base directory not found at {kb_dir}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("🚀 Knowledge Base Mass Auto-Tagger & Reorganizer")
    print("   Engine: MLX Metal GPU (mlx-community/Qwen2.5-7B-Instruct-4bit)")
    print("=" * 70 + "\n")

    taxonomy = TaxonomyRegistry(kb_dir)
    adapter = MLXAdapter()
    classifier = LocalLLMClassifier(adapter=adapter, taxonomy=taxonomy, kb_dir=kb_dir)

    docs = list(discover_documents(kb_dir))
    total_docs = len(docs)
    print(f"Folders to process: {', '.join(FOLDERS_TO_PROCESS)}")
    print(f"Folders always skipped: {', '.join(sorted(FOLDERS_TO_SKIP))}")
    print(f"Found {total_docs} Markdown documents to process.\n")

    path_mapping: dict[str, str] = {}
    results_summary: list[ReportRow] = []
    skipped_docs: list[tuple[str, str]] = []

    start_all = time.perf_counter()

    with tqdm(
        total=total_docs,
        desc="Classifying & Organizing",
        unit="doc",
        dynamic_ncols=True,
    ) as pbar:
        for idx, doc_path in enumerate(docs, start=1):
            old_rel = doc_path.relative_to(kb_dir).as_posix()
            parts = doc_path.relative_to(kb_dir).parts
            if len(parts) < 3:
                skipped_docs.append(
                    (old_rel, "expected <collection>/<source-group>/<document>.md")
                )
                pbar.update(1)
                continue
            top_group = parts[0]
            source_group = parts[1]

            t0 = time.perf_counter()
            try:
                source = KnowledgeSource.from_path(doc_path, kb_dir, taxonomy)
                res = classifier.classify_source(source)

                # Update metadata
                source.update_metadata(
                    category=res.category,
                    topics=res.topics,
                    summary=res.summary,
                )

                # Compute new clean path
                clean_name = get_clean_filename(doc_path.name, source_group)
                new_rel_path = (
                    Path(top_group) / source_group / res.category / clean_name
                )
                new_full_path = kb_dir / new_rel_path

                if (
                    new_full_path.exists()
                    and new_full_path.resolve() != doc_path.resolve()
                ):
                    raise InvalidKnowledgeSourceError(
                        old_rel,
                        f"destination already exists: {new_rel_path.as_posix()}",
                    )

                source.save(target_path=new_full_path)

                if new_full_path.resolve() != doc_path.resolve():
                    doc_path.unlink()

                elapsed = time.perf_counter() - t0
                path_mapping[old_rel] = new_rel_path.as_posix()

                results_summary.append(
                    {
                        "old_path": old_rel,
                        "new_path": new_rel_path.as_posix(),
                        "title": source.title,
                        "category": res.category,
                        "topics": res.topics,
                        "summary": res.summary,
                        "confidence": res.confidence_score,
                        "elapsed_sec": round(elapsed, 2),
                    }
                )

                tqdm.write(
                    f"[{idx}/{total_docs}] ({elapsed:.1f}s) {source.title[:45]}..\n"
                    f"   📂 {old_rel} -> {new_rel_path.as_posix()}\n"
                    f"   🏷️  [{res.category}] {', '.join(res.topics[:4])}\n"
                    f"   📝 {res.summary[:90]}...\n"
                )

            except (KBEngineError, OSError, ValidationError, ValueError) as exc:
                skipped_docs.append((old_rel, str(exc)))
                tqdm.write(f"⚠️  [Skipped/Invalid] {old_rel}: {exc}\n")

            pbar.update(1)

    # Clean up empty directories
    clean_empty_dirs(kb_dir)

    total_elapsed = time.perf_counter() - start_all
    print("\n" + "=" * 70)
    print(
        f"✅ Tagging Finished: {len(results_summary)}/{total_docs} "
        f"documents processed in {total_elapsed:.1f}s"
    )
    if skipped_docs:
        print(
            f"⚠️  {len(skipped_docs)} documents skipped due to validation "
            "(preserved for review):"
        )
        for p, err in skipped_docs:
            print(f"   - {p}: {err}")
    print("=" * 70 + "\n")

    # Save mapping report
    report_file = kb_dir.parent / "main" / ".migration_path_mapping.json"
    report_file.write_text(
        json.dumps(
            {
                "total_processed": len(results_summary),
                "total_skipped": len(skipped_docs),
                "total_seconds": round(total_elapsed, 1),
                "path_mapping": path_mapping,
                "skipped": [{"path": p, "error": e} for p, e in skipped_docs],
                "details": results_summary,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Saved path migration mapping to: {report_file.name}")

    # Rebuild Index & Sitemap
    print("\n🔄 Rebuilding Derived Index and Sitemap (INDEX.md)...")
    engine = KBEngine(kb_dir)
    engine.build_sitemap()
    status = engine.build_index()
    print(
        f"   Synchronized {status.passage_count} evidence passages from "
        f"{status.document_count} sources."
    )

    # Validate
    print("\n🔍 Validating Knowledge Base Schema & Taxonomy...")
    report = engine.validate()
    if report["is_healthy"]:
        print("   Zero errors found! Corpus is fully compliant with Taxonomy.")
    else:
        print(f"   Found {len(report['errors'])} validation warnings/errors:")
        for err in report["errors"]:
            print(f"   - {err}")

    # Category Breakdown Summary
    cat_counts: dict[str, int] = {}
    for item in results_summary:
        cat_counts[item["category"]] = cat_counts.get(item["category"], 0) + 1

    print("\n📊 Final Macro-Category Distribution:")
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        pct = (count / max(len(results_summary), 1)) * 100
        print(f"   - {cat:<12}: {count:3d} documents ({pct:.1f}%)")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
