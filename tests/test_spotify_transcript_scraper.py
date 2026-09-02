"""Unit tests for Spotify transcript scraper utilities and ID extraction."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from spotify_scraper import NotFoundError

from main.spotify_transcript_scraper import (
    build_episode_filename,
    extract_spotify_id,
    format_ms,
    main,
)


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

    def test_extract_escaped_and_wrapped_url(self) -> None:
        escaped_url = r"https://open.spotify.com/show/6kMvM8vuxlPzR8OOWSx2B1\?si\=f774d86cab824ca0"
        self.assertEqual(extract_spotify_id(escaped_url), "6kMvM8vuxlPzR8OOWSx2B1")

        wrapped_url = (
            "https://open.spotify.\n  "
            "com/show/6kMvM8vuxlPzR8OOWSx2B1?si=b963a19aa4a7437f"
        )
        self.assertEqual(extract_spotify_id(wrapped_url), "6kMvM8vuxlPzR8OOWSx2B1")

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

        with self.assertRaises(ValueError):
            extract_spotify_id(
                "https://open.spotify.com/not-a-type/5IHj4utnRlTNcCCoxyinkx"
            )

        with self.assertRaises(ValueError):
            extract_spotify_id(
                "https://open.spotify.com/episode/31Z8bM8uR5Bq3jK5m4N6op",
                expected_type="show",
            )

    def test_build_episode_filename_includes_stable_identity(self) -> None:
        episode = {
            "id": "31Z8bM8uR5Bq3jK5m4N6op",
            "release_date": "2026-09-02",
        }
        filename = build_episode_filename(episode, "Threshold: Part 1")
        self.assertEqual(
            filename,
            "2026-09-02_Threshold__Part_1_31Z8bM8uR5Bq3jK5m4N6op.md",
        )

    @patch("main.spotify_transcript_scraper.time.sleep")
    @patch("spotify_scraper.SpotifyClient")
    @patch("main.spotify_transcript_scraper.SpotifyAPIClient")
    @patch("main.spotify_transcript_scraper.load_credentials")
    def test_batch_continues_when_an_episode_has_no_transcript(
        self,
        mock_load_credentials: MagicMock,
        mock_api_class: MagicMock,
        mock_scraper_class: MagicMock,
        _mock_sleep: MagicMock,
    ) -> None:
        mock_load_credentials.return_value = {
            "SPOTIFY_CLIENT_ID": "client",
            "SPOTIFY_CLIENT_SECRET": "secret",
            "SPOTIFY_SP_DC": "cookie",
        }
        episodes = [
            {
                "id": "4NDOv25zu5sver8yqQ6BOl",
                "name": "Missing transcript",
                "release_date": "2026-01-01",
                "duration_ms": 60_000,
                "description": "Notes only",
                "external_urls": {"spotify": "https://example.com/missing"},
            },
            {
                "id": "31Z8bM8uR5Bq3jK5m4N6op",
                "name": "Available transcript",
                "release_date": "2026-01-02",
                "duration_ms": 60_000,
                "description": "Notes and transcript",
                "external_urls": {"spotify": "https://example.com/available"},
            },
        ]
        api = mock_api_class.return_value
        api.get_show_info.return_value = {
            "name": "Test Podcast",
            "publisher": "Test Publisher",
            "total_episodes": 2,
        }
        api.get_all_episodes.return_value = episodes

        scraper = mock_scraper_class.return_value
        scraper.get_transcript.side_effect = [
            NotFoundError("No transcript"),
            SimpleNamespace(lines=[SimpleNamespace(start_ms=0, text="Transcript")]),
        ]

        with TemporaryDirectory() as output_dir:
            with patch(
                "sys.argv",
                [
                    "spotify-transcript-scraper",
                    "--show-id",
                    "6kMvM8vuxlPzR8OOWSx2B1",
                    "--output-dir",
                    output_dir,
                ],
            ):
                main()

            generated_files = list(Path(output_dir).glob("*.md"))
            self.assertEqual(len(generated_files), 2)
            missing_transcript_file = next(
                path for path in generated_files if "Missing_transcript" in path.name
            )
            self.assertIn(
                "Spoken transcript not available",
                missing_transcript_file.read_text(encoding="utf-8"),
            )

    def test_format_ms(self) -> None:
        self.assertEqual(format_ms(65000), "01:05")
        self.assertEqual(format_ms(3665000), "01:01:05")


if __name__ == "__main__":
    unittest.main()
