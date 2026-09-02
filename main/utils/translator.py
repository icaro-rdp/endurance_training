"""Translation and language detection utilities for knowledge base sources.

Provides translation capabilities using official SDKs for Microsoft Azure
Translator, DeepL, and local Apple Silicon MLX models (mlx-lm),
preserving endurance cycling domain terminology, markdown formatting, and
YAML frontmatter metadata with automatic rate-limit/quota fallback.
"""

from __future__ import annotations

import json
import logging
import os
import re
from collections.abc import Callable
from typing import Protocol

import azure.ai.translation.text as azure_translation
import deepl
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import AzureError, HttpResponseError

logger = logging.getLogger(__name__)

DEFAULT_LOCAL_MODEL_ID = "mlx-community/Qwen2.5-7B-Instruct-4bit"

ITALIAN_MARKERS = frozenset(
    {
        "il",
        "lo",
        "la",
        "i",
        "gli",
        "le",
        "un",
        "uno",
        "una",
        "di",
        "da",
        "con",
        "su",
        "per",
        "tra",
        "fra",
        "questo",
        "questa",
        "questi",
        "queste",
        "quello",
        "come",
        "cosa",
        "perché",
        "quando",
        "allenamento",
        "ciclismo",
        "prestazione",
        "soglia",
        "puntata",
        "episodio",
    }
)
ENGLISH_MARKERS = frozenset(
    {
        "the",
        "and",
        "to",
        "of",
        "is",
        "that",
        "for",
        "it",
        "as",
        "was",
        "with",
        "on",
        "at",
        "by",
        "this",
        "from",
        "they",
        "we",
        "which",
        "training",
        "cycling",
        "power",
        "threshold",
        "episode",
    }
)


class TranslationError(Exception):
    """Base exception for translation failures."""


class TranslationProviderError(TranslationError):
    """Raised when a cloud translation provider cannot complete a request."""


class TranslationLimitError(TranslationProviderError):
    """Raised when a cloud provider rejects work due to quota or rate limits."""


class MarkdownTranslator(Protocol):
    """Contract implemented by translation providers."""

    name: str

    def translate_markdown(
        self,
        markdown_content: str,
        target_lang: str = "en",
        source_lang: str | None = None,
    ) -> str:
        """Translate a Markdown document while preserving its structure."""


def detect_language(text: str) -> str:
    """Distinguish likely Italian or English text.

    Uses common stopwords as a fast, zero-dependency heuristic. Ambiguous text
    is reported as ``unknown`` so cloud providers can use their own detection.

    Args:
        text: Sample string to detect language for.

    Returns:
        ``it``, ``en``, or ``unknown``. Empty input is treated as English.
    """
    sample = text.lower()[:2000]
    words = re.findall(r"\b[a-zA-Zàèéìòùáéíóú]+\b", sample)
    if not words:
        return "en"

    italian_count = sum(1 for word in words if word in ITALIAN_MARKERS)
    english_count = sum(1 for word in words if word in ENGLISH_MARKERS)

    if italian_count >= 2 and italian_count > english_count:
        return "it"
    if english_count >= 2 and english_count > italian_count:
        return "en"
    return "unknown"


def _set_frontmatter_field(markdown_content: str, field: str, value: str) -> str:
    """Set or append one field in the leading YAML frontmatter block."""
    frontmatter_match = re.match(
        r"(?P<opening>\A---\s*\n)(?P<body>.*?)(?P<closing>\n---(?:\n|\Z))",
        markdown_content,
        re.DOTALL,
    )
    if frontmatter_match is None:
        return markdown_content

    body = frontmatter_match.group("body")
    field_line = f"{field}: {value}"
    field_pattern = rf"^{re.escape(field)}:\s*.*$"
    if re.search(field_pattern, body, re.MULTILINE):
        updated_body = re.sub(field_pattern, field_line, body, flags=re.MULTILINE)
    else:
        updated_body = f"{body.rstrip()}\n{field_line}"

    return (
        markdown_content[: frontmatter_match.start()]
        + frontmatter_match.group("opening")
        + updated_body
        + frontmatter_match.group("closing")
        + markdown_content[frontmatter_match.end() :]
    )


