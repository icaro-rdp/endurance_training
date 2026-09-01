"""
Local LLM Topic Auto-Tagger and Bottom-Up Categorization Module.
"""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel, Field, field_validator

from main.utils.kb_engine.errors import (
    MissingDependencyError,
    ModelConnectionError,
    ModelInferenceError,
)
from main.utils.kb_engine.frontmatter import KnowledgeSource
from main.utils.kb_engine.taxonomy import TaxonomyRegistry

logger = logging.getLogger(__name__)

DEFAULT_LOCAL_MODEL = "mlx-community/Qwen2.5-7B-Instruct-4bit"


class DocumentTaggingResult(BaseModel):
    """Structured data contract for model topic auto-tagging output."""

    category: str = Field(
        description="The primary operational macro-category (resolved bottom-up)."
    )
    topics: list[str] = Field(
        description="All specific canonical topics discussed substantively in depth.",
        min_length=1,
        max_length=8,
    )
    summary: str = Field(
        description=(
            "One or two faithful, high-density English sentences summarizing "
            "key takeaways."
        )
    )
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    topic_evidence: dict[str, str] = Field(default_factory=dict)

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        """Validate category strictly against canonical 4-pillar categories."""
        if value not in TaxonomyRegistry.CANONICAL_CATEGORIES:
            raise ValueError(
                f"Category '{value}' is not a valid canonical category: "
                f"{TaxonomyRegistry.CANONICAL_CATEGORIES}"
            )
        return value

    @field_validator("topics")
    @classmethod
    def validate_topics(cls, topics: list[str]) -> list[str]:
        """Validate topics strictly against canonical 36 topics."""
        if not topics:
            raise ValueError("Topics list cannot be empty.")
        if len(topics) > 8:
            raise ValueError(f"Topics list cannot exceed 8 topics (got {len(topics)}).")
        for topic in topics:
            if topic not in TaxonomyRegistry.CANONICAL_TOPICS:
                raise ValueError(
                    f"Topic '{topic}' is not a valid canonical topic in taxonomy."
                )
        # Deduplicate while preserving order
        deduped: list[str] = []
        for t in topics:
            if t not in deduped:
                deduped.append(t)
        return deduped

    @classmethod
    def json_schema_for_taxonomy(
        cls, taxonomy: TaxonomyRegistry | None = None
    ) -> dict[str, Any]:
        """Export dynamic JSON schema constrained by canonical taxonomy enums."""
        categories = (
            taxonomy.categories()
            if taxonomy
            else list(TaxonomyRegistry.CANONICAL_CATEGORIES)
        )
        topics = (
            taxonomy.topics()
            if taxonomy
            else list(TaxonomyRegistry.CANONICAL_TOPICS.keys())
        )
        return {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": categories,
                    "description": "Primary macro-category resolved bottom-up.",
                },
                "topics": {
                    "type": "array",
                    "items": {"type": "string", "enum": topics},
                    "minItems": 1,
                    "maxItems": 8,
                    "description": "Canonical topics substantively discussed.",
                },
                "summary": {
                    "type": "string",
                    "description": "One or two concise English summary sentences.",
                },
                "confidence_score": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 1.0,
                },
                "topic_evidence": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
            },
            "required": ["category", "topics", "summary"],
            "additionalProperties": False,
        }


class ModelAdapter(Protocol):
    """Protocol seam for local LLM inference backends."""

    def generate(
        self, prompt: str, schema: type[BaseModel] | dict[str, Any]
    ) -> dict[str, Any]:
        """Generate structured JSON response adhering to schema."""
        ...


