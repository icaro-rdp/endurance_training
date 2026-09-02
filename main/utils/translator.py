"""Translation and language detection utilities for knowledge base sources.

Provides translation capabilities using local Apple Silicon MLX models (e.g.
Qwen2.5-7B-Instruct) or external APIs (DeepL), preserving endurance cycling
domain terminology, markdown formatting, and YAML frontmatter metadata.
"""

from __future__ import annotations

import os
import re
from typing import Any

import requests


def detect_language(text: str) -> str:
    """Detects the ISO 639-1 language code of a text snippet.

    Uses character distributions and common stopwords as a fast, zero-dependency
    heuristic for Italian vs English and other common European languages.

    Args:
        text: Sample string to detect language for.

    Returns:
        ISO 639-1 language code (e.g. 'it', 'en', 'es', 'de', 'fr').
    """
    sample = text.lower()[:2000]
    words = re.findall(r"\b[a-zA-Zàèéìòùáéíóú]+\b", sample)
    if not words:
        return "en"

    italian_markers = {
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
        "a",
        "da",
        "in",
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
    english_markers = {
        "the",
        "and",
        "to",
        "of",
        "a",
        "in",
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

    it_count = sum(1 for w in words if w in italian_markers)
    en_count = sum(1 for w in words if w in english_markers)

    if it_count > en_count:
        return "it"
    return "en"


class LocalMLXTranslator:
    """Translates Markdown content using local MLX models on Apple Silicon."""

    def __init__(
        self,
        model_id: str = "mlx-community/Qwen2.5-7B-Instruct-4bit",
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
        print(f"Loading local MLX translation model: {model_id}...")
        self.model, self.tokenizer = self._load_fn(model_id)

    def _generate_text(self, prompt_text: str, max_tokens: int = 2500) -> str:
        """Helper to invoke local MLX generation with chat template."""
        messages = [{"role": "user", "content": prompt_text}]
        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
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
        if detected_lang == target_lang:
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
            if (
                not transcript_part
                or "not available" in transcript_part.lower()
                or len(transcript_part) < 100
            ):
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


class DeepLTranslator:
    """Translates text via the official DeepL API."""

    def __init__(self, api_key: str | None = None) -> None:
        """Initializes DeepL API client with key.

        Args:
            api_key: DeepL Authentication Key. Reads DEEPL_API_KEY from env if None.
        """
        self.api_key = api_key or os.environ.get("DEEPL_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "DeepL API key required. Set DEEPL_API_KEY in .env or pass api_key."
            )
        self.base_url = (
            "https://api-free.deepl.com/v2/translate"
            if self.api_key.endswith(":fx")
            else "https://api.deepl.com/v2/translate"
        )

    def translate_text(
        self,
        text: str,
        target_lang: str = "EN-US",
        source_lang: str | None = None,
    ) -> tuple[str, str]:
        """Translates a text block via DeepL API.

        Args:
            text: Text string to translate.
            target_lang: Target language code (e.g. 'EN-US', 'EN-GB', 'IT').
            source_lang: Optional source language code (e.g. 'IT').

        Returns:
            Tuple of (translated_text, detected_source_language).
        """
        headers = {"Authorization": f"DeepL-Auth-Key {self.api_key}"}
        payload: dict[str, Any] = {
            "text": [text],
            "target_lang": target_lang.upper(),
        }
        if source_lang:
            payload["source_lang"] = source_lang.upper()

        resp = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        translations = data.get("translations", [])
        if not translations:
            return text, "unknown"

        first = translations[0]
        return first.get("text", text), first.get("detected_source_language", "unknown")