def _replace_show_notes(header: str, translated_notes: str) -> str:
    """Replace Show Notes content without relying on offsets after other edits."""
    notes_pattern = r"(## Show Notes\s*\n\s*)(.*?)(?=\n---|\Z)"
    return re.sub(
        notes_pattern,
        lambda match: f"{match.group(1)}{translated_notes}",
        header,
        count=1,
        flags=re.DOTALL,
    )


def _translate_markdown_structured(
    translate_fn: Callable[[str], tuple[str, str]],
    markdown_content: str,
    target_lang: str = "en",
    source_lang: str | None = None,
) -> str:
    """Translate generated podcast Markdown while preserving its structure.

    Args:
        translate_fn: Callback accepting text and returning (translated, detected_lang).
        markdown_content: Full markdown content.
        target_lang: Destination language code.
        source_lang: Optional source language code.
    Returns:
        Structured translated markdown string.
    """
    detected_lang = source_lang or detect_language(markdown_content)
    if detected_lang.lower() == target_lang.lower():
        return markdown_content

    if "## Transcript" in markdown_content:
        header_part, transcript_part = markdown_content.split("## Transcript", 1)
        header_part = re.sub(r"\n---\s*$", "", header_part.rstrip())
        transcript_part = transcript_part.strip()

        title_match = re.search(
            r'^title:\s*["\']?(.*?)["\']?$', header_part, re.MULTILINE
        )
        orig_title = title_match.group(1).strip() if title_match else ""

        summary_match = re.search(
            r'^summary:\s*["\']?(.*?)["\']?$', header_part, re.MULTILINE
        )
        orig_summary = summary_match.group(1).strip() if summary_match else ""

        notes_match = re.search(r"## Show Notes\s*\n\s*(.*)\Z", header_part, re.DOTALL)
        orig_notes = notes_match.group(1).strip() if notes_match else ""

        translated_title, det_lang = (
            translate_fn(orig_title) if orig_title else ("", detected_lang)
        )
        translated_summary, _ = (
            translate_fn(orig_summary) if orig_summary else ("", detected_lang)
        )
        translated_notes, _ = (
            translate_fn(orig_notes) if orig_notes else ("", detected_lang)
        )

        updated_header = _replace_show_notes(header_part, translated_notes)
        if orig_title:
            updated_header = re.sub(
                rf"^#\s+{re.escape(orig_title)}",
                f"# {translated_title}",
                updated_header,
                flags=re.MULTILINE,
            )
            updated_header = updated_header.replace(
                f"[{orig_title}]", f"[{translated_title}]"
            )
            updated_header = _set_frontmatter_field(
                updated_header,
                "title",
                json.dumps(translated_title, ensure_ascii=False),
            )

        if orig_summary:
            updated_header = _set_frontmatter_field(
                updated_header,
                "summary",
                json.dumps(translated_summary, ensure_ascii=False),
            )

        updated_header = _set_frontmatter_field(
            updated_header, "language", target_lang.lower()
        )
        updated_header = _set_frontmatter_field(
            updated_header, "original_language", det_lang.lower()
        )

        if not transcript_part or "not available" in transcript_part.lower():
            return (
                f"{updated_header}\n\n---\n\n## Transcript\n\n"
                f"*Spoken transcript not available via Spotify for this episode.*"
            )

        paragraphs = [p.strip() for p in transcript_part.split("\n\n") if p.strip()]
        translated_paragraphs: list[str] = []

        for paragraph in paragraphs:
            ts_match = re.match(
                r"^(\*\*\[\d{2}:\d{2}(?::\d{2})?\]\*\*)\s*(.*)",
                paragraph,
                re.DOTALL,
            )
            if ts_match:
                timestamp = ts_match.group(1)
                body_text = ts_match.group(2)
                translated_body, _ = translate_fn(body_text)
                translated_paragraphs.append(f"{timestamp} {translated_body}")
            else:
                translated_paragraph, _ = translate_fn(paragraph)
                translated_paragraphs.append(translated_paragraph)

        full_transcript = "\n\n".join(translated_paragraphs)
        return f"{updated_header}\n\n---\n\n## Transcript\n\n{full_transcript}"

    translated_all, _ = translate_fn(markdown_content)
    return translated_all


