"""Canonical taxonomy access backed by ``Knowledge_base/TAXONOMY.md``."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_TAXONOMY_PATH = PROJECT_ROOT / "Knowledge_base" / "TAXONOMY.md"

_CATEGORY_PATTERN = re.compile(r"^###\s+\d+\.\s+`([^`]+)`\s*$")
_TOPIC_PATTERN = re.compile(r"^\s*-\s+`([^`]+)`(?:\s+\((.*)\))?\s*$")
_SECTION_PATTERN = re.compile(r"^##\s+")


@dataclass(frozen=True, slots=True)
class TopicDefinition:
    """One canonical topic parsed from the taxonomy document."""

    slug: str
    category: str
    summary: str


def _parse_taxonomy(
    content: str,
) -> tuple[list[str], dict[str, str], dict[str, TopicDefinition]]:
    categories: list[str] = []
    category_definitions: dict[str, str] = {}
    topics: dict[str, TopicDefinition] = {}
    current_category: str | None = None

    for line in content.splitlines():
        if _SECTION_PATTERN.match(line):
            current_category = None
            continue

        category_match = _CATEGORY_PATTERN.match(line)
        if category_match:
            current_category = category_match.group(1)
            if current_category in categories:
                raise ValueError(f"Duplicate taxonomy category: {current_category}")
            categories.append(current_category)
            category_definitions[current_category] = ""
            continue

        topic_match = _TOPIC_PATTERN.match(line)
        if not topic_match:
            stripped_line = line.strip()
            if (
                current_category is not None
                and not category_definitions[current_category]
                and stripped_line
                and stripped_line != "- **Topics**:"
            ):
                category_definitions[current_category] = stripped_line
            continue
        if current_category is None:
            continue
        slug, summary = topic_match.groups()
        if slug in topics:
            raise ValueError(f"Duplicate taxonomy topic: {slug}")
        topics[slug] = TopicDefinition(
            slug=slug,
            category=current_category,
            summary=summary or slug,
        )

    return categories, category_definitions, topics


def _read_taxonomy(
    path: Path,
) -> tuple[str, list[str], dict[str, str], dict[str, TopicDefinition]]:
    content = path.read_text(encoding="utf-8")
    categories, category_definitions, topics = _parse_taxonomy(content)
    return content, categories, category_definitions, topics


(
    _CANONICAL_MARKDOWN,
    _CANONICAL_CATEGORIES,
    _CANONICAL_CATEGORY_DEFINITIONS,
    _CANONICAL_TOPICS,
) = _read_taxonomy(CANONICAL_TAXONOMY_PATH)
if not _CANONICAL_CATEGORIES or not _CANONICAL_TOPICS:
    raise RuntimeError("The project canonical taxonomy is empty.")


class TaxonomyRegistry:
    """Read canonical categories, topics, and definitions from Markdown."""

    CATEGORY_MAP: ClassVar[dict[str, str]] = {
        "training": "training",
        "physiology": "physiology",
        "nutrition": "nutrition",
        "planning": "planning",
        "hiit": "training",
        "zone2": "training",
        "strength": "training",
        "metrics": "physiology",
        "testing": "physiology",
        "periodization": "planning",
    }

    TOPIC_MAP: ClassVar[dict[str, str]] = {
        "Short_intervals": "VO2max_and_aerobic_hiit",
        "Long_intervals": "VO2max_and_aerobic_hiit",
        "Decreasing_intervals": "VO2max_and_aerobic_hiit",
        "Fast_start_intervals": "VO2max_and_aerobic_hiit",
        "Aerobic_base": "Zone2_and_endurance_base",
        "Sweet_spot": "Subthreshold_and_tempo",
        "Heavy_torque": "Torque_and_cadence_drills",
        "Unilateral": "Strength_and_resistance_training",
        "Sprint_performance": "Sprint_and_anaerobic_intervals",
        "Cross_training": "Cross_training_and_multisport",
        "Lab_vs_field": "Physiological_testing_and_diagnostics",
        "FTP": "FTP_and_functional_metrics",
        "CP": "Critical_power_and_w_prime",
        "W_prime": "Critical_power_and_w_prime",
        "VO2max": "VO2max_and_aerobic_kinetics",
        "FatMax": "Substrate_utilization_and_fat_oxidation",
        "LT1_VT1": "Thresholds_and_metabolic_domains",
        "LT2_VT2": "Thresholds_and_metabolic_domains",
        "Durability": "Durability_and_fatigue_mechanisms",
        "Power_vs_HR": "Autonomic_and_cardiac_monitoring",
        "Heart_rate_variability": "Autonomic_and_cardiac_monitoring",
        "Cardiac_hypertrophy": "Cardiovascular_and_hemodynamics",
        "Lactate_shuttle": "Lactate_kinetics_and_metabolism",
        "Mitochondrial_density": "Mitochondrial_and_cellular_adaptation",
        "Fat_oxidation": "Substrate_utilization_and_fat_oxidation",
        "Temperature_effects": "Environmental_and_thermal_stress",
        "Carbohydrate_ratio": "Carbohydrate_fueling_and_gut_training",
        "Sodium_bicarbonate": "Ergogenic_supplements_and_buffers",
        "Beta_alanine": "Ergogenic_supplements_and_buffers",
        "Hydration_electrolytes": "Hydration_and_electrolyte_balance",
        "Antioxidants": "Micronutrients_and_biomarkers",
        "Underfueling_REDs": "Energy_availability_and_reds",
        "Ergogenic_aids": "Ergogenic_supplements_and_buffers",
        "Block_periodization": "Periodization_models_and_macrocycles",
        "Double_threshold": "Microcycle_and_schedule_design",
        "Microcycles": "Microcycle_and_schedule_design",
        "Tapering": "Tapering_and_peaking",
        "TTA_TTE": "FTP_and_functional_metrics",
        "Volume_quantification": "Workload_quantification_and_modeling",
        "Periodization": "Periodization_models_and_macrocycles",
        "Progressive_overload": "Periodization_models_and_macrocycles",
    }

    CANONICAL_CATEGORIES: ClassVar[list[str]] = _CANONICAL_CATEGORIES.copy()
    CANONICAL_TOPICS: ClassVar[dict[str, TopicDefinition]] = dict(_CANONICAL_TOPICS)

    def __init__(self, kb_dir: Path | None = None) -> None:
        """Load the selected Knowledge Base taxonomy or the project canonical file."""
        self.kb_dir = kb_dir
        taxonomy_path = kb_dir / "TAXONOMY.md" if kb_dir else CANONICAL_TAXONOMY_PATH
        if not taxonomy_path.is_file():
            taxonomy_path = CANONICAL_TAXONOMY_PATH
        _, categories, category_definitions, topics = _read_taxonomy(taxonomy_path)
        self._categories = categories
        self._category_definitions = category_definitions
        self._topic_definitions = topics
        self._topics_by_category = {
            category: [
                definition.slug
                for definition in topics.values()
                if definition.category == category
            ]
            for category in categories
        }

    def categories(self) -> list[str]:
        """Return canonical categories in document order."""
        return self._categories.copy()

    def topics(self, category: str | None = None) -> list[str]:
        """Return all canonical topics or those belonging to one category."""
        if category is None:
            return list(self._topic_definitions)
        canonical_category = self.normalize_category(category) or category
        return self._topics_by_category.get(canonical_category, []).copy()

    def topic_definition(self, topic: str) -> TopicDefinition | None:
        """Return the canonical definition for a topic slug."""
        return self._topic_definitions.get(topic)

    def category_definition(self, category: str) -> str | None:
        """Return the canonical description for a category slug."""
        return self._category_definitions.get(category) or None

    def category_for_topic(self, topic: str) -> str | None:
        """Return the category containing a canonical topic."""
        definition = self.topic_definition(topic)
        return definition.category if definition else None

    def category_order(self) -> list[str]:
        """Return canonical category order."""
        return self.categories()

    def valid_category(self, category: str) -> bool:
        """Return whether a category or legacy alias resolves canonically."""
        normalized = self.normalize_category(category)
        return normalized in self._categories if normalized else False

    def topic_keywords(self) -> dict[str, list[str]]:
        """Return search phrases derived from canonical topic definitions."""
        return {
            slug: [phrase.strip() for phrase in definition.summary.split(",")]
            for slug, definition in self._topic_definitions.items()
        }

    def category_map(self) -> dict[str, str]:
        """Return legacy-to-canonical category aliases."""
        return self.CATEGORY_MAP.copy()

    def topic_map(self) -> dict[str, str]:
        """Return legacy-to-canonical topic aliases."""
        return self.TOPIC_MAP.copy()

    @classmethod
    def normalize_category(cls, category: str | None) -> str | None:
        """Resolve a category alias to its canonical value."""
        if not category:
            return None
        clean = category.strip()
        return cls.CATEGORY_MAP.get(clean.casefold(), clean)

    @classmethod
    def normalize_topic(cls, topic: str | None) -> str | None:
        """Resolve a legacy topic alias to its canonical value."""
        if not topic:
            return None
        clean = topic.strip()
        direct = cls.TOPIC_MAP.get(clean)
        if direct:
            return direct
        casefolded = clean.casefold()
        for alias, canonical in cls.TOPIC_MAP.items():
            if alias.casefold() == casefolded:
                return canonical
        return clean

    @classmethod
    def generate_taxonomy_markdown(cls, kb_dir: Path | None = None) -> str:
        """Copy the project canonical taxonomy into a temporary Knowledge Base."""
        if kb_dir is not None:
            destination = kb_dir / "TAXONOMY.md"
            if (
                not destination.exists()
                or destination.read_text(encoding="utf-8") != _CANONICAL_MARKDOWN
            ):
                destination.write_text(_CANONICAL_MARKDOWN, encoding="utf-8")
        return _CANONICAL_MARKDOWN
