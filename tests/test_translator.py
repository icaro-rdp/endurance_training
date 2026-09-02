"""Unit tests for translation utilities and language detection."""

from __future__ import annotations

import unittest

from main.utils.translator import detect_language


class TestTranslator(unittest.TestCase):
    """Tests for language detection heuristic and translator interface."""

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


if __name__ == "__main__":
    unittest.main()