class FakeModelAdapter:
    """Deterministic model adapter for fast, reproducible unit tests."""

    def __init__(
        self,
        default_response: dict[str, Any] | None = None,
        responses_by_keyword: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        self.default_response = default_response or {
            "category": "training",
            "topics": ["Zone2_and_endurance_base"],
            "summary": "Default fake model classification summary.",
            "confidence_score": 1.0,
            "topic_evidence": {
                "Zone2_and_endurance_base": "Aerobic base endurance miles."
            },
        }
        self.responses_by_keyword = responses_by_keyword or {}
        self.call_count = 0
        self.last_prompt = ""
        self.last_schema: Any = None

    def generate(
        self, prompt: str, schema: type[BaseModel] | dict[str, Any]
    ) -> dict[str, Any]:
        self.call_count += 1
        self.last_prompt = prompt
        self.last_schema = schema

        for keyword, resp in self.responses_by_keyword.items():
            if keyword in prompt:
                return resp
        return self.default_response


class MLXAdapter:
    """Apple Silicon native GPU adapter using mlx-lm with constrained sampling."""

    def __init__(
        self,
        model_name: str = DEFAULT_LOCAL_MODEL,
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> None:
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._model: Any = None
        self._tokenizer: Any = None

    def _ensure_loaded(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return

        try:
            import mlx_lm
        except ImportError as exc:
            raise MissingDependencyError(
                "mlx-lm",
                "Install using: uv add --optional local-ai 'mlx-lm>=0.21.0'",
            ) from exc

        try:
            loaded = mlx_lm.load(self.model_name)
            self._model = loaded[0]
            self._tokenizer = loaded[1]
        except Exception as exc:
            raise ModelInferenceError(
                f"Failed to load MLX model '{self.model_name}': {exc}"
            ) from exc

    def generate(
        self, prompt: str, schema: type[BaseModel] | dict[str, Any]
    ) -> dict[str, Any]:
        self._ensure_loaded()
        import mlx_lm
        import mlx_lm.sample_utils

        if isinstance(schema, type) and issubclass(schema, BaseModel):
            schema_json = schema.model_json_schema()
        else:
            schema_json = schema

        schema_str = json.dumps(schema_json)
        system_content = (
            "You are a rigorous sports science taxonomy classifier. "
            "You MUST respond ONLY with a valid JSON object conforming to "
            f"this JSON Schema:\n{schema_str}"
        )
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt},
        ]

        if hasattr(self._tokenizer, "apply_chat_template"):
            formatted_prompt = self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            formatted_prompt = (
                f"System: {system_content}\n\nUser: {prompt}\n\nAssistant: "
            )

        sampler = mlx_lm.sample_utils.make_sampler(temp=self.temperature)
        logits_processors = mlx_lm.sample_utils.make_logits_processors()

        try:
            raw_output = mlx_lm.generate(
                self._model,
                self._tokenizer,
                prompt=formatted_prompt,
                max_tokens=self.max_tokens,
                sampler=sampler,
                logits_processors=logits_processors,
                verbose=False,
            )
        except Exception as exc:
            raise ModelInferenceError(f"MLX generation failed: {exc}") from exc

        try:
            return _extract_json_from_text(raw_output)
        except Exception as exc:
            raise ModelInferenceError(
                f"Failed to parse MLX JSON output: {raw_output}"
            ) from exc


class OllamaAdapter:
    """Ollama local HTTP API adapter."""

    def __init__(
        self,
        model_name: str = "qwen2.5:7b",
        host: str = "http://localhost:11434",
        timeout: float = 60.0,
    ) -> None:
        self.model_name = model_name
        self.host = host.rstrip("/")
        self.timeout = timeout

    def generate(
        self, prompt: str, schema: type[BaseModel] | dict[str, Any]
    ) -> dict[str, Any]:
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            schema_json = schema.model_json_schema()
        else:
            schema_json = schema

        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an expert sports science taxonomy tagger. "
                        "Respond ONLY with a JSON object conforming to the schema."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "format": schema_json,
            "stream": False,
            "options": {"temperature": 0.0},
        }

        url = f"{self.host}/api/chat"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise ModelConnectionError(self.host, str(exc)) from exc
        except Exception as exc:
            raise ModelInferenceError(f"Ollama request error: {exc}") from exc

        content = resp_data.get("message", {}).get("content", "")
        if not content:
            raise ModelInferenceError("Empty response received from Ollama.")

        try:
            return _extract_json_from_text(content)
        except Exception as exc:
            raise ModelInferenceError(
                f"Failed to parse Ollama JSON output: {content}"
            ) from exc


