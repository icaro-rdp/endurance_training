import re
from pathlib import Path
from typing import ClassVar


class TaxonomyRegistry:
    CATEGORY_MAP: ClassVar[dict[str, str]] = {
        "hiit": "hiit",
        "metrics": "metrics",
        "nutrition": "nutrition",
        "physiology": "physiology",
        "strength": "strength",
        "training": "periodization",
        "zone2": "zone2",
        "testing": "metrics",
        "planning": "periodization",
    }

    TOPIC_KEYWORDS: ClassVar[dict[str, list[str]]] = {
        "FTP": ["ftp", "functional threshold power"],
        "CP": ["critical power"],
        "W_prime": ["w'", "w prime", "anaerobic work capacity"],
        "VO2max": ["vo2", "vo2max", "maximum oxygen uptake"],
        "FatMax": ["fatmax", "fat oxidation"],
        "LT1_VT1": ["lt1", "vt1", "first threshold", "aerobic threshold"],
        "LT2_VT2": ["lt2", "vt2", "second threshold", "lactate threshold", "mss"],
        "Durability": ["durability", "fatigue resistance"],
        "Power_vs_HR": [
            "power vs hr",
            "power vs heart rate",
            "decoupling",
            "drift",
            "aerobic decoupling",
            "power-hr",
            "flat vs uphill",
        ],
        "Heart_rate_variability": [
            "hrv",
            "heart rate variability",
            "rmssd",
            "sdnn",
            "autonomic",
        ],
        "Short_intervals": ["30s", "short interval", "short-interval", "intermittent"],
        "Long_intervals": ["4x8", "4x4", "4x16", "long interval"],
        "Decreasing_intervals": ["decreasing", "front-loaded"],
        "Fast_start_intervals": ["fast start", "fast-start"],
        "Aerobic_base": ["aerobic base", "base training", "zone 2", "zone-2"],
        "Mitochondrial_density": ["mitochondria", "mitochondrial"],
        "Heavy_torque": ["torque", "low cadence", "low-cadence"],
        "Periodization": ["periodization", "block", "microcycle"],
        "Unilateral": ["unilateral", "single leg", "single-leg"],
        "Sodium_bicarbonate": ["bicarbonate", "sodium bicarbonate", "bicarb"],
        "Beta_alanine": ["beta alanine", "beta-alanine"],
        "Carbohydrate_ratio": ["glucose", "fructose", "carbohydrate"],
        "Underfueling_REDs": [
            "underfueling",
            "red-s",
            "reds",
            "low energy availability",
            "lea",
            "relative energy deficiency",
        ],
        "Ergogenic_aids": [
            "ergogenic",
            "creatine",
            "caffeine",
            "nitrate",
            "bicarbonate",
            "supplement",
        ],
        "Double_threshold": ["double threshold", "norwegian"],
        "Cross_training": [
            "cross training",
            "cross-training",
            "cross_training",
            "crosstraining",
            "cross train",
            "modality transfer",
            "mode specificity",
            "run-cycle",
            "bike vs run",
        ],
        "Cardiac_hypertrophy": ["cardiac", "stroke volume", "preload", "hypertrophy"],
        "Lactate_shuttle": ["lactate shuttle", "mct1", "mct4"],
    }

    def __init__(self, kb_dir: Path):
        self.kb_dir = kb_dir
        self._categories: list[str] = []
        self._topics_by_category: dict[str, list[str]] = {}
        self._parse_taxonomy_md()

    def _parse_taxonomy_md(self) -> None:
        taxonomy_path = self.kb_dir / "TAXONOMY.md"
        if not taxonomy_path.exists():
            # Fallback if TAXONOMY.md doesn't exist
            return

        with open(taxonomy_path, encoding="utf-8") as f:
            content = f.read()

        current_category = None

        for line in content.splitlines():
            cat_match = re.match(r"^### \d+\.\s+`([^`]+)`", line)
            if cat_match:
                current_category = cat_match.group(1)
                self._categories.append(current_category)
                self._topics_by_category[current_category] = []
                continue

            topic_match = re.match(r"^\s+-\s+`([^`]+)`", line)
            if topic_match and current_category:
                topic = topic_match.group(1)
                self._topics_by_category[current_category].append(topic)

        # Additionally add categories from schema guidelines or default ones
        # Based on valid_categories list from validator.py
        default_order = [
            "metrics",
            "hiit",
            "zone2",
            "strength",
            "nutrition",
            "physiology",
            "periodization",
        ]
        for cat in default_order:
            if cat not in self._categories:
                self._categories.append(cat)
                self._topics_by_category[cat] = []

        # Preserve parsed categories that are not part of the default order.
        ordered_cats = []
        for cat in default_order:
            if cat in self._categories:
                ordered_cats.append(cat)
        for cat in self._categories:
            if cat not in ordered_cats:
                ordered_cats.append(cat)
        self._categories = ordered_cats

    def categories(self) -> list[str]:
        return self._categories.copy()

    def topics(self, category: str | None = None) -> list[str]:
        if category:
            return self._topics_by_category.get(category, []).copy()

        all_topics = []
        for topics in self._topics_by_category.values():
            all_topics.extend(topics)
        return all_topics

    def category_order(self) -> list[str]:
        return self._categories.copy()

    def valid_category(self, cat: str) -> bool:
        return cat in self._categories

    def topic_keywords(self) -> dict[str, list[str]]:
        return self.TOPIC_KEYWORDS.copy()

    def category_map(self) -> dict[str, str]:
        return self.CATEGORY_MAP.copy()
