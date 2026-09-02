"""Unit tests for Spotify transcript scraper utilities and ID extraction."""

from __future__ import annotations

import unittest

from main.spotify_transcript_scraper import extract_spotify_id, format_ms


class TestSpotifyTranscriptScraper(unittest.TestCase):
    """Tests for ID extraction and parsing logic."""

    def test_extract_raw_show_id(self) -> None:
        raw_id = "5IHj4utnRlTNcCCoxyinkx"
        self.assertEqual(extract_spotify_id(raw_id), "5IHj4utnRlTNcCCoxyinkx")
        self.assertEqual(
            extract_spotify_id(raw_id, expected_type="show"),
            "5IHj4utnRlTNcCCoxyinkx",
        )

    def test_extract_show_url_with_query_params(self) -> None:
        url = "https://open.spotify.com/show/5IHj4utnRlTNcCCoxyinkx?si=db5fcba3c59e4526"
        self.assertEqual(extract_spotify_id(url), "5IHj4utnRlTNcCCoxyinkx")
        self.assertEqual(
            extract_spotify_id(url, expected_type="show"),
            "5IHj4utnRlTNcCCoxyinkx",
        )

    def test_extract_show_url_without_query_params(self) -> None:
        url = "https://open.spotify.com/show/5IHj4utnRlTNcCCoxyinkx"
        self.assertEqual(extract_spotify_id(url), "5IHj4utnRlTNcCCoxyinkx")
        self.assertEqual(
            extract_spotify_id(url, expected_type="show"),
            "5IHj4utnRlTNcCCoxyinkx",
        )

    def test_extract_show_url_with_trailing_slash(self) -> None:
        url = "https://open.spotify.com/show/5IHj4utnRlTNcCCoxyinkx/"
        self.assertEqual(extract_spotify_id(url), "5IHj4utnRlTNcCCoxyinkx")

    def test_extract_internationalized_url(self) -> None:
        url = "https://open.spotify.com/intl-it/show/5IHj4utnRlTNcCCoxyinkx?si=db5fcba3c59e4526"
        self.assertEqual(extract_spotify_id(url), "5IHj4utnRlTNcCCoxyinkx")
        self.assertEqual(
            extract_spotify_id(url, expected_type="show"),
            "5IHj4utnRlTNcCCoxyinkx",
        )

    def test_extract_spotify_uri(self) -> None:
        uri = "spotify:show:5IHj4utnRlTNcCCoxyinkx"
        self.assertEqual(extract_spotify_id(uri), "5IHj4utnRlTNcCCoxyinkx")
        self.assertEqual(
            extract_spotify_id(uri, expected_type="show"),
            "5IHj4utnRlTNcCCoxyinkx",
        )

    def test_extract_episode_url_and_uri(self) -> None:
        url = "https://open.spotify.com/episode/31Z8bM8uR5Bq3jK5m4N6op?si=abc123xyz"
        self.assertEqual(extract_spotify_id(url), "31Z8bM8uR5Bq3jK5m4N6op")
        self.assertEqual(
            extract_spotify_id(url, expected_type="episode"),
            "31Z8bM8uR5Bq3jK5m4N6op",
        )

        uri = "spotify:episode:31Z8bM8uR5Bq3jK5m4N6op"
        self.assertEqual(
            extract_spotify_id(uri, expected_type="episode"),
            "31Z8bM8uR5Bq3jK5m4N6op",
        )

    def test_extract_invalid_id_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            extract_spotify_id("")

        with self.assertRaises(ValueError):
            extract_spotify_id("   ")

        with self.assertRaises(ValueError):
            extract_spotify_id("https://open.spotify.com/")

    def test_format_ms(self) -> None:
        self.assertEqual(format_ms(65000), "01:05")
        self.assertEqual(format_ms(3665000), "01:01:05")


if __name__ == "__main__":
    unittest.main()
