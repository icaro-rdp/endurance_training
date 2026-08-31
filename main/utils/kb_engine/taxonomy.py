import re
from pathlib import Path
from typing import ClassVar


class TaxonomyRegistry:
    CATEGORY_MAP: ClassVar[dict[str, str]] = {
        "training": "training",
        "physiology": "physiology",
        "nutrition": "nutrition",
        "planning": "planning",
        # Legacy aliases
        "hiit": "training",
        "zone2": "training",
        "strength": "training",
        "metrics": "physiology",
        "testing": "physiology",
        "periodization": "planning",
    }

    TOPIC_KEYWORDS: ClassVar[dict[str, list[str]]] = {
        # training
        "Short_intervals": ["30s", "short interval", "short-interval", "30/15", "40/20", "30/30", "tabata", "ronnestad", "intermittent"],
        "Long_intervals": ["4x8", "4x4", "4x16", "5x5", "seiler", "long interval", "aerobic interval", "threshold interval"],
        "Decreasing_intervals": ["decreasing", "front-loaded", "descending interval"],
        "Fast_start_intervals": ["fast start", "fast-start", "hard start", "hard-start"],
        "Progressive_overload": ["progressive overload", "interval progression", "overload", "progression"],
        "Aerobic_base": ["aerobic base", "base training", "zone 2", "zone-2", "low-intensity training", "lit", "base miles", "long slow distance", "lsd"],
        "Sweet_spot": ["sweet spot", "sweetspot", "tempo", "sst"],
        "Heavy_torque": ["torque", "low cadence", "low-cadence", "big gear", "sfr", "pedal force"],
        "Unilateral": ["unilateral", "single leg", "single-leg", "split squat", "bulgarian split squat"],
        "Sprint_performance": ["sprint", "sprint performance", "neuromuscular power", "peak power", "rate of force development", "rfd"],
        "Cross_training": ["cross training", "cross-training", "cross_training", "crosstraining", "modality transfer", "run vs bike", "bike vs run", "triathlon"],
        "Lab_vs_field": ["lab vs field", "metabolic cart", "lactate meter", "field testing", "determining zone 2"],
        # physiology
        "FTP": ["ftp", "functional threshold power", "hour power", "20-minute test"],
        "CP": ["critical power", "power-duration", "cp model"],
        "W_prime": ["w'", "w prime", "w_prime", "anaerobic work capacity", "anaerobic capacity"],
        "VO2max": ["vo2", "vo2max", "vo2 max", "maximum oxygen uptake", "maximal oxygen uptake", "peak aerobic power", "aerobic capacity"],
        "FatMax": ["fatmax", "fat max", "maximal fat oxidation", "peak fat oxidation", "mfo"],
        "LT1_VT1": ["lt1", "vt1", "first threshold", "first lactate threshold", "first ventilatory threshold", "aerobic threshold", "talk test"],
        "LT2_VT2": ["lt2", "vt2", "second threshold", "second lactate threshold", "second ventilatory threshold", "anaerobic threshold", "mss", "mlss", "obla"],
        "Durability": ["durability", "fatigue resistance", "stamina", "power degradation", "late-ride"],
        "Power_vs_HR": ["power vs hr", "power vs heart rate", "decoupling", "drift", "aerobic decoupling", "power-hr", "flat vs uphill", "cardiac drift", "efficiency factor"],
        "Heart_rate_variability": ["hrv", "heart rate variability", "rmssd", "sdnn", "autonomic", "vagal tone", "readiness score"],
        "Cardiac_hypertrophy": ["cardiac", "stroke volume", "preload", "hypertrophy", "cardiac output", "left ventricle"],
        "Lactate_shuttle": ["lactate shuttle", "mct1", "mct4", "monocarboxylate", "lactate clearance", "lactate kinetics"],
        "Mitochondrial_density": ["mitochondria", "mitochondrial", "mitochondrial biogenesis", "pgc-1alpha", "capillarization", "capillary density", "citrate synthase"],
        "Fat_oxidation": ["fat oxidation", "fat burning", "lipid metabolism", "glycogen sparing", "substrate utilization", "lchf", "ketogenic", "keto"],
        "Temperature_effects": ["heat", "temperature", "heat stress", "heat acclimation", "thermoregulation", "sweat rate", "cramp", "cramping", "core temp", "saddle sore"],
        # nutrition
        "Sodium_bicarbonate": ["bicarbonate", "sodium bicarbonate", "bicarb", "maurten bicarb"],
        "Beta_alanine": ["beta alanine", "beta-alanine", "carnosine"],
        "Carbohydrate_ratio": ["glucose", "fructose", "carbohydrate", "carbs per hour", "fueling", "gut training", "intra-workout fueling"],
        "Hydration_electrolytes": ["hydration", "electrolyte", "electrolytes", "fluid balance", "sodium loss", "sweat sodium"],
        "Antioxidants": ["antioxidant", "antioxidants", "vitamin c", "vitamin e", "polyphenols", "blunting adaptation"],
        "Underfueling_REDs": ["underfueling", "red-s", "reds", "low energy availability", "lea", "relative energy deficiency", "female athlete triad"],
        "Ergogenic_aids": ["ergogenic", "creatine", "caffeine", "nitrate", "beetroot", "supplement", "supplements"],
        # planning
        "Block_periodization": ["block periodization", "block training", "concentrated loading", "shock block", "training block", "hit block"],
        "Double_threshold": ["double threshold", "norwegian", "norwegian method", "two sessions per day", "subthreshold", "ingebrigtsen"],
        "Microcycles": ["microcycle", "microcycles", "weekly structure", "weekly plan", "recovery week", "rest day", "sleep", "recovery", "deload"],
        "Tapering": ["taper", "tapering", "pre-race taper", "peaking"],
        "TTA_TTE": ["tte", "time to exhaustion", "time-to-exhaustion", "tta", "sustaining power"],
        "Volume_quantification": ["tss", "training stress score", "kilojoules", "training load", "ctl", "atl", "tsb", "volume quantification", "workload"],
        "Periodization": ["periodization", "annual plan", "macrocycle", "mesocycle", "training phase", "base build peak"],
    }

    def __init__(self, kb_dir: Path):
        self.kb_dir = kb_dir
        self._categories: list[str] = []
        self._topics_by_category: dict[str, list[str]] = {}
        self._parse_taxonomy_md()

    def _parse_taxonomy_md(self) -> None:
        taxonomy_path = self.kb_dir / "TAXONOMY.md"
        if not taxonomy_path.exists():
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

        default_order = [
            "training",
            "physiology",
            "nutrition",
            "planning",
        ]
        for cat in default_order:
            if cat not in self._categories:
                self._categories.append(cat)
                self._topics_by_category[cat] = []

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