class LocalMLXTranslator:
    """Translates Markdown content using local MLX models on Apple Silicon."""

    def __init__(
        self,
        model_id: str = DEFAULT_LOCAL_MODEL_ID,
    ) -> None:
        """Initializes the local MLX model and tokenizer.

        Args:
            model_id: HuggingFace model repo ID formatted for MLX.
        """
        try:
            from mlx_lm import generate, load

            self._load_fn = load
            self._generate_fn = generate
        except ImportError as exc:
            raise RuntimeError(
                "mlx-lm is required for local translation. "
                "Install it with: uv sync --extra local-ai"
            ) from exc

        self.model_id = model_id
        logger.info("Loading local MLX translation model: %s", model_id)
        loaded_model = self._load_fn(model_id)
        self.model = loaded_model[0]
        self.tokenizer = loaded_model[1]

    def _generate_text(self, prompt_text: str, max_tokens: int = 2500) -> str:
        """Helper to invoke local MLX generation with chat template."""
        messages = [{"role": "user", "content": prompt_text}]
        # mlx-lm's tokenizer wrapper does not publish type information for this API.
        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )  # type: ignore[no-untyped-call]
        response = self._generate_fn(
            self.model,
            self.tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            verbose=False,
        )
        clean = response.strip()
        if clean.startswith("```markdown"):
            clean = clean[len("```markdown") :].strip()
        if clean.startswith("```"):
            clean = clean[3:].strip()
        if clean.endswith("```"):
            clean = clean[:-3].strip()
        return clean

    def translate_markdown(
        self,
        markdown_content: str,
        target_lang: str = "en",
        source_lang: str | None = None,
        max_tokens: int = 3500,
    ) -> str:
        """Translates an episode markdown document into the target language.

        Preserves YAML frontmatter structure, cycling terminology, timestamps,
        and section headers. Handles long transcripts by chunking.

        Args:
            markdown_content: Complete markdown file string including frontmatter.
            target_lang: Destination ISO 639-1 language code (default: 'en').
            source_lang: Optional source language code (detected if None).
            max_tokens: Maximum tokens for generation output.

        Returns:
            Translated markdown document with updated language frontmatter.
        """
        detected_lang = source_lang or detect_language(markdown_content)
        if detected_lang.lower() == target_lang.lower():
            return markdown_content

        # Split into metadata/notes and transcript body if long transcript exists
        if "## Transcript" in markdown_content:
            parts = markdown_content.split("## Transcript", 1)
            header_part = parts[0].strip()
            transcript_part = parts[1].strip()

            # Translate header (frontmatter, title, show notes)
            header_prompt = (
                "You are an expert endurance sports physiology and cycling coach "
                "translator.\n"
                f"Translate this podcast episode header & show notes from "
                f"{detected_lang.upper()} into natural, accurate "
                f"{target_lang.upper()}.\n"
                "Key rules:\n"
                "1. Accurately translate cycling/endurance science terms "
                '(e.g. "Riscaldamento" -> "Warm-up", '
                '"cinetica del VO₂" -> "VO₂ kinetics", '
                '"soglia anaerobica" -> "anaerobic threshold", '
                '"rulli" -> "turbo trainers").\n'
                f"2. Maintain YAML frontmatter with `language: {target_lang}` "
                f"and `original_language: {detected_lang}`.\n"
                "3. Preserve all URLs, durations, dates, and markdown headers.\n"
                "4. Output ONLY the translated markdown header and show notes.\n\n"
                f"Original:\n```markdown\n{header_part}\n```\n"
            )
            translated_header = self._generate_text(
                header_prompt, max_tokens=max_tokens
            )

            # If transcript is empty or unavailable placeholder
            if not transcript_part or "not available" in transcript_part.lower():
                return (
                    f"{translated_header}\n\n---\n\n## Transcript\n\n"
                    f"*Spoken transcript not available via Spotify for this episode.*"
                )

            # Chunk transcript paragraphs (e.g. ~6 timestamped paragraphs per chunk)
            paragraphs = [p.strip() for p in transcript_part.split("\n\n") if p.strip()]
            chunk_size = 6
            translated_paragraphs: list[str] = []
            for i in range(0, len(paragraphs), chunk_size):
                chunk_items = paragraphs[i : i + chunk_size]
                chunk_text = "\n\n".join(chunk_items)
                transcript_prompt = (
                    "You are an expert endurance cycling coach translator.\n"
                    f"Translate the following podcast transcript segment from "
                    f"{detected_lang.upper()} into natural, accurate "
                    f"{target_lang.upper()}.\n"
                    "Key rules:\n"
                    "1. Accurately translate cycling physiology terms (VO₂ kinetics, "
                    "anaerobic threshold, turbo trainer, cadence, etc.).\n"
                    "2. PRESERVE all timestamps in bold brackets like **[00:00]**, "
                    "**[01:33]** exactly at the beginning of paragraphs.\n"
                    "3. Output ONLY the translated paragraphs separated by "
                    "double newlines.\n\n"
                    f"Original:\n{chunk_text}\n"
                )
                translated_chunk = self._generate_text(
                    transcript_prompt, max_tokens=max_tokens
                )
                translated_paragraphs.append(translated_chunk)

            full_transcript = "\n\n".join(translated_paragraphs)
            return f"{translated_header}\n\n---\n\n## Transcript\n\n{full_transcript}"

        # Otherwise translate whole content in one prompt
        full_prompt = (
            "You are an expert endurance sports physiology and cycling coach "
            "translator.\n"
            f"Translate the following podcast episode markdown note from "
            f"{detected_lang.upper()} into natural, accurate, idiomatic "
            f"{target_lang.upper()}.\n"
            "Key rules:\n"
            "1. Accurately translate cycling and endurance science terminology "
            '(e.g. "Riscaldamento" -> "Warm-up", '
            '"cinetica del VO₂" -> "VO₂ kinetics", '
            '"soglia anaerobica" -> "anaerobic threshold", '
            '"rulli" -> "turbo trainers").\n'
            f"2. Maintain YAML frontmatter with `language: {target_lang}` "
            f"and `original_language: {detected_lang}`.\n"
            "3. Preserve all URLs, durations, dates, and markdown headers.\n"
            "4. Output ONLY the translated markdown.\n\n"
            f"Original Markdown:\n```markdown\n{markdown_content}\n```\n"
        )
        return self._generate_text(full_prompt, max_tokens=max_tokens)


