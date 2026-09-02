"""Unit tests for translation utilities, language detection, and hybrid fallback."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from main.utils.translator import (
    HybridTranslator,
    TranslationLimitError,
    _translate_markdown_structured,
    detect_language,
)


class TestTranslator(unittest.TestCase):
    """Tests for language detection heuristic and hybrid fallback interface."""

    def test_detect_language_italian(self) -> None:
        it_text = (
            "In questo episodio parliamo di allenamento della soglia anaerobica, "
            "cinetica del VO2 e gestione del riscaldamento nel ciclismo."
        )
        self.assertEqual(detect_language(it_text), "it")

    def test_detect_language_english(self) -> None:
        en_text = (
            "In this episode we discuss anaerobic threshold training, "
            "VO2 kinetics, and warm-up management for endurance cycling."
        )
        self.assertEqual(detect_language(en_text), "en")

    def test_detect_language_empty_fallback(self) -> None:
        self.assertEqual(detect_language(""), "en")

    def test_detect_language_returns_unknown_for_unsupported_language(self) -> None:
        spanish_text = "Este episodio explica cómo mejorar el rendimiento deportivo."
        self.assertEqual(detect_language(spanish_text), "unknown")

    def test_hybrid_translator_skips_english_content(self) -> None:
        hybrid = HybridTranslator(deepl_key="", prefer_api=False)
        content = "The episode explains how cycling training improves power."
        result = hybrid.translate_markdown(content, target_lang="en")
        self.assertEqual(result, content)

    @patch("main.utils.translator.DeepLTranslator")
    def test_hybrid_translator_uses_api_when_successful(
        self, mock_deepl_class: MagicMock
    ) -> None:
        mock_deepl_instance = MagicMock()
        mock_deepl_instance.name = "DeepL"
        mock_deepl_instance.translate_markdown.return_value = (
            "---\ntitle: 'Translated via DeepL'\n---\n# Notes"
        )
        mock_deepl_class.return_value = mock_deepl_instance

        hybrid = HybridTranslator(deepl_key="test_key", prefer_api=True)
        it_content = (
            "---\ntitle: 'Episodio di ciclismo'\n---\n"
            "## Show Notes\nQuesto è un episodio italiano."
        )
        result = hybrid.translate_markdown(it_content, target_lang="en")
        self.assertIn("Translated via DeepL", result)
        mock_deepl_instance.translate_markdown.assert_called_once()

    @patch("main.utils.translator.LocalMLXTranslator")
    @patch("main.utils.translator.DeepLTranslator")
    def test_hybrid_translator_falls_back_on_rate_limit(
        self,
        mock_deepl_class: MagicMock,
        mock_local_class: MagicMock,
    ) -> None:
        mock_deepl_instance = MagicMock()
        mock_deepl_instance.name = "DeepL"
        mock_deepl_instance.translate_markdown.side_effect = TranslationLimitError(
            "Quota exceeded on DeepL"
        )
        mock_deepl_class.return_value = mock_deepl_instance

        hybrid = HybridTranslator(deepl_key="test_key", prefer_api=True)

        mock_local_instance = MagicMock()
        mock_local_instance.translate_markdown.return_value = (
            "---\ntitle: 'Translated via Local MLX'\n---\n# Notes"
        )
        mock_local_class.return_value = mock_local_instance

        it_content = (
            "---\ntitle: 'Episodio di ciclismo'\n---\n"
            "## Show Notes\nQuesto è un episodio italiano."
        )
        result = hybrid.translate_markdown(it_content, target_lang="en")
        self.assertIn("Translated via Local MLX", result)
        hybrid.translate_markdown(it_content, target_lang="en")
        self.assertEqual(mock_deepl_instance.translate_markdown.call_count, 1)
        self.assertEqual(mock_local_instance.translate_markdown.call_count, 2)

    @patch("main.utils.translator.AzureTranslator")
    def test_hybrid_translator_uses_azure_when_present(
        self, mock_azure_class: MagicMock
    ) -> None:
        mock_azure_instance = MagicMock()
        mock_azure_instance.name = "Microsoft Azure Translator"
        mock_azure_instance.translate_markdown.return_value = (
            "---\ntitle: 'Translated via Azure'\n---\n# Notes"
        )
        mock_azure_class.return_value = mock_azure_instance

        hybrid = HybridTranslator(azure_key="azure_test_key", prefer_api=True)
        it_content = (
            "---\ntitle: 'Episodio di ciclismo'\n---\n"
            "## Show Notes\nQuesto è un episodio italiano."
        )
        result = hybrid.translate_markdown(it_content, target_lang="en")
        self.assertIn("Translated via Azure", result)
        mock_azure_instance.translate_markdown.assert_called_once()

    @patch("main.utils.translator.DeepLTranslator")
    @patch("main.utils.translator.AzureTranslator")
    def test_hybrid_translator_tries_deepl_after_azure_limit(
        self,
        mock_azure_class: MagicMock,
        mock_deepl_class: MagicMock,
    ) -> None:
        azure = MagicMock(name="azure")
        azure.name = "Microsoft Azure Translator"
        azure.translate_markdown.side_effect = TranslationLimitError("quota")
        mock_azure_class.return_value = azure

        deepl = MagicMock(name="deepl")
        deepl.name = "DeepL"
        deepl.translate_markdown.return_value = "translated by DeepL"
        mock_deepl_class.return_value = deepl

        hybrid = HybridTranslator(azure_key="azure", deepl_key="deepl")
        result = hybrid.translate_markdown(
            "Questo episodio parla di allenamento e ciclismo.", target_lang="en"
        )

        self.assertEqual(result, "translated by DeepL")
        azure.translate_markdown.assert_called_once()
        deepl.translate_markdown.assert_called_once()

        hybrid.translate_markdown(
            "Questo episodio parla di allenamento e ciclismo.", target_lang="en"
        )
        azure.translate_markdown.assert_called_once()
        self.assertEqual(deepl.translate_markdown.call_count, 2)

    @patch("main.utils.translator.DeepLTranslator")
    @patch("main.utils.translator.AzureTranslator")
    def test_hybrid_translator_can_disable_azure(
        self,
        mock_azure_class: MagicMock,
        mock_deepl_class: MagicMock,
    ) -> None:
        deepl = MagicMock(name="deepl")
        deepl.name = "DeepL"
        deepl.translate_markdown.return_value = "translated by DeepL"
        mock_deepl_class.return_value = deepl

        hybrid = HybridTranslator(
            azure_key="azure",
            deepl_key="deepl",
            enable_azure=False,
        )
        result = hybrid.translate_markdown(
            "Questo episodio parla di allenamento e ciclismo.", target_lang="en"
        )

        self.assertEqual(result, "translated by DeepL")
        mock_azure_class.assert_not_called()
        deepl.translate_markdown.assert_called_once()

    def test_structured_translation_preserves_document_layout(self) -> None:
        translations = {
            "Titolo": ("A much longer translated title", "it"),
            "Riassunto": ("A much longer translated summary", "it"),
            "Note italiane": ("Translated show notes", "it"),
            "Testo breve.": ("Short transcript.", "it"),
        }
        markdown = """---
title: "Titolo"
summary: "Riassunto"
language: it
---

# Titolo

- **Listen on Spotify:** [Titolo](https://example.com)

---

## Show Notes

Note italiane

---

## Transcript

**[00:00]** Testo breve.
"""

        result = _translate_markdown_structured(
            translate_fn=translations.__getitem__,
            markdown_content=markdown,
            target_lang="en",
            source_lang="it",
        )

        self.assertIn('title: "A much longer translated title"', result)
        self.assertIn('summary: "A much longer translated summary"', result)
        self.assertIn("language: en", result)
        self.assertIn("original_language: it", result)
        self.assertIn("## Show Notes\n\nTranslated show notes", result)
        self.assertIn("**[00:00]** Short transcript.", result)
        self.assertEqual(result.count("## Transcript"), 1)
        self.assertNotIn("\n---\n\n---\n\n## Transcript", result)


if __name__ == "__main__":
    unittest.main()
