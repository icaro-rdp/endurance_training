import re
from pathlib import Path
from typing import Dict, List, Optional

class TaxonomyRegistry:
    CATEGORY_MAP: Dict[str, str] = {
        "hiit": "hiit",
        "metrics": "metrics",
        "nutrition": "nutrition",
        "physiology": "physiology",
        "strength": "strength",
        "training": "periodization",
        "zone2": "zone2",
        "testing": "metrics",
        "planning": "periodization",
        "Books": "book",
    }

    TOPIC_KEYWORDS: Dict[str, List[str]] = {
        "FTP": ["ftp", "functional threshold power"],
        "CP": ["critical power"],
        "W_prime": ["w'", "w prime", "anaerobic work capacity"],
        "VO2max": ["vo2", "vo2max", "maximum oxygen uptake"],
        "FatMax": ["fatmax", "fat oxidation"],
        "LT1_VT1": ["lt1", "vt1", "first threshold", "aerobic threshold"],
        "LT2_VT2": ["lt2", "vt2", "second threshold", "lactate threshold", "mss"],
        "Durability": ["durability", "fatigue resistance"],
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
        "Glucose_fructose": ["glucose", "fructose", "carbohydrate"],
        "Double_threshold": ["double threshold", "norwegian"],
        "Cardiac_hypertrophy": ["cardiac", "stroke volume", "preload", "hypertrophy"],
        "Lactate_shuttle": ["lactate shuttle", "mct1", "mct4"],
    }

    def __init__(self, kb_dir: Path):
        self.kb_dir = kb_dir
        self._categories: List[str] = []
        self._topics_by_category: Dict[str, List[str]] = {}
        self._parse_taxonomy_md()

    def _parse_taxonomy_md(self):
        taxonomy_path = self.kb_dir / "TAXONOMY.md"
        if not taxonomy_path.exists():
            # Fallback if TAXONOMY.md doesn't exist
            return
            
        with open(taxonomy_path, "r", encoding="utf-8") as f:
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
        default_order = ["metrics", "hiit", "zone2", "strength", "nutrition", "physiology", "periodization", "book", "general"]
        for cat in default_order:
            if cat not in self._categories:
                self._categories.append(cat)
                self._topics_by_category[cat] = []
                
        # Reorder to match default_order, preserving any extra parsed categories at the end
        ordered_cats = []
        for cat in default_order:
            if cat in self._categories:
                ordered_cats.append(cat)
        for cat in self._categories:
            if cat not in ordered_cats:
                ordered_cats.append(cat)
        self._categories = ordered_cats

    def categories(self) -> List[str]:
        return self._categories.copy()

    def topics(self, category: Optional[str] = None) -> List[str]:
        if category:
            return self._topics_by_category.get(category, []).copy()
        
        all_topics = []
        for topics in self._topics_by_category.values():
            all_topics.extend(topics)
        return all_topics

    def category_order(self) -> List[str]:
        return self._categories.copy()

    def valid_category(self, cat: str) -> bool:
        return cat in self._categories

    def topic_keywords(self) -> Dict[str, List[str]]:
        return self.TOPIC_KEYWORDS.copy()

    def category_map(self) -> Dict[str, str]:
        return self.CATEGORY_MAP.copy()
