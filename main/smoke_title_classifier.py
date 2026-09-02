"""Smoke script to extract Markdown titles and classify them without bodies.

Usage:
    uv run python -m main.smoke_title_classifier
    uv run python -m main.smoke_title_classifier --method hybrid --limit 50
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding

logger = logging.getLogger(__name__)

# Category definitions for semantic embedding matching (3-Pillar Taxonomy)
CATEGORY_PROTOTYPES: dict[str, str] = {
    "training": (
        "training execution interval protocol design workouts sweet spot threshold "
        "VO2max HIIT sprint cadence torque resistance strength squat bike fit pacing "
        "periodization models macrocycles training intensity distribution polarized "
        "pyramidal microcycle schedule design workload quantification TSS CTL ATL TSB "
        "PMC tapering peaking overtraining recovery rest season planning psychology"
    ),
    "physiology": (
        "underlying biological mechanisms cardiovascular cardiac hemodynamics "
        "mitochondria cellular adaptation lactate kinetics threshold critical power "
        "VO2max kinetics durability fatigue diagnostics testing"
    ),
    "nutrition": (
        "nutritional fueling intra-workout carbohydrates hydration electrolytes "
        "energy availability RED-S ergogenic supplements sodium bicarbonate "
        "beta-alanine micronutrients biomarkers diet"
    ),
}

# High-precision keywords for rule-based matching
KEYWORD_RULES: dict[str, list[str]] = {
    "nutrition": [
        "carbohydrate",
        "glucose",
        "fructose",
        "fueling",
        "hydration",
        "electrolyte",
        "bicarbonate",
        "beta-alanine",
        "caffeine",
        "creatine",
        "ketone",
        "antioxidant",
        "supplement",
        "diet",
        "glycogen",
        "red-s",
        "energy availability",
        "nutrition",
    ],
    "physiology": [
        "mitochondria",
        "cardiovascular",
        "cardiac",
        "stroke volume",
        "hemodynamics",
        "lactate",
        "substrate",
        "fat oxidation",
        "fatmax",
        "critical power",
        "w'",
        "w-prime",
        "kinetics",
        "durability",
        "hrv",
        "thermal",
        "hypoxia",
        "metabolic cart",
        "immunology",
    ],
    "training": [
        "interval",
        "hiit",
        "sit",
        "sprint",
        "zone 2",
        "zone 3",
        "sweet spot",
        "over-under",
        "4x8",
        "4x4",
        "30/15",
        "cadence",
        "torque",
        "squat",
        "strength",
        "lifting",
        "pacing",
        "bike fit",
        "aerodynamic",
        "drills",
        "periodiz",
        "macrocycle",
        "microcycle",
        "mesocycle",
        "taper",
        "peaking",
        "schedule",
        "season plan",
        "training plan",
        "polarized",
        "pyramidal",
        "intensity distribution",
        "workload",
        "tss",
        "ctl",
        "atl",
        "tsb",
        "pmc",
        "overtrain",
        "overreach",
        "rest week",
        "recovery week",
        "fitness plateau",
        "psychology",
    ],
}


@dataclass(frozen=True)
class TitleRecord:
    """Metadata and extracted title for a Markdown file."""

    relative_path: str
    title: str
    current_category: str
    current_topics: tuple[str, ...]


@dataclass(frozen=True)
class TitleClassificationResult:
    """Classification outcome for a document title."""

    record: TitleRecord
    predicted_category: str
    confidence: float
    method: str
    scores: dict[str, float]


def extract_title_without_body(
    file_path: Path, max_header_lines: int = 40
) -> tuple[str, str, tuple[str, ...]]:
    """Extract document title, category, and topics without reading file body.

    Args:
        file_path: Path to the Markdown file.
        max_header_lines: Maximum number of initial lines to inspect.

    Returns:
        A tuple of (title, category, topics).
    """
    title = ""
    category = "unknown"
    topics: list[str] = []

    try:
        with file_path.open("r", encoding="utf-8") as handle:
            in_frontmatter = False
            in_topics = False

            for idx, line in enumerate(handle):
                if idx >= max_header_lines:
                    break

                stripped = line.strip()
                if idx == 0 and stripped == "---":
                    in_frontmatter = True
                    continue

                if in_frontmatter and stripped == "---":
                    in_frontmatter = False
                    continue

                if in_frontmatter:
                    if stripped.startswith("title:"):
                        raw = line.split("title:", 1)[1].strip()
                        title = raw.strip("\"'")
                    elif stripped.startswith("category:"):
                        category = line.split("category:", 1)[1].strip().strip("\"'")
                    elif stripped.startswith("topics:"):
                        in_topics = True
                    elif in_topics:
                        if stripped.startswith("-"):
                            topic_val = stripped.lstrip("- ").strip("\"'")
                            if topic_val:
                                topics.append(topic_val)
                        elif stripped and not stripped.startswith("#"):
                            in_topics = False

                elif not title and stripped.startswith("# "):
                    title = stripped[2:].strip()
                    break

    except OSError as err:
        logger.warning("Failed reading file header for %s: %s", file_path, err)

    if not title:
        title = file_path.stem.replace("-", " ").replace("_", " ").title()

    return title, category, tuple(topics)


def collect_kb_titles(kb_dir: Path) -> list[TitleRecord]:
    """Scan knowledge base directory and extract titles from all markdown documents.

    Args:
        kb_dir: Root directory of the knowledge base.

    Returns:
        List of TitleRecord objects.
    """
    records: list[TitleRecord] = []
    ignored_names = {"INDEX.md", "TAXONOMY.md", "README.md"}

    for path in sorted(kb_dir.rglob("*.md")):
        if path.name in ignored_names:
            continue
        rel_path = path.relative_to(kb_dir).as_posix()
        title, category, topics = extract_title_without_body(path)
        records.append(
            TitleRecord(
                relative_path=rel_path,
                title=title,
                current_category=category,
                current_topics=topics,
            )
        )
    return records


class TitleClassifier:
    """Classifies document titles into macro-categories without file bodies."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5") -> None:
        """Initialize classifier and load embedding model."""
        self.categories = ["training", "physiology", "nutrition"]
        self.embedder = TextEmbedding(model_name=model_name)

        cat_texts = [CATEGORY_PROTOTYPES[cat] for cat in self.categories]
        raw_cat_embeddings = list(self.embedder.embed(cat_texts))
        self.cat_embeddings = np.array(
            [emb / np.linalg.norm(emb) for emb in raw_cat_embeddings]
        )

    def classify_by_rules(self, title: str) -> tuple[str | None, float]:
        """Classify title using high-precision domain keywords.

        Args:
            title: Extracted document title.

        Returns:
            Tuple of (category, score) or (None, 0.0) if no rule matches.
        """
        lower = title.lower()
        rule_hits: dict[str, int] = {cat: 0 for cat in self.categories}

        for cat, keywords in KEYWORD_RULES.items():
            for kw in keywords:
                if kw in lower:
                    rule_hits[cat] += 1

        top_cat = max(rule_hits, key=lambda c: rule_hits[c])
        max_hits = rule_hits[top_cat]

        if max_hits > 0:
            return top_cat, min(1.0, 0.6 + 0.15 * max_hits)
        return None, 0.0

    def classify_by_embedding(self, title: str) -> tuple[str, float, dict[str, float]]:
        """Classify title using dense semantic similarity.

        Args:
            title: Extracted document title.

        Returns:
            Tuple of (best_category, confidence, score_map).
        """
        title_emb = list(self.embedder.embed([title]))[0]
        norm_emb = title_emb / np.linalg.norm(title_emb)
        sims = np.dot(self.cat_embeddings, norm_emb)

        scores = {cat: float(sims[idx]) for idx, cat in enumerate(self.categories)}
        best_idx = int(np.argmax(sims))
        best_cat = self.categories[best_idx]
        confidence = float(sims[best_idx])

        return best_cat, confidence, scores

    def classify_title(
        self, record: TitleRecord, method: str = "hybrid"
    ) -> TitleClassificationResult:
        """Assign category to title using specified method.

        Args:
            record: TitleRecord containing title string.
            method: Classification method ('hybrid', 'embedding', or 'rules').

        Returns:
            TitleClassificationResult instance.
        """
        rule_cat, rule_conf = self.classify_by_rules(record.title)
        emb_cat, emb_conf, scores = self.classify_by_embedding(record.title)

        if method == "rules":
            pred_cat = rule_cat or "training"
            conf = rule_conf if rule_cat else 0.25
            return TitleClassificationResult(
                record=record,
                predicted_category=pred_cat,
                confidence=conf,
                method="rules",
                scores=scores,
            )

        if method == "embedding":
            return TitleClassificationResult(
                record=record,
                predicted_category=emb_cat,
                confidence=emb_conf,
                method="embedding",
                scores=scores,
            )

        # Hybrid: rule match has priority if distinct, else semantic embedding
        if rule_cat is not None and rule_conf >= 0.75:
            pred_cat = rule_cat
            conf = rule_conf
            used_method = "rules+hybrid"
        else:
            pred_cat = emb_cat
            conf = emb_conf
            used_method = "embedding+hybrid"

        return TitleClassificationResult(
            record=record,
            predicted_category=pred_cat,
            confidence=conf,
            method=used_method,
            scores=scores,
        )


