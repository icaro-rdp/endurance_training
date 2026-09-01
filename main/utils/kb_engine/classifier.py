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

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    GetCoreSchemaHandler,
    field_validator,
)
from pydantic_core import CoreSchema, core_schema

from main.utils.kb_engine.errors import (
    MissingDependencyError,
    ModelConnectionError,
    ModelInferenceError,
)
from main.utils.kb_engine.frontmatter import KnowledgeSource
from main.utils.kb_engine.taxonomy import TaxonomyRegistry

logger = logging.getLogger(__name__)

DEFAULT_LOCAL_MODEL = "mlx-community/Qwen2.5-7B-Instruct-4bit"
# Model backends return untyped JSON; Pydantic validates it at the classifier seam.
ModelPayload = dict[str, Any]


class CanonicalCategory(str):
    """Category value constrained by the canonical taxonomy."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: object,
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Build validation and JSON Schema from the taxonomy registry."""
        return core_schema.no_info_after_validator_function(
            cls,
            core_schema.literal_schema(TaxonomyRegistry.CANONICAL_CATEGORIES),
        )


class CanonicalTopic(str):
    """Topic value constrained by the canonical taxonomy."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: object,
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Build validation and JSON Schema from the taxonomy registry."""
        return core_schema.no_info_after_validator_function(
            cls,
            core_schema.literal_schema(list(TaxonomyRegistry.CANONICAL_TOPICS)),
        )


class DocumentTaggingResult(BaseModel):
    """Structured data contract for model topic auto-tagging output."""

    model_config = ConfigDict(extra="forbid")

    category: CanonicalCategory = Field(
        description="The primary operational macro-category (resolved bottom-up)."
    )
    topics: list[CanonicalTopic] = Field(
        description="All specific canonical topics discussed substantively in depth.",
        min_length=1,
        max_length=8,
    )
    summary: str = Field(
        description=(
            "One or two faithful, high-density English sentences summarizing "
            "key takeaways."
        ),
        min_length=1,
    )
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    topic_evidence: dict[str, str] = Field(default_factory=dict)

    @field_validator("topics")
    @classmethod
    def deduplicate_topics(
        cls,
        topics: list[CanonicalTopic],
    ) -> list[CanonicalTopic]:
        """Deduplicate canonical topics while preserving their order."""
        deduped: list[CanonicalTopic] = []
        for topic in topics:
            if topic not in deduped:
                deduped.append(topic)
        return deduped

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, summary: str) -> str:
        """Require a non-empty summary containing no more than two sentences."""
        normalized_summary = summary.strip()
        if not normalized_summary:
            raise ValueError("summary must not be blank")

        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", normalized_summary)
        if len(sentences) > 2:
            raise ValueError("summary must contain no more than two sentences")
        return normalized_summary


class ModelAdapter(Protocol):
    """Protocol seam for local LLM inference backends."""

    def generate(self, prompt: str, schema: type[BaseModel]) -> ModelPayload:
        """Generate structured JSON response adhering to schema."""
        ...