class AzureTranslator:
    """Translates text and markdown via official Microsoft Azure Translator SDK."""

    name = "Microsoft Azure Translator"

    def __init__(
        self,
        api_key: str | None = None,
        region: str | None = None,
        endpoint: str | None = None,
    ) -> None:
        """Initializes official Azure TextTranslationClient.

        Args:
            api_key: Azure Translator Subscription Key (AZURE_TRANSLATOR_KEY).
            region: Service Region (AZURE_TRANSLATOR_REGION, default: 'global').
            endpoint: Custom endpoint URL if specified.
        """
        self.api_key = api_key or os.environ.get("AZURE_TRANSLATOR_KEY", "")
        self.region = (
            region or os.environ.get("AZURE_TRANSLATOR_REGION", "") or "global"
        )
        if not self.api_key:
            raise ValueError(
                "Azure Translator key required. Set AZURE_TRANSLATOR_KEY in .env."
            )
        base = endpoint or "https://api.cognitive.microsofttranslator.com"
        credential = AzureKeyCredential(self.api_key)
        self.client = azure_translation.TextTranslationClient(
            endpoint=base,
            credential=credential,
            region=self.region if self.region != "global" else None,
        )

    def translate_text(
        self,
        text: str,
        target_lang: str = "en",
        source_lang: str | None = None,
    ) -> tuple[str, str]:
        """Translates a text string via Azure Translator SDK.

        Args:
            text: Text string to translate.
            target_lang: Target language code (e.g. 'en').
            source_lang: Optional source language code (e.g. 'it').

        Returns:
            Tuple of (translated_text, detected_source_language).
        """
        if not text.strip():
            return text, source_lang or "unknown"

        try:
            response = self.client.translate(
                body=[text],
                to_language=[target_lang],
                from_language=source_lang,
            )
        except HttpResponseError as exc:
            if exc.status_code in {403, 429}:
                raise TranslationLimitError(str(exc)) from exc
            raise TranslationProviderError(str(exc)) from exc
        except AzureError as exc:
            raise TranslationProviderError(str(exc)) from exc
        if not response:
            raise TranslationProviderError("Azure returned no response")

        first_res = response[0]
        detected = (
            getattr(first_res.detected_language, "language", None)
            if hasattr(first_res, "detected_language") and first_res.detected_language
            else (source_lang or "unknown")
        )
        translations = getattr(first_res, "translations", [])
        if translations:
            return str(translations[0].text), str(detected)
        raise TranslationProviderError("Azure returned no translation")

    def translate_markdown(
        self,
        markdown_content: str,
        target_lang: str = "en",
        source_lang: str | None = None,
    ) -> str:
        """Translates markdown document via Azure Translator preserving structure."""
        return _translate_markdown_structured(
            translate_fn=lambda t: self.translate_text(
                t, target_lang=target_lang, source_lang=source_lang
            ),
            markdown_content=markdown_content,
            target_lang=target_lang,
            source_lang=source_lang,
        )