def run_smoke_test(
    kb_dir: Path, method: str = "hybrid", limit: int | None = None
) -> None:
    """Execute title classification smoke test and print diagnostic reasoning.

    Args:
        kb_dir: Path to Knowledge_base directory.
        method: Method to use ('hybrid', 'embedding', 'rules').
        limit: Optional limit on number of documents to display.
    """
    records = collect_kb_titles(kb_dir)
    if not records:
        print(f"No Markdown records found in {kb_dir}")
        return

    classifier = TitleClassifier()
    results: list[TitleClassificationResult] = []

    print(f"\nExtracted {len(records)} document titles (without loading file bodies).")
    print(f"Classifying titles via method='{method}'...\n")

    for rec in records:
        res = classifier.classify_title(rec, method=method)
        results.append(res)

    # Category counts
    current_dist = Counter(r.current_category for r in records)
    predicted_dist = Counter(r.predicted_category for r in results)

    # Confusion matrix
    matrix: dict[str, dict[str, int]] = defaultdict(lambda: Counter())
    for res in results:
        matrix[res.record.current_category][res.predicted_category] += 1

    cats = ["training", "physiology", "nutrition"]

    print("=" * 70)
    print("📊 CATEGORY DISTRIBUTION COMPARISON (3-PILLAR TAXONOMY)")
    print("=" * 70)
    print(
        f"{'Category':<14} | {'Current in Corpus':<18} | {'Predicted from Title':<20}"
    )
    print("-" * 70)
    for cat in cats:
        curr_val = current_dist.get(cat, 0)
        curr_pct = (curr_val / len(records)) * 100
        pred_val = predicted_dist.get(cat, 0)
        pred_pct = (pred_val / len(records)) * 100
        print(
            f"{cat:<14} | {curr_val:4d} ({curr_pct:5.1f}%)       | "
            f"{pred_val:4d} ({pred_pct:5.1f}%)"
        )
    print("=" * 70)

    print("\n" + "=" * 70)
    print("🔍 CONFUSION MATRIX (Row = Corpus Frontmatter, Column = Title Prediction)")
    print("=" * 70)
    header = f"{'Corpus / Pred':<14} | " + " | ".join(f"{c:<10}" for c in cats)
    print(header)
    print("-" * 70)
    for row_cat in cats:
        row_line = f"{row_cat:<14} | " + " | ".join(
            f"{matrix[row_cat][col_cat]:<10}" for col_cat in cats
        )
        print(row_line)
    print("=" * 70)


def main() -> None:
    """CLI entrypoint for title classification smoke test."""
    parser = argparse.ArgumentParser(
        description="Extract titles without reading bodies and predict categories."
    )
    parser.add_argument(
        "--kb-dir",
        type=Path,
        default=Path("Knowledge_base"),
        help="Path to Knowledge_base root directory.",
    )
    parser.add_argument(
        "--method",
        choices=["hybrid", "embedding", "rules"],
        default="hybrid",
        help="Classification method to employ.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=15,
        help="Number of sample discrepancy titles to print.",
    )

    args = parser.parse_args()
    kb_path = args.kb_dir.resolve()
    if not kb_path.is_dir():
        print(
            f"Error: Knowledge Base directory '{kb_path}' does not exist.",
            file=sys.stderr,
        )
        sys.exit(1)

    run_smoke_test(kb_dir=kb_path, method=args.method, limit=args.limit)


if __name__ == "__main__":
    main()
