#!/usr/bin/env python3
"""
WIP Frontmatter Migration & Taxonomy Inference Tool.

Scans Markdown documents in Knowledge_base/WIP (or any specified path),
safely extracts provenance metadata (title, author, date, source, summary),
infers canonical categories and topics using a hybrid FastEmbed dense vector
and weighted lexical classifier, cleans legacy HTML / URL artifacts,
and formats canonical YAML frontmatter conforming to TAXONOMY.md.
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from main.utils.kb_engine.embedder import PassageEmbedder
from main.utils.kb_engine.taxonomy import TaxonomyRegistry

MONTH_MAP: dict[str, str] = {
    "jan": "01",
    "january": "01",
    "feb": "02",
    "february": "02",
    "mar": "03",
    "march": "03",
    "apr": "04",
    "april": "04",
    "may": "05",
    "jun": "06",
    "june": "06",
    "jul": "07",
    "july": "07",
    "aug": "08",
    "august": "08",
    "sep": "09",
    "sept": "09",
    "september": "09",
    "oct": "10",
    "october": "10",
    "nov": "11",
    "november": "11",
    "dec": "12",
    "december": "12",
}

LEGACY_CATEGORY_MAP: dict[str, str] = {
    "hiit": "training",
    "zone2": "training",
    "strength": "training",
    "training": "training",
    "metrics": "physiology",
    "testing": "physiology",
    "physiology": "physiology",
    "nutrition": "nutrition",
    "periodization": "planning",
    "planning": "planning",
}

BLOG_AUTHORS: dict[str, str] = {
    "Coaches_Corner_Blog": "Coach Darryl MacKenzie",
    "Coaching_Professor_Paul_Laursen": "Dr. Paul Laursen",
    "Cycling_Science_Made_Simple": "Cycling Science Made Simple (Wattkg)",
    "Empirical_Cycling_Community_Notes": "Empirical Cycling Community / Kolie Moore",
    "High_North_Performance": "Tom Bell & Dr. Emma Wilkins",
    "Physiologically_Speaking_Brady_Holmer": "Brady Holmer",
    "Science_of_Endurance_Matt_Carpenter": "Matt Carpenter",
    "Spare_Cycles": "Jem Arnold",
}

BLOG_DOMAINS: dict[str, str] = {
    "Coaches_Corner_Blog": "https://selleanatomica.com",
    "Coaching_Professor_Paul_Laursen": "https://coachingprofessor.substack.com",
    "Cycling_Science_Made_Simple": "https://www.wattkg.com",
    "Empirical_Cycling_Community_Notes": "https://lucasvance.github.io/empirical-cycling-community-notes",
    "High_North_Performance": "https://www.highnorth.co.uk",
    "Physiologically_Speaking_Brady_Holmer": "https://www.physiologicallyspeaking.com",
    "Science_of_Endurance_Matt_Carpenter": "https://mcarpenter.substack.com",
    "Spare_Cycles": "https://sparecycles.blog",
}

TOPIC_DETAILED_DESCS: dict[str, tuple[str, str, list[str]]] = {
    # training
    "Short_intervals": (
        "training",
        "Short intervals, micro-intervals, intermittent intervals, 30/15, 40/20, 30/30, Tabata, Ronnestad intervals, SIT sprint interval training, short work-relief bouts",
        ["short interval", "short-interval", "micro-interval", "30s", "30/15", "40/20", "30/30", "tabata", "ronnestad", "intermittent"],
    ),
    "Long_intervals": (
        "training",
        "Long intervals, 4x8 min, 4x4 min, 4x16 min, Seiler intervals, aerobic intervals, VO2max long intervals, 5x5 min, threshold intervals, steady intervals",
        ["long interval", "long-interval", "4x8", "4x4", "4x16", "5x5", "seiler", "aerobic interval", "vo2max interval", "threshold interval"],
    ),
    "Decreasing_intervals": (
        "training",
        "Decreasing intervals, front-loaded intervals, descending duration intervals, variable duration intervals, declining interval length",
        ["decreasing interval", "front-loaded", "descending interval", "decreasing duration", "variable interval"],
    ),
    "Fast_start_intervals": (
        "training",
        "Fast-start intervals, hard-start intervals, over-pacing initial phase, accelerating VO2 kinetics, fast start pacing",
        ["fast start", "fast-start", "hard start", "hard-start", "fast start interval", "hard start interval", "over-pacing"],
    ),
    "Progressive_overload": (
        "training",
        "Progressive overload, interval progression, training density progression, increasing interval time in zone, training stimulus progression, overload principle",
        ["progressive overload", "interval progression", "overload", "training progression", "increasing volume in zone", "progression"],
    ),
    "Aerobic_base": (
        "training",
        "Aerobic base training, low-intensity training LIT, zone 2 endurance volume, polarized training, base miles, long slow distance, zone 2 rides, steady base endurance",
        ["aerobic base", "base training", "zone 2", "zone-2", "low-intensity training", "lit", "base miles", "long slow distance", "lsd", "steady endurance"],
    ),
    "Heavy_torque": (
        "training",
        "Heavy torque training, low cadence intervals, big gear intervals, slow cadence high force, SFR salite forza resistenza, torque intervals, muscular tension",
        ["heavy torque", "low cadence", "low-cadence", "big gear", "sfr", "torque interval", "high force", "pedal force", "cadence"],
    ),
    "Unilateral": (
        "training",
        "Unilateral strength training, single-leg exercises, split squats, Bulgarian split squat, single-leg press, bilateral deficit, single-leg strength",
        ["unilateral", "single leg", "single-leg", "split squat", "bulgarian split squat", "bilateral deficit"],
    ),
    "Sprint_performance": (
        "training",
        "Sprint performance, maximal neuromuscular power, rate of force development RFD, peak anaerobic power, sprint mechanics, standing start, sprint training",
        ["sprint", "sprint performance", "neuromuscular power", "peak power", "rate of force development", "rfd", "standing start", "maximal sprint"],
    ),
    "Cross_training": (
        "training",
        "Cross-training, modality transfer, running vs cycling aerobic transfer, cross-discipline training, triathlon multi-sport adaptations, run to bike transfer, cross training",
        ["cross training", "cross-training", "cross_training", "crosstraining", "modality transfer", "run vs bike", "bike vs run", "triathlon", "running and cycling"],
    ),
    "Lab_vs_field": (
        "training",
        "Lab vs field testing, determining zone 2 without metabolic cart, lactate meter vs talk test, field testing methodologies, metabolic testing protocols",
        ["lab vs field", "metabolic cart", "lactate meter", "field testing", "determining zone 2", "testing protocols", "laboratory testing"],
    ),
    # physiology
    "FTP": (
        "physiology",
        "Functional Threshold Power, 1-hour power, threshold testing, ramp test, 20-minute power, FTP testing, lactate balance point, FTP estimation, critical threshold power",
        ["ftp", "functional threshold power", "hour power", "20-minute test", "ramp test"],
    ),
    "CP": (
        "physiology",
        "Critical Power, hyperbolic power-duration relationship, CP model, 3-parameter model, critical speed, anaerobic work capacity asymptote, power duration curve",
        ["critical power", "power-duration", "power duration curve", "cp model", "critical speed"],
    ),
    "W_prime": (
        "physiology",
        "W prime, anaerobic work capacity, W prime expenditure, anaerobic capacity, kilojoules above CP, W prime reconstitution, battery expenditure",
        ["w'", "w prime", "w_prime", "anaerobic work capacity", "anaerobic capacity", "w' bal", "w prime balance"],
    ),
    "VO2max": (
        "physiology",
        "Maximal oxygen uptake, VO2 max, aerobic capacity, VLamax interaction, cardiorespiratory capacity, peak aerobic power, maximal aerobic velocity, VO2 kinetics",
        ["vo2", "vo2max", "vo2 max", "maximum oxygen uptake", "maximal oxygen uptake", "peak aerobic power", "aerobic capacity", "vo2 kinetics"],
    ),
    "FatMax": (
        "physiology",
        "Maximal fat oxidation rate, FatMax power, fat burning peak, MFO, peak fat oxidation, fat combustion zone, metabolic efficiency",
        ["fatmax", "fat max", "maximal fat oxidation", "peak fat oxidation", "mfo", "fat combustion"],
    ),
    "LT1_VT1": (
        "physiology",
        "First lactate threshold, first ventilatory threshold, aerobic threshold, talk test, baseline blood lactate rise, 2 mmol/L, LT1, VT1, gas exchange threshold",
        ["lt1", "vt1", "first threshold", "first lactate threshold", "first ventilatory threshold", "aerobic threshold", "talk test", "get"],
    ),
    "LT2_VT2": (
        "physiology",
        "Second lactate threshold, second ventilatory threshold, maximum steady state, MSS, MLSS, anaerobic threshold, OBLA, 4 mmol/L, LT2, VT2, respiratory compensation point RCP",
        ["lt2", "vt2", "second threshold", "second lactate threshold", "second ventilatory threshold", "anaerobic threshold", "mss", "mlss", "obla", "rcp", "maximal lactate steady state"],
    ),
    "Durability": (
        "physiology",
        "Durability, fatigue resistance, power degradation over time, stamina, resistance to fatigue late in long rides or after thousands of kilojoules, late-ride performance",
        ["durability", "fatigue resistance", "stamina", "power degradation", "decoupling over time", "late-ride"],
    ),
    "Power_vs_HR": (
        "physiology",
        "Power vs heart rate decoupling, aerobic decoupling, cardiac drift, efficiency factor EF, power-HR ratio, flat vs uphill power, heart rate drift",
        ["power vs hr", "power vs heart rate", "aerobic decoupling", "cardiac drift", "efficiency factor", "power-hr", "decoupling", "drift", "flat vs uphill"],
    ),
    "Heart_rate_variability": (
        "physiology",
        "Heart rate variability, HRV, rMSSD, SDNN, autonomic nervous system, readiness score, vagal tone, recovery monitoring, parasympathetic activity",
        ["hrv", "heart rate variability", "rmssd", "sdnn", "autonomic", "vagal tone", "readiness score", "morning hrv"],
    ),
    "Cardiac_hypertrophy": (
        "physiology",
        "Cardiac hypertrophy, eccentric left ventricular remodeling, stroke volume, cardiac output, Frank-Starling mechanism, ventricular preload, cardiovascular adaptations, heart health",
        ["cardiac", "stroke volume", "preload", "hypertrophy", "cardiac output", "left ventricle", "ventricular remodeling", "heart health", "cardiovascular adaptation"],
    ),
    "Lactate_shuttle": (
        "physiology",
        "Lactate shuttle, monocarboxylate transporters MCT1 and MCT4, lactate clearance, lactate oxidation, muscle lactate kinetics, lactate metabolism",
        ["lactate shuttle", "mct1", "mct4", "monocarboxylate", "lactate clearance", "lactate metabolism", "lactate oxidation", "lactate kinetics"],
    ),
    "Mitochondrial_density": (
        "physiology",
        "Mitochondrial density, mitochondrial biogenesis, PGC-1alpha, capillarization, capillary density, oxidative enzyme activity, citrate synthase, muscle fiber oxidative capacity",
        ["mitochondria", "mitochondrial", "mitochondrial biogenesis", "pgc-1alpha", "capillarization", "capillary density", "citrate synthase", "oxidative enzyme"],
    ),
    "Fat_oxidation": (
        "physiology",
        "Fat oxidation, lipid metabolism, substrate utilization, glycogen sparing, fat burning, ketogenic diet, low carb high fat LCHF, fat adaptation, keto adaptation",
        ["fat oxidation", "fat burning", "lipid metabolism", "glycogen sparing", "substrate utilization", "lchf", "ketogenic", "keto", "fat adaptation"],
    ),
    "Temperature_effects": (
        "physiology",
        "Temperature effects, heat stress, thermoregulation, heat acclimation, core temperature, sweat rate, cramping, hydration status in heat, dehydration, electrolytes, saddle sores",
        ["heat", "temperature", "heat stress", "heat acclimation", "thermoregulation", "sweat rate", "cramp", "cramping", "electrolytes", "hydration in heat", "core temp", "core temperature", "saddle sore"],
    ),
    # nutrition
    "Sodium_bicarbonate": (
        "nutrition",
        "Sodium bicarbonate, bicarb supplementation, extracellular buffering agent, Maurten bicarb system, blood pH alkalosis, sodium bicarb protocol",
        ["sodium bicarbonate", "bicarbonate", "bicarb", "maurten bicarb", "extracellular buffer", "blood ph alkalosis"],
    ),
    "Beta_alanine": (
        "nutrition",
        "Beta-alanine, carnosine synthesis, intracellular buffering agent, tingling paresthesia, high-intensity buffer, carnosine loading",
        ["beta alanine", "beta-alanine", "carnosine", "intracellular buffer", "paresthesia", "carnosine loading"],
    ),
    "Carbohydrate_ratio": (
        "nutrition",
        "Carbohydrate ratio, glucose to fructose 1:0.8 or 2:1, grams of carbs per hour, gut training, intra-workout fueling, exogenous carbohydrate oxidation, fueling with carbohydrates, fueling strategy",
        ["carbohydrate", "glucose", "fructose", "carbs per hour", "fueling", "gut training", "intra-workout fueling", "glycogen", "sugar", "carbohydrate ratio"],
    ),
    "Antioxidants": (
        "nutrition",
        "Antioxidants supplementation, vitamin C, vitamin E, polyphenols, blunting training adaptation, reactive oxygen species ROS, redox balance",
        ["antioxidant", "antioxidants", "vitamin c", "vitamin e", "polyphenols", "blunting adaptation", "reactive oxygen species", "ros"],
    ),
    "Underfueling_REDs": (
        "nutrition",
        "Relative energy deficiency in sport RED-S, low energy availability LEA, underfueling, hormonal suppression, bone health, female athlete triad, eating disorder in athletes",
        ["underfueling", "red-s", "reds", "low energy availability", "lea", "relative energy deficiency", "female athlete triad", "energy deficit", "amenorrhea"],
    ),
    "Ergogenic_aids": (
        "nutrition",
        "Ergogenic aids, performance supplements, caffeine, creatine monohydrate, dietary nitrates, beetroot juice, glycerol, legal performance enhancers, sports supplements",
        ["ergogenic", "caffeine", "creatine", "nitrate", "beetroot", "supplement", "supplements", "ergogenic aid", "performance supplement"],
    ),
    # planning
    "Block_periodization": (
        "planning",
        "Block periodization, concentrated loading blocks, block training vs linear periodization, HIT shock blocks, training blocks",
        ["block periodization", "block training", "concentrated loading", "shock block", "training block", "hit block"],
    ),
    "Double_threshold": (
        "planning",
        "Double threshold training, Norwegian training model, two threshold sessions in one day, subthreshold training, Ingebrigtsen method, double threshold model",
        ["double threshold", "norwegian method", "norwegian model", "two sessions per day", "subthreshold", "ingebrigtsen"],
    ),
    "Microcycles": (
        "planning",
        "Microcycles, weekly training structure, 7-day or 10-day microcycle design, recovery weeks, tapering, taper protocols, weekly planning, rest days, sleep and recovery",
        ["microcycle", "weekly structure", "weekly plan", "taper", "tapering", "recovery week", "rest day", "sleep", "recovery", "deload"],
    ),
    "TTA_TTE": (
        "planning",
        "Time to exhaustion TTE, time to fatigue at FTP or Critical Power, sustaining threshold power, TTA, time to exhaustion duration, fatigue point",
        ["tte", "time to exhaustion", "time-to-exhaustion", "tta", "sustaining power", "duration at ftp", "exhaustion"],
    ),
    "Volume_quantification": (
        "planning",
        "Volume quantification, training stress score TSS, kilojoules kJ, work in zones, training load, acute to chronic workload ratio, CTL, ATL, TSB, quantified training volume, tracking training load",
        ["tss", "training stress score", "kilojoules", "training load", "ctl", "atl", "tsb", "volume quantification", "workload", "training volume", "tracking load"],
    ),
    "Periodization": (
        "planning",
        "Annual training plan, periodization phases, mesocycles, macrocycles, base build peak, phase potentiation",
        ["periodization", "annual plan", "macrocycle", "mesocycle", "training phase", "base build peak", "phase potentiation"],
    ),
}


@dataclass(frozen=True, slots=True)
class MigrationResult:
    file_path: Path
    rel_path: str
    original_frontmatter: dict[str, Any]
    new_frontmatter: dict[str, Any]
    diff: str
    changed: bool
    is_valid: bool
    error_message: str = ""


class WIPFrontmatterMigrator:
    def __init__(self, kb_dir: Path, taxonomy: TaxonomyRegistry | None = None):
        self.kb_dir = kb_dir.resolve()
        self.taxonomy = taxonomy or TaxonomyRegistry(self.kb_dir)
        self.embedder = PassageEmbedder.get_model()
        self._init_topic_embeddings()

    def _init_topic_embeddings(self) -> None:
        self.topic_names = list(TOPIC_DETAILED_DESCS.keys())
        topic_texts = [
            f"{t} ({TOPIC_DETAILED_DESCS[t][0]}): {TOPIC_DETAILED_DESCS[t][1]}"
            for t in self.topic_names
        ]
        topic_vecs = list(self.embedder.embed(topic_texts))
        matrix = np.array(topic_vecs, dtype=np.float32)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        self.topic_matrix = matrix / (norms + 1e-9)

    def safe_parse_header(self, content: str) -> tuple[dict[str, Any], str]:
        if not content.startswith("---"):
            return {}, content
        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}, content
        raw_yaml = parts[1]
        # Clean escaped quote artifacts like \" or \\"
        fixed_yaml = re.sub(r'\\\\\"|\\\"', "'", raw_yaml)
        try:
            data = yaml.safe_load(fixed_yaml)
            if isinstance(data, dict):
                return data, parts[2]
        except Exception:
            pass

        # Fallback line-by-line parsing
        meta: dict[str, Any] = {}
        for line in raw_yaml.splitlines():
            m = re.match(r"^(\w+):\s*(.*)$", line)
            if m:
                k, v = m.group(1), m.group(2).strip('"\' ')
                meta[k] = v
        return meta, parts[2]

    def normalize_date(
        self, raw_date: Any, content: str = "", default_year: int = 2023
    ) -> str:
        d_str = str(raw_date).strip() if raw_date is not None else ""
        m1 = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", d_str)
        if m1:
            y, m, d = m1.groups()
            return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"

        m2 = re.match(r"^(\d{1,2})\s+([a-zA-Z]+)$", d_str)
        if m2:
            day, mon = m2.groups()
            mon_clean = mon.lower()
            if mon_clean in MONTH_MAP:
                years = [
                    int(y)
                    for y in re.findall(r"\b(20\d\d)\b", content)
                    if 2015 <= int(y) <= 2026
                ]
                year = max(years) if years else default_year
                return f"{year:04d}-{MONTH_MAP[mon_clean]}-{int(day):02d}"

        m3 = re.match(r"^([a-zA-Z]+)\s+(\d{1,2}),?\s*(\d{4})$", d_str)
        if m3:
            mon, day, year = m3.groups()
            mon_clean = mon.lower()
            if mon_clean in MONTH_MAP:
                return f"{int(year):04d}-{MONTH_MAP[mon_clean]}-{int(day):02d}"

        # Try searching for a date in the content text or filename
        m4 = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", content[:1000])
        if m4:
            y, m, d = m4.groups()
            return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"

        return f"{default_year}-01-01"

    def extract_source(self, file_path: Path, content: str) -> str:
        m = re.search(
            r"Source:\s*\[.*?\]\((https?://[^\s\)]+)\)", content, re.IGNORECASE
        )
        if m:
            return m.group(1).strip()
        m2 = re.search(r"Source:\s*(https?://[^\s\)]+)", content, re.IGNORECASE)
        if m2:
            return m2.group(1).strip()
        for folder, domain in BLOG_DOMAINS.items():
            if folder in str(file_path):
                return domain
        return "Endurance Training Knowledge Base"

    def extract_author(
        self, file_path: Path, meta: dict[str, Any], content: str
    ) -> str:
        author = str(meta.get("author", "")).strip()
        if author:
            return author
        m = re.search(r"Author:\s*\[?(.*?)\]?(?:\(|$)", content)
        if m:
            a = m.group(1).strip("[]() *")
            if a and not a.startswith("http"):
                return a
        for folder, default_author in BLOG_AUTHORS.items():
            if folder in str(file_path):
                return default_author
        return "Endurance Research"

    def extract_summary(
        self, meta: dict[str, Any], content: str, body: str, title: str
    ) -> str:
        def _clean(t: str) -> str:
            t = re.sub(r"\[([^\]]+)\]\(<?[^>\)]*>?\)", r"\1", t)
            t = re.sub(r"<[^>]+>", "", t)
            t = re.sub(r"[\*_`]", "", t)
            t = re.sub(r"\s+", " ", t).strip()
            return t

        def _filter_bylines(raw_text: str) -> str:
            lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
            filtered = [
                l
                for l in lines
                if not re.match(
                    r"(?i)^(?:written by|\d+\s+[A-Za-z]+|\d{4}-\d{2}-\d{2}|by:?\s+\[?)",
                    l,
                )
                and not re.match(r"(?i)^author:?\s*", l)
            ]
            return _clean(" ".join(filtered))

        desc = str(meta.get("description", "")).strip()
        cleaned_desc = _filter_bylines(desc)
        cleaned_desc = re.sub(
            r"^([A-Za-z0-9\s:,\-'\"]+)\s+\1", r"\1", cleaned_desc
        ).strip()

        # If description is substantive, different from title, and not truncated with ellipses
        if (
            len(cleaned_desc) > 35
            and not cleaned_desc.endswith("...")
            and cleaned_desc.lower() != title.lower()
        ):
            return cleaned_desc[:350].strip()

        # Try abstract
        m = re.search(r"<abstract[^>]*>(.*?)</abstract>", content, re.DOTALL)
        if m:
            ab = _filter_bylines(m.group(1))
            if len(ab) > 35 and ab.lower() != title.lower() and not ab.endswith("..."):
                return ab[:350].strip()

        # Fallback to first high-quality content paragraph
        for block in body.split("\n\n"):
            b = _clean(block)
            if (
                len(b) > 50
                and not b.startswith("#")
                and not b.startswith("---")
                and not b.startswith("Source:")
                and not b.startswith("Author:")
                and not b.startswith("Written By")
                and not b.startswith("Jump Link")
                and not b.startswith("Key Takeaways")
                and not b.startswith("Illustration / Chart")
                and not b.startswith("Photo by")
                and b.lower() != title.lower()
            ):
                return b[:350].strip()

        return cleaned_desc or f"Detailed endurance training analysis of {title}."

    def extract_key_takeaways(self, body: str) -> list[str] | None:
        m = re.search(
            r"(?i)(?:##\s*Key Takeaways|Key Takeaways:)\s*\n+(.*?)(?=\n##|\n<nav>|\Z)",
            body,
            re.DOTALL,
        )
        if not m:
            return None
        raw_section = m.group(1)
        takeaways = []
        for line in raw_section.splitlines():
            line_s = line.strip()
            if line_s.startswith(("* ", "- ", "• ")) or re.match(
                r"^\d+\.\s+", line_s
            ):
                # Filter out pure link entries (e.g. host bios, books, websites)
                if re.match(r"^[*\-•\d\.]+\s*\[.*?\]\(.*?\)$", line_s):
                    continue
                cleaned = re.sub(r"^[*\-•\d\.]+\s*", "", line_s)
                cleaned = re.sub(r"\[([^\]]+)\]\(<?[^>\)]*>?\)", r"\1", cleaned)
                cleaned = re.sub(r"[\*_`]", "", cleaned).strip()
                if (
                    len(cleaned) > 25
                    and not cleaned.startswith("http")
                    and not cleaned.startswith("Breath:")
                    and "amazon.com" not in cleaned.lower()
                    and "coaching.com" not in cleaned.lower()
                    and "tired mom runs" not in cleaned.lower()
                    and "where fitness meets" not in cleaned.lower()
                ):
                    takeaways.append(cleaned)
        return takeaways[:6] if takeaways else None

    def classify_document(
        self, title: str, summary: str, body: str
    ) -> tuple[str, list[str]]:
        t_lower = title.lower()
        s_lower = summary.lower()
        b_lower = body[:3000].lower()

        # Keyword scores
        kw_scores: dict[str, float] = {t: 0.0 for t in self.topic_names}
        for t, (_, _, keywords) in TOPIC_DETAILED_DESCS.items():
            for kw in keywords:
                if kw in t_lower:
                    kw_scores[t] += 4.5
                if kw in s_lower:
                    kw_scores[t] += 2.5
                if kw in b_lower:
                    kw_scores[t] += 1.0

        # Dense vector semantic scoring
        query_text = f"{title}. {summary}"
        doc_vec = next(iter(self.embedder.embed([query_text])))
        doc_vec = doc_vec / (np.linalg.norm(doc_vec) + 1e-9)
        sims = np.dot(self.topic_matrix, doc_vec)

        # Combined scoring
        combined: list[tuple[float, str, str]] = []
        for i, t in enumerate(self.topic_names):
            cat = TOPIC_DETAILED_DESCS[t][0]
            sim_score = max(0.0, float(sims[i]) - 0.28) * 6.0
            total_score = kw_scores[t] * 2.0 + sim_score
            combined.append((total_score, t, cat))

        combined.sort(key=lambda x: x[0], reverse=True)

        selected_topics: list[str] = []
        for score, t, cat in combined:
            if score > 1.2:
                selected_topics.append(t)
            if len(selected_topics) >= 4:
                break

        if not selected_topics:
            selected_topics = [combined[0][1]]

        top_topic = selected_topics[0]
        primary_category = TOPIC_DETAILED_DESCS[top_topic][0]

        return primary_category, selected_topics

    def clean_markdown_body(self, body: str) -> str:
        # Remove <abstract> blocks
        cleaned = re.sub(r"<abstract[^>]*>.*?</abstract>\s*", "", body, flags=re.DOTALL)
        # Remove <nav> blocks
        cleaned = re.sub(r"<nav[^>]*>.*?</nav>\s*", "", cleaned, flags=re.DOTALL)
        # Fix angle-bracket wrapped URLs in markdown links: [text](<https://...>) -> [text](https://...)
        cleaned = re.sub(r"\[(.*?)\]\(<(https?://[^\s>]+)>\)", r"[\1](\2)", cleaned)
        cleaned = re.sub(r"\[(.*?)\]\(<(/[^>]+)>\)", r"[\1](\2)", cleaned)
        return cleaned.strip() + "\n"

    def format_frontmatter(self, doc_data: dict[str, Any]) -> str:
        lines = ["---"]
        title_str = str(doc_data.get("title", "")).replace('"', '\\"')
        lines.append(f'title: "{title_str}"')
        lines.append(f"language: {doc_data.get('language', 'en')}")
        lines.append(f"category: {doc_data.get('category')}")
        lines.append("topics:")
        for topic in doc_data.get("topics", []):
            lines.append(f"  - {topic}")
        source_str = str(doc_data.get("source", "")).replace('"', '\\"')
        lines.append(f'source: "{source_str}"')
        author_str = str(doc_data.get("author", "")).replace('"', '\\"')
        lines.append(f'author: "{author_str}"')
        lines.append(f'date: "{doc_data.get("date")}"')
        summary_str = str(doc_data.get("summary", "")).replace('"', "'")
        lines.append(f'summary: "{summary_str}"')

        key_takeaways = doc_data.get("key_takeaways")
        if key_takeaways:
            lines.append("key_takeaways:")
            for kt in key_takeaways:
                kt_clean = kt.replace('"', "'")
                lines.append(f'  - "{kt_clean}"')

        lines.append("---")
        return "\n".join(lines)

    def process_file(
        self, file_path: Path, apply: bool = False, clean_body: bool = True
    ) -> MigrationResult:
        file_path = file_path.resolve()
        try:
            rel_path = str(file_path.relative_to(self.kb_dir))
        except ValueError:
            rel_path = file_path.name
        content = file_path.read_text(encoding="utf-8")
        orig_meta, orig_body = self.safe_parse_header(content)

        # Title extraction & sanitization
        title = orig_meta.get("title", "")
        if not title:
            h1 = re.search(r"^#\s+(.+)$", orig_body, re.MULTILINE)
            title = h1.group(1).strip() if h1 else file_path.stem.replace("_", " ")
        title = re.sub(r'\\\\\"|\\\"', '"', title).strip()

        # Date, author, source, summary
        date_val = self.normalize_date(orig_meta.get("date"), content)
        author = self.extract_author(file_path, orig_meta, content)
        source = self.extract_source(file_path, content)
        summary = self.extract_summary(orig_meta, content, orig_body, title)
        takeaways = self.extract_key_takeaways(orig_body)

        # Infer category and topics
        category, topics = self.classify_document(title, summary, orig_body)

        new_meta: dict[str, Any] = {
            "title": title,
            "language": "en",
            "category": category,
            "topics": topics,
            "source": source,
            "author": author,
            "date": date_val,
            "summary": summary,
        }
        if takeaways:
            new_meta["key_takeaways"] = takeaways

        new_fm_str = self.format_frontmatter(new_meta)
        target_body = self.clean_markdown_body(orig_body) if clean_body else orig_body.strip() + "\n"
        new_content = f"{new_fm_str}\n\n{target_body}"

        diff = "".join(
            difflib.unified_diff(
                content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"a/{rel_path}",
                tofile=f"b/{rel_path}",
            )
        )

        changed = content != new_content
        if apply and changed:
            file_path.write_text(new_content, encoding="utf-8")

        return MigrationResult(
            file_path=file_path,
            rel_path=rel_path,
            original_frontmatter=orig_meta,
            new_frontmatter=new_meta,
            diff=diff,
            changed=changed,
            is_valid=True,
        )

    def process_directory(
        self, target_dir: Path, apply: bool = False, clean_body: bool = True
    ) -> list[MigrationResult]:
        results: list[MigrationResult] = []
        md_files = sorted(target_dir.rglob("*.md"))
        for file_path in md_files:
            if file_path.name in {"INDEX.md", "TAXONOMY.md"}:
                continue
            res = self.process_file(file_path, apply=apply, clean_body=clean_body)
            results.append(res)
        return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate WIP markdown files with valid taxonomy frontmatter"
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("Knowledge_base/WIP"),
        help="Target directory to process (default: Knowledge_base/WIP)",
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=None,
        help="Process a single file instead of full directory",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write updated frontmatter and clean body to disk",
    )
    parser.add_argument(
        "--preview",
        type=int,
        default=0,
        metavar="N",
        help="Display diff previews for N sample documents",
    )
    parser.add_argument(
        "--reindex",
        action="store_true",
        help="Rebuild search index and sitemap after applying",
    )
    args = parser.parse_args()

    kb_dir = Path("Knowledge_base")
    migrator = WIPFrontmatterMigrator(kb_dir)

    if args.file:
        files_to_process = [args.file]
    else:
        target_dir = args.dir if args.dir.is_absolute() else (Path.cwd() / args.dir)
        files_to_process = sorted(target_dir.rglob("*.md"))

    print("==========================================================")
    print("      Knowledge Base WIP Frontmatter Migration Engine     ")
    print("==========================================================")
    mode = "APPLY (WRITING TO DISK)" if args.apply else "DRY-RUN (NO CHANGES SAVED)"
    print(f"Mode:               {mode}")
    print(f"Total Files Found:  {len(files_to_process)}")
    print("----------------------------------------------------------\n")

    results: list[MigrationResult] = []
    category_counts: dict[str, int] = {}
    topic_counts: dict[str, int] = {}

    for fp in files_to_process:
        if fp.name in {"INDEX.md", "TAXONOMY.md"}:
            continue
        res = migrator.process_file(fp, apply=args.apply)
        results.append(res)
        cat = res.new_frontmatter["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
        for t in res.new_frontmatter["topics"]:
            topic_counts[t] = topic_counts.get(t, 0) + 1

    print("Inferred Category Distribution:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        pct = (count / len(results)) * 100 if results else 0
        print(f"  - {cat:15}: {count:4d} files ({pct:5.1f}%)")
    print()

    print(f"Top Inferred Topics (across {len(topic_counts)} unique taxonomy topics):")
    for t, count in sorted(topic_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  - {t:25}: {count:4d} references")
    print()

    if args.preview > 0 and results:
        preview_count = min(args.preview, len(results))
        # Select evenly spaced samples across blogs
        step = max(1, len(results) // preview_count)
        samples = [results[i] for i in range(0, len(results), step)][:preview_count]

        print(f"Showing {len(samples)} Sample Previews:")
        print("=" * 60)
        for s in samples:
            print(f"\n--- FILE: {s.rel_path} ---")
            print(s.diff if s.diff else "[No diff - already identical]")
            print("-" * 60)

    if args.apply and args.reindex:
        from main.utils.kb_engine import KBEngine

        print("\nRebuilding Knowledge Base Derived Index & Sitemap...")
        engine = KBEngine(kb_dir=kb_dir)
        engine.build_index()
        engine.build_sitemap()
        print("Running validation check...")
        val_res = engine.validate()
        print(f"Validation: {len(val_res['errors'])} errors, {len(val_res['warnings'])} warnings.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