class DeepLTranslator:
    """Translates text and markdown via official DeepL SDK."""

    name = "DeepL"

    def __init__(self, api_key: str | None = None) -> None:
        """Initializes official DeepL Translator client.

        Args:
            api_key: DeepL Authentication Key. Reads DEEPL_API_KEY from env if None.
        """
        self.api_key = api_key or os.environ.get("DEEPL_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "DeepL API key required. Set DEEPL_API_KEY in .env or pass api_key."
            )
        self.translator = deepl.Translator(self.api_key)

    def translate_text(
        self,
        text: str,
        target_lang: str = "EN-US",
        source_lang: str | None = None,
    ) -> tuple[str, str]:
        """Translates a text block via DeepL SDK.

        Args:
            text: Text string to translate.
            target_lang: Target language code (e.g. 'EN-US', 'EN-GB', 'IT').
            source_lang: Optional source language code (e.g. 'IT').

        Returns:
            Tuple of (translated_text, detected_source_language).
        """
        if not text.strip():
            return text, source_lang or "unknown"

        try:
            result = self.translator.translate_text(
                text,
                target_lang=target_lang.upper(),
                source_lang=source_lang.upper() if source_lang else None,
            )
        except (
            deepl.QuotaExceededException,
            deepl.TooManyRequestsException,
            deepl.AuthorizationException,
        ) as exc:
            raise TranslationLimitError(str(exc)) from exc
        except deepl.DeepLException as exc:
            raise TranslationProviderError(str(exc)) from exc

        if isinstance(result, list):
            if not result:
                raise TranslationProviderError("DeepL returned no translation")
            result = result[0]
        detected = (
            getattr(result, "detected_source_lang", source_lang or "unknown")
            if hasattr(result, "detected_source_lang")
            else "unknown"
        )
        return str(result.text), str(detected)

    def translate_markdown(
        self,
        markdown_content: str,
        target_lang: str = "en",
        source_lang: str | None = None,
    ) -> str:
        """Translates a full markdown document via DeepL SDK preserving structure."""
        target_deepl = "EN-US" if target_lang.lower() == "en" else target_lang.upper()
        return _translate_markdown_structured(
            translate_fn=lambda t: self.translate_text(
                t, target_lang=target_deepl, source_lang=source_lang
            ),
            markdown_content=markdown_content,
            target_lang=target_lang,
            source_lang=source_lang,
        )