def _extract_json_from_text(text: str) -> dict[str, Any]:
    """Extract and parse JSON object from text or markdown code fence."""
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1).strip()
    else:
        first_brace = cleaned.find("{")
        last_brace = cleaned.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            cleaned = cleaned[first_brace : last_brace + 1]

    try:
        parsed = json.loads(cleaned)
        if not isinstance(parsed, dict):
            raise ModelInferenceError(
                f"Expected JSON object, got {type(parsed).__name__}"
            )
        return parsed
    except json.JSONDecodeError as exc:
        raise ModelInferenceError(
            f"Invalid JSON string extracted from output: {cleaned[:100]}"
        ) from exc


def _split_into_windows(full_text: str, max_window_chars: int = 12000) -> list[str]:
    """Split markdown into heading-aware windows covering all chars."""
    if len(full_text) <= max_window_chars:
        return [full_text]

    sections = re.split(r"(?=(?:\n|^)#{1,3}\s+)", full_text)
    windows: list[str] = []
    current_chunk = ""

    for section in sections:
        if not section:
            continue
        if len(current_chunk) + len(section) <= max_window_chars:
            current_chunk += section
        else:
            if current_chunk:
                windows.append(current_chunk)
            if len(section) > max_window_chars:
                for i in range(0, len(section), max_window_chars - 500):
                    part = section[i : i + max_window_chars]
                    if part:
                        windows.append(part)
                current_chunk = ""
            else:
                current_chunk = section

    if current_chunk and (not windows or windows[-1] != current_chunk):
        windows.append(current_chunk)

    return windows if windows else [full_text]


def _consolidate_window_results(
    window_results: list[DocumentTaggingResult],
    taxonomy: TaxonomyRegistry,
) -> DocumentTaggingResult:
    """
    Consolidate results across all document windows.
    - Collects all candidate topics across every window.
    - Ranks candidate topics by recurrence across windows and evidence.
    - Retains up to 8 top topics.
    - Merges evidence snippets for retained topics.
    - Synthesizes summary sentences across windows into a cohesive summary.
    - Resolves primary category bottom-up AFTER final topics are selected.
    """
    if len(window_results) == 1:
        return window_results[0]

    topic_window_counts: dict[str, int] = {}
    topic_conf_sums: dict[str, float] = {}
    topic_evidence_map: dict[str, list[str]] = {}

    for wr in window_results:
        for topic in wr.topics:
            topic_window_counts[topic] = topic_window_counts.get(topic, 0) + 1
            topic_conf_sums[topic] = (
                topic_conf_sums.get(topic, 0.0) + wr.confidence_score
            )
            ev = wr.topic_evidence.get(topic)
            if ev:
                if topic not in topic_evidence_map:
                    topic_evidence_map[topic] = []
                if ev not in topic_evidence_map[topic]:
                    topic_evidence_map[topic].append(ev)

    sorted_topics = sorted(
        topic_window_counts.keys(),
        key=lambda t: (
            -topic_window_counts[t],
            -topic_conf_sums[t],
            -len(" ".join(topic_evidence_map.get(t, []))),
            t,
        ),
    )
    final_topics = sorted_topics[:8]

    final_evidence: dict[str, str] = {}
    for t in final_topics:
        snippets = topic_evidence_map.get(t, [])
        if snippets:
            final_evidence[t] = " ".join(snippets)

    summary_sentences: list[str] = []
    for wr in window_results:
        if wr.summary:
            for sent in re.split(r"(?<=[.!?])\s+", wr.summary.strip()):
                sent_clean = sent.strip()
                if sent_clean and sent_clean not in summary_sentences:
                    summary_sentences.append(sent_clean)

    final_summary = (
        " ".join(summary_sentences[:3])
        if summary_sentences
        else "Consolidated document summary."
    )

    category_counts: dict[str, int] = {}
    for t in final_topics:
        defn = taxonomy.CANONICAL_TOPICS.get(t)
        cat = defn.category if defn else None
        if cat:
            category_counts[cat] = category_counts.get(cat, 0) + 1

    if not category_counts:
        final_category = "training"
    else:
        sorted_cats = sorted(
            category_counts.keys(),
            key=lambda c: (
                -category_counts[c],
                0
                if c == "training"
                else (1 if c == "physiology" else (2 if c == "nutrition" else 3)),
            ),
        )
        final_category = sorted_cats[0]

    avg_conf = sum(wr.confidence_score for wr in window_results) / len(window_results)

    return DocumentTaggingResult(
        category=final_category,
        topics=final_topics,
        summary=final_summary,
        confidence_score=round(avg_conf, 2),
        topic_evidence=final_evidence,
    )