class FakeModelAdapter:
    """Deterministic model adapter for fast, reproducible unit tests."""

    def __init__(
        self,
        default_response: ModelPayload | None = None,
        responses_by_keyword: dict[str, ModelPayload] | None = None,
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
        self.last_schema: type[BaseModel] | None = None

    def generate(self, prompt: str, schema: type[BaseModel]) -> ModelPayload:
        """Return the configured deterministic response."""
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
    ) -> None:
        self.model_name = model_name
        self.max_tokens = max_tokens
        # Optional MLX/Outlines packages do not expose a stable shared model type.
        self._model: Any = None
        self._tokenizer: Any = None
        self._structured_model: Any = None

    def _ensure_loaded(self) -> None:
        if self._structured_model is not None:
            return

        try:
            import mlx_lm
            import outlines
        except ImportError as exc:
            raise MissingDependencyError(
                "mlx-lm and outlines",
                "Install using: uv sync --extra local-ai",
            ) from exc

        try:
            loaded = mlx_lm.load(self.model_name)
            model = loaded[0]
            tokenizer = loaded[1]
            structured_model = outlines.from_mlxlm(model, tokenizer)
        except (OSError, RuntimeError, ValueError) as exc:
            raise ModelInferenceError(
                f"Failed to load MLX model '{self.model_name}': {exc}"
            ) from exc

        self._model = model
        self._tokenizer = tokenizer
        self._structured_model = structured_model

    def generate(self, prompt: str, schema: type[BaseModel]) -> ModelPayload:
        """Generate JSON while masking tokens that violate a Pydantic schema."""
        self._ensure_loaded()
        schema_str = json.dumps(schema.model_json_schema())
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

        try:
            raw_output = self._structured_model(
                formatted_prompt,
                output_type=schema,
                max_tokens=self.max_tokens,
            )
        except (OSError, RuntimeError, ValueError) as exc:
            raise ModelInferenceError(f"MLX generation failed: {exc}") from exc

        if isinstance(raw_output, BaseModel):
            return raw_output.model_dump()
        if not isinstance(raw_output, str):
            raise ModelInferenceError(
                f"MLX returned unsupported output type: {type(raw_output).__name__}"
            )
        return _extract_json_from_text(raw_output)


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

    def generate(self, prompt: str, schema: type[BaseModel]) -> ModelPayload:
        """Generate a JSON response through Ollama's schema format contract."""
        schema_json = schema.model_json_schema()

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
        except (TimeoutError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ModelInferenceError(f"Ollama request error: {exc}") from exc

        content = resp_data.get("message", {}).get("content", "")
        if not content:
            raise ModelInferenceError("Empty response received from Ollama.")

        return _extract_json_from_text(content)


def create_model_adapter(
    backend: str,
    model_name: str | None = None,
    ollama_host: str = "http://localhost:11434",
) -> ModelAdapter:
    """Create a supported local model adapter from CLI configuration."""
    if backend == "mlx":
        return MLXAdapter(model_name=model_name or DEFAULT_LOCAL_MODEL)
    if backend == "ollama":
        return OllamaAdapter(
            model_name=model_name or "qwen2.5:7b",
            host=ollama_host,
        )
    raise ValueError(f"Unsupported local model backend: {backend}")


def _extract_json_from_text(text: str) -> ModelPayload:
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
    if max_window_chars <= 0:
        raise ValueError("max_window_chars must be positive")
    if len(full_text) <= max_window_chars:
        return [full_text]

    sections = re.split(r"(?=(?:\n|^)#{1,3}\s+)", full_text)
    windows: list[str] = []
    current_chunk = ""
    overlap_chars = min(500, max_window_chars // 5)
    window_step = max_window_chars - overlap_chars

    for section in sections:
        if not section:
            continue
        if len(current_chunk) + len(section) <= max_window_chars:
            current_chunk += section
        else:
            if current_chunk:
                windows.append(current_chunk)
            if len(section) > max_window_chars:
                for i in range(0, len(section), window_step):
                    part = section[i : i + max_window_chars]
                    if part:
                        windows.append(part)
                current_chunk = ""
            else:
                current_chunk = section

    if current_chunk and (not windows or windows[-1] != current_chunk):
        windows.append(current_chunk)

    return windows if windows else [full_text]


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
            category_definition = self.taxonomy.category_definition(cat)
            if category_definition:
                taxonomy_lines.append(f"  Definition: {category_definition}")
            for topic in topics_by_cat.get(cat, []):
                defn = self.taxonomy.topic_definition(topic)
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
            f"CANONICAL TAXONOMY ({len(self.taxonomy.topics())} Topics across "
            f"{len(categories)} Categories):\n"
            f"{taxonomy_str}\n"
            "RULES:\n"
            "1. NON-HIERARCHICAL TOPIC SELECTION: Select 1 to 8 canonical topics "
            "from across the full vocabulary substantively discussed.\n"
            "2. BOTTOM-UP CATEGORY RESOLUTION: After assigning topics, derive the "
            "single category whose canonical definition best matches the document's "
            "operational focus.\n"
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

        for window in windows:
            prompt = self.build_prompt(
                title=doc_title,
                content=window,
                existing_summary=existing_summary,
            )
            raw_result = self.adapter.generate(prompt, schema=DocumentTaggingResult)
            parsed = DocumentTaggingResult.model_validate(raw_result)
            window_results.append(parsed)

        if len(window_results) == 1:
            return window_results[0]

        consolidation_prompt = self._build_consolidation_prompt(window_results)
        consolidated = self.adapter.generate(
            consolidation_prompt,
            schema=DocumentTaggingResult,
        )
        return DocumentTaggingResult.model_validate(consolidated)

    def _build_consolidation_prompt(
        self,
        window_results: list[DocumentTaggingResult],
    ) -> str:
        serialized_results = json.dumps(
            [result.model_dump(mode="json") for result in window_results],
            indent=2,
        )
        return (
            "CONSOLIDATE WINDOW RESULTS for one complete document.\n\n"
            "Use every window result, including late-window evidence. Select the "
            "1-8 strongest substantive canonical topics across the document. Then "
            "derive the single primary category from the document's operational "
            "focus; do not use a fixed category priority or a simple topic-count "
            "tie-break. Produce one or two faithful summary sentences that cover "
            "the document-wide conclusions, including material late conclusions. "
            "Keep evidence only for selected topics.\n\n"
            f"WINDOW RESULTS:\n{serialized_results}\n"
        )

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
        source = KnowledgeSource.from_path(Path(file_path), target_kb, self.taxonomy)
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
        source = KnowledgeSource.from_path(Path(file_path), target_kb, self.taxonomy)
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