class HybridTranslator:
    """Translate through configured cloud providers, then local MLX."""

    def __init__(
        self,
        azure_key: str | None = None,
        azure_region: str | None = None,
        deepl_key: str | None = None,
        local_model_id: str = DEFAULT_LOCAL_MODEL_ID,
        prefer_api: bool = True,
        enable_azure: bool = True,
        enable_deepl: bool = True,
    ) -> None:
        """Initialize the ordered translation fallback pipeline.

        Args:
            azure_key: Azure Translator Key (reads AZURE_TRANSLATOR_KEY).
            azure_region: Azure Region (reads AZURE_TRANSLATOR_REGION).
            deepl_key: DeepL Key (reads DEEPL_API_KEY).
            local_model_id: HuggingFace model repo ID for local MLX fallback.
            prefer_api: Whether to try cloud APIs first before local MLX.
            enable_azure: Whether Azure may be added to the cloud pipeline.
            enable_deepl: Whether DeepL may be added to the cloud pipeline.
        """
        self.local_model_id = local_model_id
        self._local: LocalMLXTranslator | None = None
        self._cloud_translators: list[MarkdownTranslator] = []

        azure_secret = azure_key or os.environ.get("AZURE_TRANSLATOR_KEY", "")
        deepl_secret = deepl_key or os.environ.get("DEEPL_API_KEY", "")

        if prefer_api and enable_azure and azure_secret:
            try:
                self._cloud_translators.append(
                    AzureTranslator(api_key=azure_secret, region=azure_region)
                )
            except (AzureError, ValueError) as exc:
                logger.warning("Azure setup skipped: %s", exc)

        if prefer_api and enable_deepl and deepl_secret:
            try:
                self._cloud_translators.append(DeepLTranslator(api_key=deepl_secret))
            except (deepl.DeepLException, ValueError) as exc:
                logger.warning("DeepL setup skipped: %s", exc)

    def _get_local(self) -> LocalMLXTranslator:
        """Lazy loader for local MLX model."""
        if self._local is None:
            self._local = LocalMLXTranslator(model_id=self.local_model_id)
        return self._local

    def translate_markdown(
        self,
        markdown_content: str,
        target_lang: str = "en",
        source_lang: str | None = None,
    ) -> str:
        """Translates markdown with automatic rate limit / quota fallback.

        Args:
            markdown_content: Complete markdown document string.
            target_lang: Target language code (default: 'en').
            source_lang: Optional source language code (detected if None).

        Returns:
            Translated markdown content.
        """
        detected_language = source_lang or detect_language(markdown_content)
        if detected_language.lower() == target_lang.lower():
            return markdown_content

        cloud_source_language = (
            None if detected_language == "unknown" else detected_language
        )
        for translator in tuple(self._cloud_translators):
            try:
                return translator.translate_markdown(
                    markdown_content,
                    target_lang=target_lang,
                    source_lang=cloud_source_language,
                )
            except TranslationLimitError as exc:
                logger.warning(
                    "%s quota or rate limit reached: %s",
                    translator.name,
                    exc,
                )
                self._cloud_translators.remove(translator)
            except TranslationProviderError as exc:
                logger.warning(
                    "%s translation failed: %s",
                    translator.name,
                    exc,
                )

        return self._get_local().translate_markdown(
            markdown_content,
            target_lang=target_lang,
            source_lang=detected_language,
        )
