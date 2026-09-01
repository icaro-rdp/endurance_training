from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from .synonyms import DOMAIN_SYNONYMS, STOP_WORDS, expand_synonyms, get_domain_synonyms


@dataclass(frozen=True, slots=True)
class TopicDefinition:
    slug: str
    category: str
    summary: str
    inclusions: tuple[str, ...] = ()
    exclusions: tuple[str, ...] = ()
    synonyms: tuple[str, ...] = ()


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

    CANONICAL_TOPICS: ClassVar[dict[str, TopicDefinition]] = {
        # 1. training (10 topics)
        "Zone2_and_endurance_base": TopicDefinition(
            slug="Zone2_and_endurance_base",
            category="training",
            summary="Low-intensity continuous endurance training volume, Zone 2, LIT, LSD, base miles",
            synonyms=("zone 2", "zone-2", "aerobic base", "base training", "low-intensity training", "lit", "base miles", "long slow distance", "lsd", "endurance ride", "easy ride", "conversational pace", "aerobic endurance"),
        ),
        "Subthreshold_and_tempo": TopicDefinition(
            slug="Subthreshold_and_tempo",
            category="training",
            summary="Sweet Spot 88-94% FTP, Zone 3 tempo, extensive aerobic density",
            synonyms=("sweet spot", "sweetspot", "sst", "tempo", "zone 3", "subthreshold", "extensive aerobic", "sub-ftp", "aerobic density", "tempo ride"),
        ),
        "Threshold_intervals": TopicDefinition(
            slug="Threshold_intervals",
            category="training",
            summary="Over-unders, 2x20m, threshold repeats, sustained FTP intervals, lactate clearance",
            synonyms=("threshold intervals", "ftp intervals", "over-unders", "over unders", "lactate clearance intervals", "mlss intervals", "threshold repeats", "steady state intervals", "2x20", "3x15", "4x10", "threshold progression"),
        ),
        "VO2max_and_aerobic_hiit": TopicDefinition(
            slug="VO2max_and_aerobic_hiit",
            category="training",
            summary="Seiler 4x8/4x4, Ronnestad 30/15, fast-start HIIT, decreasing intervals, severe domain intervals",
            synonyms=("vo2max intervals", "hiit", "high intensity interval training", "4x8", "4x4", "30/15", "40/20", "ronnestad", "seiler intervals", "short intervals", "long intervals", "fast start", "fast-start intervals", "decreasing intervals", "severe domain", "aerobic intervals", "microbursts"),
        ),
        "Sprint_and_anaerobic_intervals": TopicDefinition(
            slug="Sprint_and_anaerobic_intervals",
            category="training",
            summary="Sprint Interval Training SIT 15-30s, repeated sprint ability RSA, microbursts",
            synonyms=("sprint training", "sit", "sprint interval training", "rsa", "repeated sprint ability", "neuromuscular power", "anaerobic capacity intervals", "sprint drills", "microbursts", "peak power", "standing start", "finish sprint"),
        ),
        "Strength_and_resistance_training": TopicDefinition(
            slug="Strength_and_resistance_training",
            category="training",
            summary="Gym heavy resistance training, squats, deadlifts, unilateral/bilateral, concurrent training",
            synonyms=("strength training", "resistance training", "gym training", "heavy lifting", "squat", "deadlift", "unilateral", "bilateral deficit", "bulgarian split squat", "concurrent training", "rfd", "rate of force development", "plyometrics", "core strength", "weight lifting"),
        ),
        "Torque_and_cadence_drills": TopicDefinition(
            slug="Torque_and_cadence_drills",
            category="training",
            summary="Low-cadence torque efforts, SFR, high-cadence spin-ups, neuromuscular pedaling drills",
            synonyms=("heavy torque", "torque training", "low cadence", "sfr", "big gear", "pedal force", "cadence drills", "high cadence", "spin-ups", "pedaling efficiency", "fixed gear", "stride frequency", "low-rpm"),
        ),
        "Pacing_and_execution_dynamics": TopicDefinition(
            slug="Pacing_and_execution_dynamics",
            category="training",
            summary="Pacing tactics, ERG vs slope mode, RPE auto-regulation, TT/climb power distribution",
            synonyms=("pacing", "pacing strategy", "erg mode", "slope mode", "rpe pacing", "time trial pacing", "auto-regulation", "flat vs uphill power", "negative split", "power distribution", "race pacing", "climbing pacing"),
        ),
        "Cross_training_and_multisport": TopicDefinition(
            slug="Cross_training_and_multisport",
            category="training",
            summary="Modality transfer, run-to-bike transfer, swimming, triathlon brick workouts",
            synonyms=("cross training", "cross-training", "multisport", "triathlon", "brick workout", "bike to run", "run to bike", "modality transfer", "swimming", "rowing", "xc skiing", "cross country skiing"),
        ),
        "Biomechanics_fit_and_equipment": TopicDefinition(
            slug="Biomechanics_fit_and_equipment",
            category="training",
            summary="Bike fit ergonomics, saddle pressure, aerodynamics CdA, rolling resistance Crr, drivetrain friction",
            synonyms=("bike fit", "biomechanics", "aerodynamics", "cda", "rolling resistance", "crr", "crank length", "saddle pressure", "tire pressure", "drivetrain efficiency", "cleat position", "shoe stiffness", "chain waxing", "stack and reach"),
        ),

        # 2. physiology (13 topics)
        "Cardiovascular_and_hemodynamics": TopicDefinition(
            slug="Cardiovascular_and_hemodynamics",
            category="physiology",
            summary="Stroke volume, eccentric left ventricular hypertrophy, cardiac output, preload, plasma volume",
            synonyms=("cardiovascular", "stroke volume", "cardiac output", "eccentric hypertrophy", "left ventricle", "cardiac preload", "plasma volume", "hemodynamics", "capillarization", "blood volume", "frank-starling", "vascular compliance"),
        ),
        "Mitochondrial_and_cellular_adaptation": TopicDefinition(
            slug="Mitochondrial_and_cellular_adaptation",
            category="physiology",
            summary="PGC-1alpha, CaMK, AMPK vs mTOR signaling, citrate synthase, fiber type transitions",
            synonyms=("mitochondria", "mitochondrial biogenesis", "mitochondrial density", "pgc-1alpha", "ampk", "camk", "p38 mapk", "citrate synthase", "respiratory chain", "fiber type transition", "mtor", "cellular signaling"),
        ),
        "Lactate_kinetics_and_metabolism": TopicDefinition(
            slug="Lactate_kinetics_and_metabolism",
            category="physiology",
            summary="MCT1/4 transporters, Brooks lactate shuttle, clearance dynamics, muscular/hepatic oxidation",
            synonyms=("lactate shuttle", "lactate kinetics", "mct1", "mct4", "monocarboxylate", "lactate clearance", "lactate oxidation", "lactic acid", "lactate turnover", "brooks lactate shuttle", "lactate transport"),
        ),
        "Substrate_utilization_and_fat_oxidation": TopicDefinition(
            slug="Substrate_utilization_and_fat_oxidation",
            category="physiology",
            summary="Beta-oxidation, CPT-1, FAT/CD36, IMTG vs FFA, glycogen depletion, FatMax, MFO, LCHF",
            synonyms=("fat oxidation", "substrate oxidation", "lipid metabolism", "beta-oxidation", "glycogen sparing", "substrate utilization", "metabolic flexibility", "fatmax", "mfo", "cpt-1", "fat/cd36", "lipolysis", "imtg", "lchf", "ketogenic", "keto"),
        ),
        "Thresholds_and_metabolic_domains": TopicDefinition(
            slug="Thresholds_and_metabolic_domains",
            category="physiology",
            summary="3-domain model: moderate/heavy/severe, LT1/VT1, LT2/VT2, MLSS, RCP, OBLA",
            synonyms=("lt1", "lt2", "vt1", "vt2", "aerobic threshold", "anaerobic threshold", "mlss", "maximal lactate steady state", "rcp", "respiratory compensation point", "exercise intensity domains", "obla", "moderate domain", "heavy domain", "severe domain"),
        ),
        "Critical_power_and_w_prime": TopicDefinition(
            slug="Critical_power_and_w_prime",
            category="physiology",
            summary="Hyperbolic power-duration model, Critical Power CP, W', W'bal, Skiba model, Critical Speed",
            synonyms=("critical power", "cp", "w'", "w prime", "w_prime", "w prime balance", "w_bal", "anaerobic work capacity", "power-duration model", "hyperbolic model", "critical speed", "skiba", "monod scherrer"),
        ),
        "FTP_and_functional_metrics": TopicDefinition(
            slug="FTP_and_functional_metrics",
            category="physiology",
            summary="Functional Threshold Power, Time-to-Exhaustion TTE at FTP, fractional utilization, MMP profile",
            synonyms=("ftp", "functional threshold power", "tte", "tta_tte", "time to exhaustion", "power-duration curve", "mmp", "mean maximal power", "fractional utilization", "coggan ftp", "power profile", "hour power", "sustainable power"),
        ),
        "VO2max_and_aerobic_kinetics": TopicDefinition(
            slug="VO2max_and_aerobic_kinetics",
            category="physiology",
            summary="VO2max limits, phase I/II/III kinetics, time constant tau, VO2 slow component, MAP",
            synonyms=("vo2max", "maximal oxygen uptake", "vo2 kinetics", "vo2 slow component", "oxygen uptake", "map", "maximal aerobic power", "peak oxygen uptake", "aerobic capacity", "tau kinetics", "oxygen deficit"),
        ),
        "Durability_and_fatigue_mechanisms": TopicDefinition(
            slug="Durability_and_fatigue_mechanisms",
            category="physiology",
            summary="Durability over kJ, central/peripheral fatigue, motor unit recruitment, Henneman size principle",
            synonyms=("durability", "fatigue resistance", "neuromuscular fatigue", "central fatigue", "peripheral fatigue", "henneman size principle", "motor unit recruitment", "late-ride power", "kj accumulation", "stamina", "eimd", "muscle damage"),
        ),
        "Autonomic_and_cardiac_monitoring": TopicDefinition(
            slug="Autonomic_and_cardiac_monitoring",
            category="physiology",
            summary="Heart rate variability HRV, rMSSD, resting HR, cardiovascular drift, Power:HR decoupling",
            synonyms=("hrv", "heart rate variability", "rmssd", "sdnn", "autonomic nervous system", "vagal tone", "cardiovascular drift", "aerobic decoupling", "power vs hr", "efficiency factor", "resting heart rate", "readiness", "orthostatic test"),
        ),
        "Environmental_and_thermal_stress": TopicDefinition(
            slug="Environmental_and_thermal_stress",
            category="physiology",
            summary="Heat acclimation, core temperature kinetics, sweat rate, altitude/hypoxia, EPO, cold stress",
            synonyms=("heat stress", "temperature effects", "thermoregulation", "heat acclimation", "core temperature", "sweat rate physiology", "altitude", "hypoxia", "acclimatization", "cold stress", "environmental physiology", "epo", "hif-1alpha"),
        ),
        "Physiological_testing_and_diagnostics": TopicDefinition(
            slug="Physiological_testing_and_diagnostics",
            category="physiology",
            summary="Metabolic cart, FatMax testing, lactate step tests, ramp tests, 20-min test, NIRS/SmO2",
            synonyms=("physiological testing", "lab testing", "field testing", "metabolic cart", "fatmax testing", "lactate testing", "lactate step test", "ramp test", "20-minute test", "nirs", "smo2", "muscle oxygenation", "zone calibration", "lab vs field", "dmax"),
        ),
        "Athlete_health_and_exercise_immunology": TopicDefinition(
            slug="Athlete_health_and_exercise_immunology",
            category="physiology",
            summary="Exercise immunology, J-curve, sickness return-to-play, AFib, bone health, female menstrual cycle",
            synonyms=("exercise immunology", "illness", "immune system", "return to play", "afib", "atrial fibrillation", "cardiac safety", "troponin", "menstrual cycle", "female athlete physiology", "perimenopause", "bone mineral density", "neck check", "urti"),
        ),

        # 3. nutrition (6 topics)
        "Carbohydrate_fueling_and_gut_training": TopicDefinition(
            slug="Carbohydrate_fueling_and_gut_training",
            category="nutrition",
            summary="Intra-workout carb rates 30-120g/hr, glucose:fructose 1:0.8/2:1, SGLT1/GLUT5, gut training",
            synonyms=("carbohydrate fueling", "carbohydrate_ratio", "intra-workout fueling", "carbs per hour", "glucose fructose ratio", "1:0.8", "2:1", "sglt1", "glut5", "gut training", "gastric emptying", "energy gels", "hydrogel", "maurten", "drink mix", "fueling rate"),
        ),
        "Daily_macronutrient_and_energy_periodization": TopicDefinition(
            slug="Daily_macronutrient_and_energy_periodization",
            category="nutrition",
            summary="Carbohydrate periodization, fuel for work, train-low/sleep-low, protein 1.6-2.2g/kg, MPS",
            synonyms=("macronutrient periodization", "fuel for the work required", "carbohydrate periodization", "train low", "sleep low", "protein requirements", "protein timing", "carbohydrate loading", "carb loading", "daily nutrition", "dietary fat", "mps", "leucine"),
        ),
        "Hydration_and_electrolyte_balance": TopicDefinition(
            slug="Hydration_and_electrolyte_balance",
            category="nutrition",
            summary="Fluid replacement, sweat rate calculation, sweat sodium concentration, hyponatremia",
            synonyms=("hydration", "electrolytes", "hydration_electrolytes", "sodium loss", "sweat sodium", "fluid replacement", "sweat rate", "hyponatremia", "rehydration", "dehydration", "isotonic", "electrolyte drinks", "hypotonic"),
        ),
        "Energy_availability_and_reds": TopicDefinition(
            slug="Energy_availability_and_reds",
            category="nutrition",
            summary="Relative Energy Deficiency in Sport RED-S, Low Energy Availability LEA <30 kcal/kg, endocrine health",
            synonyms=("red-s", "reds", "underfueling_reds", "low energy availability", "lea", "underfueling", "relative energy deficiency", "female athlete triad", "amenorrhea", "endocrine suppression", "energy availability"),
        ),
        "Ergogenic_supplements_and_buffers": TopicDefinition(
            slug="Ergogenic_supplements_and_buffers",
            category="nutrition",
            summary="Sodium bicarbonate, beta-alanine, caffeine, dietary nitrates/beetroot, creatine, ketone esters",
            synonyms=("ergogenic aids", "ergogenic_aids", "supplements", "sodium_bicarbonate", "sodium bicarbonate", "bicarb", "beta_alanine", "beta alanine", "carnosine", "caffeine", "nitrates", "beetroot juice", "creatine", "ketone esters", "exogenous ketones", "bicarbonate"),
        ),
        "Micronutrients_and_biomarkers": TopicDefinition(
            slug="Micronutrients_and_biomarkers",
            category="nutrition",
            summary="Iron metabolism, serum ferritin, hepcidin, Vitamin D3, antioxidant debate: Vitamin C/E, blood panels",
            synonyms=("micronutrients", "antioxidants", "antioxidant", "ferritin", "iron deficiency", "hepcidin", "anemia", "vitamin d", "vitamin c", "vitamin e", "polyphenols", "blood biomarkers", "blunting adaptations", "calcium", "magnesium"),
        ),

        # 4. planning (7 topics)
        "Periodization_models_and_macrocycles": TopicDefinition(
            slug="Periodization_models_and_macrocycles",
            category="planning",
            summary="Linear, block periodization, reverse, phase potentiation, annual plan ATP, progressive overload",
            synonyms=("periodization", "block_periodization", "progressive_overload", "macrocycle", "mesocycle", "annual plan", "atp", "block periodization", "linear periodization", "reverse periodization", "base build peak", "phase potentiation", "overload progression"),
        ),
        "Training_intensity_distribution": TopicDefinition(
            slug="Training_intensity_distribution",
            category="planning",
            summary="TID: Polarized 80/20, pyramidal, threshold-centric distribution, session-goal vs time-in-zone",
            synonyms=("training intensity distribution", "tid", "polarized training", "polarized model", "80/20", "pyramidal training", "threshold model", "seiler tid", "intensity distribution", "hvlit", "time in zone"),
        ),
        "Microcycle_and_schedule_design": TopicDefinition(
            slug="Microcycle_and_schedule_design",
            category="planning",
            summary="7-day/10-day microcycles, session sequencing, Norwegian double threshold scheduling, recovery weeks",
            synonyms=("microcycles", "double_threshold", "microcycle", "weekly schedule", "weekly plan", "double threshold", "norwegian method", "two sessions per day", "recovery week", "deload week", "session sequencing", "rest day"),
        ),
        "Workload_quantification_and_modeling": TopicDefinition(
            slug="Workload_quantification_and_modeling",
            category="planning",
            summary="PMC: CTL/ATL/TSB, TSS, NP, IF, Banister impulse-response model, TRIMP, mechanical kJ",
            synonyms=("volume_quantification", "training load", "tss", "training stress score", "ctl", "atl", "tsb", "fitness and fatigue", "performance management chart", "pmc", "normalized power", "np", "intensity factor", "if", "banister model", "trimp", "kilojoules", "srpe"),
        ),
        "Tapering_and_peaking": TopicDefinition(
            slug="Tapering_and_peaking",
            category="planning",
            summary="Exponential volume reduction 40-60%, intensity/frequency maintenance, taper duration, race openers",
            synonyms=("tapering", "taper", "peaking", "pre-race taper", "supercompensation", "race preparation", "openers", "volume reduction", "mujika taper", "peak readiness"),
        ),
        "Overtraining_and_recovery_management": TopicDefinition(
            slug="Overtraining_and_recovery_management",
            category="planning",
            summary="Functional/non-functional overreaching, OTS, sleep architecture, recovery modalities",
            synonyms=("overtraining", "overtraining syndrome", "ots", "overreaching", "for", "nfor", "recovery management", "sleep", "sleep hygiene", "parasympathetic overtraining", "sympathetic overtraining", "burnout", "systemic recovery", "cold water immersion", "active recovery"),
        ),
        "Psychology_and_cognitive_performance": TopicDefinition(
            slug="Psychology_and_cognitive_performance",
            category="planning",
            summary="Psychobiological model of endurance, RPE governor, mental fatigue, ACT training, resilience",
            synonyms=("sports psychology", "psychology", "rpe governor", "psychobiological model", "marcora", "mental fatigue", "cognitive resilience", "act training", "suffering tolerance", "perceived exertion", "cognitive control", "self-regulation"),
        ),
    }

    TOPIC_KEYWORDS: ClassVar[dict[str, list[str]]] = {
        slug: list(defn.synonyms) for slug, defn in CANONICAL_TOPICS.items()
    }

    CANONICAL_CATEGORIES: ClassVar[list[str]] = [
        "training",
        "physiology",
        "nutrition",
        "planning",
    ]

    def __init__(self, kb_dir: Path | None = None):
        self.kb_dir = kb_dir
        self._categories: list[str] = self.CANONICAL_CATEGORIES.copy()
        self._topics_by_category: dict[str, list[str]] = {
            cat: [defn.slug for defn in self.CANONICAL_TOPICS.values() if defn.category == cat]
            for cat in self.CANONICAL_CATEGORIES
        }
        if kb_dir:
            self._load_from_directory(kb_dir)

    def _load_from_directory(self, kb_dir: Path) -> None:
        """Optionally load custom categories/topics if a custom TAXONOMY.md is provided."""
        taxonomy_path = kb_dir / "TAXONOMY.md"
        if not taxonomy_path.exists():
            return

        with open(taxonomy_path, encoding="utf-8") as f:
            content = f.read()

        parsed_cats: list[str] = []
        parsed_topics_by_cat: dict[str, list[str]] = {}
        current_category = None

        for line in content.splitlines():
            import re
            cat_match = re.match(r"^### \d+\.\s+`([^`]+)`", line)
            if cat_match:
                current_category = cat_match.group(1)
                parsed_cats.append(current_category)
                parsed_topics_by_cat[current_category] = []
                continue

            topic_match = re.match(r"^\s+-\s+`([^`]+)`", line)
            if topic_match and current_category:
                topic = topic_match.group(1)
                parsed_topics_by_cat[current_category].append(topic)

        if parsed_cats:
            self._categories = parsed_cats
            self._topics_by_category = parsed_topics_by_cat

    def categories(self) -> list[str]:
        return self._categories.copy()

    def topics(self, category: str | None = None) -> list[str]:
        if category:
            canonical_cat = self.normalize_category(category) or category
            if canonical_cat in self._topics_by_category:
                return self._topics_by_category[canonical_cat].copy()
            return self._topics_by_category.get(category, []).copy()

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

    @classmethod
    def generate_taxonomy_markdown(cls, kb_dir: Path | None = None) -> str:
        """Generate the complete, canonical TAXONOMY.md Markdown file from Python definitions."""
        lines = [
            "# Endurance Training Knowledge Base Taxonomy",
            "",
            "This file is the canonical source for Knowledge Base categories, topics, and",
            "source frontmatter. New Knowledge Sources must use only the exact category and topic values",
            "listed here.",
            "",
            "---",
            "",
            "## Categories & Topics (4-Pillar Taxonomy - 36 Canonical Topics)",
            "",
        ]

        descriptions = {
            "training": "Training execution, interval protocol design, aerobic base, resistance exercise, biomechanics, ergonomics, and pacing tactics.",
            "physiology": "Underlying biological mechanisms, cardiovascular remodeling, cellular bioenergetics, metabolic thresholds, fatigue etiology, and diagnostic assessment.",
            "nutrition": "Nutritional fueling, intra-workout carbohydrates, hydration/fluid balance, clinical energy availability, micronutrients, and ergogenic supplementation.",
            "planning": "Periodization models, training intensity distributions, microcycle architecture, workload quantification, tapering, and overtraining management.",
        }

        for i, cat in enumerate(cls.CANONICAL_CATEGORIES, start=1):
            lines.append(f"### {i}. `{cat}`")
            lines.append(descriptions.get(cat, ""))
            lines.append("- **Topics**:")
            for defn in cls.CANONICAL_TOPICS.values():
                if defn.category == cat:
                    lines.append(f"  - `{defn.slug}` ({defn.summary})")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## Canonical Frontmatter Contract",
            "",
            "Every curated Markdown Knowledge Source must begin with a YAML mapping. The",
            "current validator reports a blocking workflow error when any of these minimum",
            "fields is missing or empty:",
            "",
            "- `title`",
            "- `category`",
            "- `topics`",
            "- `summary`",
            "",
            "Every Knowledge Source must use the standard provenance contract below:",
            "",
            "```yaml",
            "---",
            'title: "Document Title"',
            "language: en",
            "category: training",
            "topics:",
            "  - VO2max_and_aerobic_hiit",
            "  - Periodization_models_and_macrocycles",
            'source: "Origin URL or podcast name"',
            'author: "Author or speaker"',
            'date: "YYYY-MM-DD"',
            'summary: "One or two faithful English sentences."',
            "---",
            "```",
            "",
            "When directly supported takeaways have been reviewed, add:",
            "",
            "```yaml",
            "key_takeaways:",
            '  - "A takeaway directly supported by the source"',
            "```",
            "",
            "Rules:",
            "",
            "- `language` is exactly `en`; the complete source must be English.",
            "- `category` is exactly one of `training`, `physiology`, `nutrition`, or `planning`.",
            "- Every topic uses the exact spelling and case from this file. Do not introduce",
            "  a near-synonym as a one-off tag.",
            "- `source`, `author`, and `date` record real provenance. A publication date uses",
            "  `YYYY-MM-DD`; do not invent a date or provenance placeholder.",
            "- `key_takeaways` is optional. Omit it when no takeaways have been deliberately",
            "  curated; indexing does not synthesize it.",
            "",
            "The passage layer derives `source_type`, repository-relative path,",
            "`source_slug`, passage identifiers and boundaries, citation line ranges, and",
            "size diagnostics. Those values do not belong in source frontmatter.",
            "",
        ])

        markdown_content = "\n".join(lines)
        if kb_dir:
            tax_file = kb_dir / "TAXONOMY.md"
            if not tax_file.exists() or tax_file.read_text(encoding="utf-8") != markdown_content:
                tax_file.write_text(markdown_content, encoding="utf-8")
        return markdown_content