class LocalLLMClassifier:
    """
    Topic Auto-Tagger and Bottom-Up Categorization engine.
    Derives topics across full taxonomy first, then resolves macro-category.
    """

    def __init__(
        self,
        adapter: ModelAdapter | None = None,
        taxonomy: TaxonomyRegistry | None = None,
        kb_dir: Path | None = None,
        max_window_chars: int = 12000,
    ) -> None:
        self.kb_dir = kb_dir or Path("Knowledge_base")
        self.taxonomy = taxonomy or TaxonomyRegistry(self.kb_dir)
        self.adapter = adapter or MLXAdapter()
        self.max_window_chars = max_window_chars

    def build_prompt(
        self,
        title: str,
        content: str,
        existing_summary: str | None = None,
    ) -> str:
        """Construct prompt dynamically from canonical TaxonomyRegistry."""
        categories = self.taxonomy.categories()
        topics_by_cat = {cat: self.taxonomy.topics(cat) for cat in categories}

        taxonomy_lines = []
        for cat in categories:
            taxonomy_lines.append(f"### Category: `{cat}`")
            for topic in topics_by_cat.get(cat, []):
                defn = self.taxonomy.CANONICAL_TOPICS.get(topic)
                desc = defn.summary if defn else topic
                taxonomy_lines.append(f"  - `{topic}`: {desc}")
            taxonomy_lines.append("")

        taxonomy_str = "\n".join(taxonomy_lines)

        summary_clause = (
            f"Existing Summary / Provenance: {existing_summary}\n"
            if existing_summary
            else ""
        )

        return (
            "Analyze this endurance sports science document. "
            "Assign canonical topics and derive the macro-category bottom-up.\n\n"
            f"CANONICAL TAXONOMY (36 Topics across 4 Categories):\n"
            f"{taxonomy_str}\n"
            "RULES:\n"
            "1. NON-HIERARCHICAL TOPIC SELECTION: Select 1 to 8 canonical topics "
            "from across the full vocabulary substantively discussed.\n"
            "2. BOTTOM-UP CATEGORY RESOLUTION: After assigning topics, derive the "
            "single best primary category:\n"
            "   - 'training' for workout protocols, pacing, strength, or drills.\n"
            "   - 'physiology' for biological mechanisms, thresholds, cellular "
            "adaptations, or testing.\n"
            "   - 'nutrition' for fueling, hydration, or supplements.\n"
            "   - 'planning' for periodization, microcycles, or workload modeling.\n"
            "3. CITE EVIDENCE: Provide brief rationale for each assigned topic.\n"
            "4. SUMMARY: Produce 1-2 concise, high-density English sentences.\n\n"
            f"DOCUMENT TITLE: {title}\n"
            f"{summary_clause}"
            "DOCUMENT CONTENT:\n"
            '"""\n'
            f"{content}\n"
            '"""\n\n'
            "Respond with a JSON object matching the schema:\n"
        )

    def classify_content(
        self,
        content: str,
        title: str | None = None,
        existing_summary: str | None = None,
    ) -> DocumentTaggingResult:
        """Classify markdown content, handling heading-aware windowing when large."""
        doc_title = title or "Curated Document"
        full_text = content.strip()

        windows = _split_into_windows(full_text, self.max_window_chars)
        window_results: list[DocumentTaggingResult] = []

        schema_dict = DocumentTaggingResult.json_schema_for_taxonomy(self.taxonomy)

        for window in windows:
            prompt = self.build_prompt(
                title=doc_title,
                content=window,
                existing_summary=existing_summary,
            )
            raw_result = self.adapter.generate(prompt, schema=schema_dict)
            parsed = DocumentTaggingResult.model_validate(raw_result)
            window_results.append(parsed)

        return _consolidate_window_results(window_results, self.taxonomy)

    def classify_source(
        self,
        source: KnowledgeSource,
    ) -> DocumentTaggingResult:
        """Classify an in-memory KnowledgeSource domain entity."""
        return self.classify_content(
            content=source.body,
            title=source.title,
            existing_summary=source.summary,
        )

    def classify_document(
        self,
        file_path: Path | str,
        kb_dir: Path | None = None,
    ) -> DocumentTaggingResult:
        """Read and classify a markdown document from disk."""
        target_kb = kb_dir or self.kb_dir
        source = KnowledgeSource.from_path(
            Path(file_path), target_kb, self.taxonomy
        )
        return self.classify_content(
            content=source.body,
            title=source.title,
            existing_summary=source.summary,
        )

    def apply_tags_to_file(
        self,
        file_path: Path | str,
        dry_run: bool = False,
        kb_dir: Path | None = None,
    ) -> DocumentTaggingResult:
        """Classify a document and update frontmatter metadata on disk."""
        target_kb = kb_dir or self.kb_dir
        source = KnowledgeSource.from_path(
            Path(file_path), target_kb, self.taxonomy
        )
        result = self.classify_content(
            content=source.body,
            title=source.title,
            existing_summary=source.summary,
        )

        source.update_metadata(
            category=result.category,
            topics=result.topics,
            summary=result.summary,
        )
        source.save(dry_run=dry_run)
        return result


