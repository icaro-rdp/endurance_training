import re
from pathlib import Path
from typing import ClassVar

from .synonyms import DOMAIN_SYNONYMS, STOP_WORDS, expand_synonyms, get_domain_synonyms


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

    # Backward-compatible mapping from legacy / sub-protocol slugs to canonical topics
    TOPIC_MAP: ClassVar[dict[str, str]] = {
        # training legacy aliases
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
        # physiology legacy aliases
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
        # nutrition legacy aliases
        "Carbohydrate_ratio": "Carbohydrate_fueling_and_gut_training",
        "Sodium_bicarbonate": "Ergogenic_supplements_and_buffers",
        "Beta_alanine": "Ergogenic_supplements_and_buffers",
        "Hydration_electrolytes": "Hydration_and_electrolyte_balance",
        "Antioxidants": "Micronutrients_and_biomarkers",
        "Underfueling_REDs": "Energy_availability_and_reds",
        "Ergogenic_aids": "Ergogenic_supplements_and_buffers",
        # planning legacy aliases
        "Block_periodization": "Periodization_models_and_macrocycles",
        "Double_threshold": "Microcycle_and_schedule_design",
        "Microcycles": "Microcycle_and_schedule_design",
        "Tapering": "Tapering_and_peaking",
        "TTA_TTE": "FTP_and_functional_metrics",
        "Volume_quantification": "Workload_quantification_and_modeling",
        "Periodization": "Periodization_models_and_macrocycles",
        "Progressive_overload": "Periodization_models_and_macrocycles",
    }

    TOPIC_KEYWORDS: ClassVar[dict[str, list[str]]] = {
        # 1. training (10 topics)
        "Zone2_and_endurance_base": [
            "zone 2", "zone-2", "aerobic base", "base training", "low-intensity training",
            "lit", "base miles", "long slow distance", "lsd", "endurance ride", "easy ride",
            "conversational pace", "aerobic endurance"
        ],
        "Subthreshold_and_tempo": [
            "sweet spot", "sweetspot", "sst", "tempo", "zone 3", "subthreshold",
            "extensive aerobic", "sub-ftp", "aerobic density", "tempo ride"
        ],
        "Threshold_intervals": [
            "threshold intervals", "ftp intervals", "over-unders", "over unders",
            "lactate clearance intervals", "mlss intervals", "threshold repeats",
            "steady state intervals", "2x20", "3x15", "4x10", "threshold progression"
        ],
        "VO2max_and_aerobic_hiit": [
            "vo2max intervals", "hiit", "high intensity interval training", "4x8", "4x4",
            "30/15", "40/20", "ronnestad", "seiler intervals", "short intervals",
            "long intervals", "fast start", "fast-start intervals", "decreasing intervals",
            "severe domain", "aerobic intervals", "microbursts"
        ],
        "Sprint_and_anaerobic_intervals": [
            "sprint training", "sit", "sprint interval training", "rsa",
            "repeated sprint ability", "neuromuscular power", "anaerobic capacity intervals",
            "sprint drills", "microbursts", "peak power", "standing start", "finish sprint"
        ],
        "Strength_and_resistance_training": [
            "strength training", "resistance training", "gym training", "heavy lifting",
            "squat", "deadlift", "unilateral", "bilateral deficit", "bulgarian split squat",
            "concurrent training", "rfd", "rate of force development", "plyometrics",
            "core strength", "weight lifting"
        ],
        "Torque_and_cadence_drills": [
            "heavy torque", "torque training", "low cadence", "sfr", "big gear",
            "pedal force", "cadence drills", "high cadence", "spin-ups", "pedaling efficiency",
            "fixed gear", "stride frequency", "low-rpm"
        ],
        "Pacing_and_execution_dynamics": [
            "pacing", "pacing strategy", "erg mode", "slope mode", "rpe pacing",
            "time trial pacing", "auto-regulation", "flat vs uphill power", "negative split",
            "power distribution", "race pacing", "climbing pacing"
        ],
        "Cross_training_and_multisport": [
            "cross training", "cross-training", "multisport", "triathlon", "brick workout",
            "bike to run", "run to bike", "modality transfer", "swimming", "rowing",
            "xc skiing", "cross country skiing"
        ],
        "Biomechanics_fit_and_equipment": [
            "bike fit", "biomechanics", "aerodynamics", "cda", "rolling resistance",
            "crr", "crank length", "saddle pressure", "tire pressure", "drivetrain efficiency",
            "cleat position", "shoe stiffness", "chain waxing", "stack and reach"
        ],

        # 2. physiology (13 topics)
        "Cardiovascular_and_hemodynamics": [
            "cardiovascular", "stroke volume", "cardiac output", "eccentric hypertrophy",
            "left ventricle", "cardiac preload", "plasma volume", "hemodynamics",
            "capillarization", "blood volume", "frank-starling", "vascular compliance"
        ],
        "Mitochondrial_and_cellular_adaptation": [
            "mitochondria", "mitochondrial biogenesis", "mitochondrial density",
            "pgc-1alpha", "ampk", "camk", "p38 mapk", "citrate synthase",
            "respiratory chain", "fiber type transition", "mtor", "cellular signaling"
        ],
        "Lactate_kinetics_and_metabolism": [
            "lactate shuttle", "lactate kinetics", "mct1", "mct4", "monocarboxylate",
            "lactate clearance", "lactate oxidation", "lactic acid", "lactate turnover",
            "brooks lactate shuttle", "lactate transport"
        ],
        "Substrate_utilization_and_fat_oxidation": [
            "fat oxidation", "substrate oxidation", "lipid metabolism", "beta-oxidation",
            "glycogen sparing", "substrate utilization", "metabolic flexibility", "fatmax",
            "mfo", "cpt-1", "fat/cd36", "lipolysis", "imtg", "lchf", "ketogenic", "keto"
        ],
        "Thresholds_and_metabolic_domains": [
            "lt1", "lt2", "vt1", "vt2", "aerobic threshold", "anaerobic threshold",
            "mlss", "maximal lactate steady state", "rcp", "respiratory compensation point",
            "exercise intensity domains", "obla", "moderate domain", "heavy domain", "severe domain"
        ],
        "Critical_power_and_w_prime": [
            "critical power", "cp", "w'", "w prime", "w_prime", "w prime balance",
            "w_bal", "anaerobic work capacity", "power-duration model", "hyperbolic model",
            "critical speed", "skiba", "monod scherrer"
        ],
        "FTP_and_functional_metrics": [
            "ftp", "functional threshold power", "tte", "tta_tte", "time to exhaustion",
            "power-duration curve", "mmp", "mean maximal power", "fractional utilization",
            "coggan ftp", "power profile", "hour power", "sustainable power"
        ],
        "VO2max_and_aerobic_kinetics": [
            "vo2max", "maximal oxygen uptake", "vo2 kinetics", "vo2 slow component",
            "oxygen uptake", "map", "maximal aerobic power", "peak oxygen uptake",
            "aerobic capacity", "tau kinetics", "oxygen deficit"
        ],
        "Durability_and_fatigue_mechanisms": [
            "durability", "fatigue resistance", "neuromuscular fatigue", "central fatigue",
            "peripheral fatigue", "henneman size principle", "motor unit recruitment",
            "late-ride power", "kj accumulation", "stamina", "eimd", "muscle damage"
        ],
        "Autonomic_and_cardiac_monitoring": [
            "hrv", "heart rate variability", "rmssd", "sdnn", "autonomic nervous system",
            "vagal tone", "cardiovascular drift", "aerobic decoupling", "power vs hr",
            "efficiency factor", "resting heart rate", "readiness", "orthostatic test"
        ],
        "Environmental_and_thermal_stress": [
            "heat stress", "temperature effects", "thermoregulation", "heat acclimation",
            "core temperature", "sweat rate physiology", "altitude", "hypoxia",
            "acclimatization", "cold stress", "environmental physiology", "epo", "hif-1alpha"
        ],
        "Physiological_testing_and_diagnostics": [
            "physiological testing", "lab testing", "field testing", "metabolic cart",
            "fatmax testing", "lactate testing", "lactate step test", "ramp test",
            "20-minute test", "nirs", "smo2", "muscle oxygenation", "zone calibration",
            "lab vs field", "dmax"
        ],
        "Athlete_health_and_exercise_immunology": [
            "exercise immunology", "illness", "immune system", "return to play",
            "afib", "atrial fibrillation", "cardiac safety", "troponin", "menstrual cycle",
            "female athlete physiology", "perimenopause", "bone mineral density", "neck check", "urti"
        ],

        # 3. nutrition (6 topics)
        "Carbohydrate_fueling_and_gut_training": [
            "carbohydrate fueling", "carbohydrate_ratio", "intra-workout fueling",
            "carbs per hour", "glucose fructose ratio", "1:0.8", "2:1", "sglt1",
            "glut5", "gut training", "gastric emptying", "energy gels", "hydrogel",
            "maurten", "drink mix", "fueling rate"
        ],
        "Daily_macronutrient_and_energy_periodization": [
            "macronutrient periodization", "fuel for the work required", "carbohydrate periodization",
            "train low", "sleep low", "protein requirements", "protein timing",
            "carbohydrate loading", "carb loading", "daily nutrition", "dietary fat", "mps", "leucine"
        ],
        "Hydration_and_electrolyte_balance": [
            "hydration", "electrolytes", "hydration_electrolytes", "sodium loss",
            "sweat sodium", "fluid replacement", "sweat rate", "hyponatremia",
            "rehydration", "dehydration", "isotonic", "electrolyte drinks", "hypotonic"
        ],
        "Energy_availability_and_reds": [
            "red-s", "reds", "underfueling_reds", "low energy availability", "lea",
            "underfueling", "relative energy deficiency", "female athlete triad",
            "amenorrhea", "endocrine suppression", "energy availability"
        ],
        "Ergogenic_supplements_and_buffers": [
            "ergogenic aids", "ergogenic_aids", "supplements", "sodium_bicarbonate",
            "sodium bicarbonate", "bicarb", "beta_alanine", "beta alanine", "carnosine",
            "caffeine", "nitrates", "beetroot juice", "creatine", "ketone esters",
            "exogenous ketones", "bicarbonate"
        ],
        "Micronutrients_and_biomarkers": [
            "micronutrients", "antioxidants", "antioxidant", "ferritin", "iron deficiency",
            "hepcidin", "anemia", "vitamin d", "vitamin c", "vitamin e", "polyphenols",
            "blood biomarkers", "blunting adaptations", "calcium", "magnesium"
        ],

        # 4. planning (7 topics)
        "Periodization_models_and_macrocycles": [
            "periodization", "block_periodization", "progressive_overload", "macrocycle",
            "mesocycle", "annual plan", "atp", "block periodization", "linear periodization",
            "reverse periodization", "base build peak", "phase potentiation", "overload progression"
        ],
        "Training_intensity_distribution": [
            "training intensity distribution", "tid", "polarized training", "polarized model",
            "80/20", "pyramidal training", "threshold model", "seiler tid",
            "intensity distribution", "hvlit", "time in zone"
        ],
        "Microcycle_and_schedule_design": [
            "microcycles", "double_threshold", "microcycle", "weekly schedule",
            "weekly plan", "double threshold", "norwegian method", "two sessions per day",
            "recovery week", "deload week", "session sequencing", "rest day"
        ],
        "Workload_quantification_and_modeling": [
            "volume_quantification", "training load", "tss", "training stress score",
            "ctl", "atl", "tsb", "fitness and fatigue", "performance management chart",
            "pmc", "normalized power", "np", "intensity factor", "if", "banister model",
            "trimp", "kilojoules", "srpe"
        ],
        "Tapering_and_peaking": [
            "tapering", "taper", "peaking", "pre-race taper", "supercompensation",
            "race preparation", "openers", "volume reduction", "mujika taper", "peak readiness"
        ],
        "Overtraining_and_recovery_management": [
            "overtraining", "overtraining syndrome", "ots", "overreaching", "for",
            "nfor", "recovery management", "sleep", "sleep hygiene",
            "parasympathetic overtraining", "sympathetic overtraining", "burnout",
            "systemic recovery", "cold water immersion", "active recovery"
        ],
        "Psychology_and_cognitive_performance": [
            "sports psychology", "psychology", "rpe governor", "psychobiological model",
            "marcora", "mental fatigue", "cognitive resilience", "act training",
            "suffering tolerance", "perceived exertion", "cognitive control", "self-regulation"
        ],
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
            canonical_cat = self.normalize_category(category) or category
            return self._topics_by_category.get(canonical_cat, []).copy()

        all_topics = []
        for topics in self._topics_by_category.values():
            all_topics.extend(topics)
        return all_topics

    def category_order(self) -> list[str]:
        return self._categories.copy()

    def valid_category(self, cat: str) -> bool:
        norm = self.normalize_category(cat)
        return norm in self._categories if norm else False

    def topic_keywords(self) -> dict[str, list[str]]:
        return self.TOPIC_KEYWORDS.copy()

    def category_map(self) -> dict[str, str]:
        return self.CATEGORY_MAP.copy()

    def topic_map(self) -> dict[str, str]:
        return self.TOPIC_MAP.copy()

    @classmethod
    def normalize_category(cls, cat: str | None) -> str | None:
        """Resolve any category alias or variant to its canonical 4-pillar name."""
        if not cat:
            return None
        clean = cat.lower().strip()
        return cls.CATEGORY_MAP.get(clean, cat)

    @classmethod
    def normalize_topic(cls, topic: str | None) -> str | None:
        """Resolve legacy topic slugs or aliases to their canonical topic name."""
        if not topic:
            return None
        clean = topic.strip()
        # Direct lookup in TOPIC_MAP
        if clean in cls.TOPIC_MAP:
            return cls.TOPIC_MAP[clean]
        # Case-insensitive / formatted lookup
        clean_lower = clean.lower()
        for k, v in cls.TOPIC_MAP.items():
            if k.lower() == clean_lower:
                return v
        return clean