def classify_content(
    content: str,
    title: str | None = None,
    kb_dir: Path | None = None,
    adapter: ModelAdapter | None = None,
    taxonomy: TaxonomyRegistry | None = None,
) -> DocumentTaggingResult:
    """Classify markdown content string."""
    classifier = LocalLLMClassifier(adapter=adapter, taxonomy=taxonomy, kb_dir=kb_dir)
    return classifier.classify_content(content, title=title)


def classify_document(
    file_path: Path | str,
    kb_dir: Path | None = None,
    adapter: ModelAdapter | None = None,
    taxonomy: TaxonomyRegistry | None = None,
) -> DocumentTaggingResult:
    """Classify a markdown file on disk."""
    classifier = LocalLLMClassifier(adapter=adapter, taxonomy=taxonomy, kb_dir=kb_dir)
    return classifier.classify_document(file_path, kb_dir=kb_dir)


def apply_tags_to_file(
    file_path: Path | str,
    dry_run: bool = False,
    kb_dir: Path | None = None,
    adapter: ModelAdapter | None = None,
    taxonomy: TaxonomyRegistry | None = None,
) -> DocumentTaggingResult:
    """Classify and optionally apply tags to file on disk."""
    classifier = LocalLLMClassifier(adapter=adapter, taxonomy=taxonomy, kb_dir=kb_dir)
    return classifier.apply_tags_to_file(file_path, dry_run=dry_run, kb_dir=kb_dir)


# Compatibility alias
TopicTagger = LocalLLMClassifier
