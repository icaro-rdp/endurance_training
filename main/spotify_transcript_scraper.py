#!/usr/bin/env python3
"""Spotify Podcast Transcript Scraper & Markdown Generator.

Fetches podcast episode metadata via Spotify Web API and extracts
time-synced episode transcripts, generating clean Markdown files formatted
with YAML frontmatter conforming to the knowledge base taxonomy.
Supports on-the-fly local MLX / DeepL translation into English under WIP.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from datetime import timedelta
from pathlib import Path
from typing import Any

import requests


def extract_spotify_id(value: str, expected_type: str | None = None) -> str:
    """Extracts a Spotify ID from a raw ID, Spotify URI, or Spotify URL.

    Handles full URLs with query parameters (e.g. ?si=...), internationalized
    Spotify URLs (e.g. /intl-it/show/...), URI schemes (spotify:show:...),
    and plain alphanumeric IDs.

    Args:
        value: Input string containing a raw Spotify ID, URI, or URL.
        expected_type: Optional expected entity type (e.g. 'show', 'episode').

    Returns:
        The extracted alphanumeric Spotify ID.

    Raises:
        ValueError: If a valid Spotify ID cannot be parsed from the input.
    """
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("Empty Spotify identifier provided.")

    # 1. Typed Spotify URI: spotify:<expected_type>:<id>
    if expected_type:
        typed_uri_match = re.search(rf"spotify:{expected_type}:([a-zA-Z0-9]+)", cleaned)
        if typed_uri_match:
            return typed_uri_match.group(1)

    # 2. General Spotify URI: spotify:(show|episode|track):<id>
    uri_match = re.search(r"spotify:(?:[a-zA-Z]+:)?([a-zA-Z0-9]+)", cleaned)
    if uri_match:
        return uri_match.group(1)

    # 3. Typed Spotify URL: open.spotify.com/(intl-[a-z-]+/)?<expected_type>/<id>
    if expected_type:
        typed_url_match = re.search(
            rf"open\.spotify\.com/(?:intl-[a-zA-Z-]+/)?{expected_type}/([a-zA-Z0-9]+)(?:[/?#]|$)",
            cleaned,
        )
        if typed_url_match:
            return typed_url_match.group(1)

    # 4. General Spotify URL: open.spotify.com/(intl-[a-z-]+/)?(show|episode|track)/<id>
    url_match = re.search(
        r"open\.spotify\.com/(?:intl-[a-zA-Z-]+/)?(?:[a-zA-Z_-]+/)?([a-zA-Z0-9]+)(?:[/?#]|$)",
        cleaned,
    )
    if url_match:
        return url_match.group(1)

    # 5. Plain alphanumeric ID
    if re.fullmatch(r"[a-zA-Z0-9]+", cleaned):
        return cleaned

    raise ValueError(f"Unable to parse Spotify ID from: '{value}'")


def load_credentials() -> dict[str, str]:
    """Loads and sanitizes environment variables from .env file or environment.

    Returns:
        Dictionary containing mapped credential key-value pairs.
    """
    env_path = Path(__file__).resolve().parent.parent / ".env"
    env_vars: dict[str, str] = {}

    if env_path.exists():
        try:
            from dotenv import dotenv_values

            raw_env = dotenv_values(env_path)
            for k, v in raw_env.items():
                if k and v:
                    clean_k = k.strip("\"' ")
                    clean_v = v.strip("\"' ")
                    env_vars[clean_k] = clean_v
        except ImportError:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                clean_k = k.strip("\"' ")
                clean_v = v.strip("\"' ")
                if clean_k and clean_v:
                    env_vars[clean_k] = clean_v

    # Fall back to os.environ if not in .env file
    for key in [
        "SPOTIFY_CLIENT_ID",
        "SPOTIFY_CLIENT_SECRET",
        "SPOTIFY_SP_DC",
        "DEEPL_API_KEY",
    ]:
        if key not in env_vars and key in os.environ:
            env_vars[key] = os.environ[key]

    return env_vars


class SpotifyAPIClient:
    """Handles interaction with official Spotify Web API."""

    def __init__(self, client_id: str, client_secret: str) -> None:
        """Initializes API client and fetches access token.

        Args:
            client_id: Spotify Developer Application Client ID.
            client_secret: Spotify Developer Application Client Secret.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self._get_access_token()

    def _get_access_token(self) -> str:
        """Fetches Client Credentials access token."""
        url = "https://accounts.spotify.com/api/token"
        response = requests.post(
            url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        if response.status_code != 200:
            raise RuntimeError(
                "Spotify Web API authentication failed "
                f"({response.status_code}): {response.text}"
            )
        return response.json()["access_token"]

    def get_show_info(self, show_id: str) -> dict[str, Any]:
        """Gets show metadata.

        Args:
            show_id: Spotify Show ID.

        Returns:
            Dictionary containing show details.
        """
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"https://api.spotify.com/v1/shows/{show_id}?market=US"
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_episode_info(self, episode_id: str) -> dict[str, Any]:
        """Gets episode metadata.

        Args:
            episode_id: Spotify Episode ID.

        Returns:
            Dictionary containing episode details.
        """
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"https://api.spotify.com/v1/episodes/{episode_id}?market=US"
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_all_episodes(
        self, show_id: str, limit: int | None = None
    ) -> list[dict[str, Any]]:
        """Paginates through all episodes of a show.

        Args:
            show_id: Spotify Show ID.
            limit: Maximum number of episodes to fetch.

        Returns:
            List of episode dictionaries.
        """
        headers = {"Authorization": f"Bearer {self.access_token}"}
        episodes: list[dict[str, Any]] = []
        offset = 0
        batch_size = 50

        print(f"Fetching episode catalogue for show '{show_id}' via Web API...")
        while True:
            url = (
                f"https://api.spotify.com/v1/shows/{show_id}/episodes"
                f"?limit={batch_size}&offset={offset}&market=US"
            )
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("items", [])
            if not items:
                break

            episodes.extend(items)
            print(f"  Retrieved {len(episodes)} / {data.get('total', '?')} episodes...")

            if limit and len(episodes) >= limit:
                episodes = episodes[:limit]
                break

            if not data.get("next"):
                break
            offset += batch_size

        return episodes


def format_ms(ms: int) -> str:
    """Formats milliseconds into [MM:SS] or [HH:MM:SS].

    Args:
        ms: Duration in milliseconds.

    Returns:
        Formatted string representation of the duration.
    """
    td = timedelta(milliseconds=ms)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def format_transcript_paragraphs(
    lines: list[dict[str, Any]], paragraph_interval_ms: int = 45000
) -> str:
    """Groups time-synced transcript lines into structured, readable paragraphs.

    Args:
        lines: List of transcript lines containing start_ms and text.
        paragraph_interval_ms: Millisecond interval between paragraph markers.

    Returns:
        Formatted transcript text with timestamps.
    """
    if not lines:
        return "*Spoken transcript not available via Spotify for this episode.*"

    paragraphs: list[str] = []
    current_para: list[str] = []
    current_start_ms = 0

    for line in lines:
        start_ms = line.get("start_ms", 0)
        text = line.get("text", "").strip()
        if not text:
            continue

        if not current_para:
            current_start_ms = start_ms
            current_para.append(text)
        elif start_ms - current_start_ms >= paragraph_interval_ms:
            time_str = format_ms(current_start_ms)
            paragraphs.append(f"**[{time_str}]** " + " ".join(current_para))
            current_para = [text]
            current_start_ms = start_ms
        else:
            current_para.append(text)

    if current_para:
        time_str = format_ms(current_start_ms)
        paragraphs.append(f"**[{time_str}]** " + " ".join(current_para))

    return "\n\n".join(paragraphs)


def scan_existing_downloads(output_dir: Path) -> set[str]:
    """Scans target directory to index existing Spotify episode IDs and URLs.

    Args:
        output_dir: Directory to scan for existing markdown files.

    Returns:
        Set of existing episode IDs and stems to prevent redundant downloads.
    """
    existing_identifiers: set[str] = set()
    if not output_dir.exists():
        return existing_identifiers

    for file_path in output_dir.glob("*.md"):
        if file_path.stat().st_size < 50:
            continue
        existing_identifiers.add(file_path.stem.lower())

        try:
            with open(file_path, encoding="utf-8") as f:
                head = f.read(1500)
                match = re.search(r"open\.spotify\.com/episode/([a-zA-Z0-9]+)", head)
                if match:
                    existing_identifiers.add(match.group(1))
        except OSError:
            pass

    return existing_identifiers


def generate_markdown(
    episode_info: dict[str, Any],
    transcript_lines: list[dict[str, Any]] | None,
    show_name: str = "Podcast",
    author: str = "",
) -> str:
    """Generates a complete, structured Markdown document.

    Args:
        episode_info: Episode metadata dictionary from Spotify.
        transcript_lines: Optional list of timestamped transcript segments.
        show_name: Name of the podcast show.
        author: Author or publisher name.

    Returns:
        Formatted markdown string with YAML frontmatter conforming to taxonomy.
    """
    title = episode_info.get("name", "Untitled Episode").strip()
    release_date = episode_info.get("release_date", "")
    duration_ms = episode_info.get("duration_ms", 0)
    duration_str = format_ms(duration_ms)
    spotify_url = episode_info.get("external_urls", {}).get("spotify", "")
    desc = episode_info.get("description", "").strip()

    clean_desc = re.sub(r"\s+", " ", desc).replace('"', "'")
    summary = clean_desc

    author_val = author.strip()
    if not author_val:
        if "empirical cycling" in show_name.lower():
            author_val = "Kolie Moore"
        else:
            author_val = episode_info.get("show", {}).get("publisher", "") or "Unknown"

    transcript_content = (
        format_transcript_paragraphs(transcript_lines)
        if transcript_lines
        else "*Spoken transcript not available via Spotify for this episode.*"
    )

    md = f"""---
title: "{title.replace('"', "'")}"
category: []
topics: []
source: "{show_name}"
author: "{author_val}"
date: "{release_date}"
spotify_url: "{spotify_url}"
duration: "{duration_str}"
summary: "{summary}"
---

# {title}

- **Show:** {show_name}
- **Date:** {release_date}
- **Duration:** {duration_str}
- **Listen on Spotify:** [{title}]({spotify_url})

---

## Show Notes

{desc}

---

## Transcript

{transcript_content}
"""
    return md


def main() -> None:
    """Main CLI entrypoint for the Spotify transcript scraper."""
    parser = argparse.ArgumentParser(
        description="Spotify Podcast Transcript Scraper (Markdown Generator)"
    )
    parser.add_argument(
        "--show-id",
        "-s",
        default=None,
        help="Spotify Show ID or URL (e.g. https://open.spotify.com/show/5IHj4utnRlTNcCCoxyinkx)",
    )
    parser.add_argument(
        "--episode-id",
        "-e",
        default=None,
        help="Specific Spotify Episode ID or URL (optional)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Max number of episodes to process (default: 0 = all episodes)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default=None,
        help=(
            "Output directory for saved markdown files "
            "(default: Knowledge_base/WIP/<show_name>/raw_transcripts)"
        ),
    )
    parser.add_argument(
        "--translate-local",
        action="store_true",
        help=(
            "Translate downloaded markdown to English using local "
            "Apple Silicon MLX model"
        ),
    )
    parser.add_argument(
        "--local-model",
        default="mlx-community/Qwen2.5-7B-Instruct-4bit",
        help=(
            "Model ID for local MLX translation "
            "(default: mlx-community/Qwen2.5-7B-Instruct-4bit)"
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if markdown file exists",
    )
    parser.add_argument(
        "--sp-dc",
        default=None,
        help="Spotify 'sp_dc' cookie (optional; reads from .env by default)",
    )

    args = parser.parse_args()

    if not args.show_id and not args.episode_id:
        parser.error(
            "Please provide a Spotify Show ID/URL via --show-id / -s "
            "or a specific Episode ID/URL via --episode-id / -e."
        )

    # Load credentials
    credentials = load_credentials()
    client_id = credentials.get("SPOTIFY_CLIENT_ID")
    client_secret = credentials.get("SPOTIFY_CLIENT_SECRET")
    sp_dc = args.sp_dc or credentials.get("SPOTIFY_SP_DC")

    if not client_id or not client_secret:
        print(
            "Error: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be present "
            "in .env or environment."
        )
        sys.exit(1)

    print("=== Spotify Podcast Transcript Markdown Scraper ===")
    print(f"Spotify Web API Client ID: {client_id[:6]}...{client_id[-4:]}")
    print(f"Spotify SP_DC Session Cookie: {'Present' if sp_dc else 'NOT PRESENT'}")

    # Initialize Web API
    api = SpotifyAPIClient(client_id, client_secret)

    show_id: str | None = None
    show_name = "Podcast"
    show_publisher = ""

    if args.show_id:
        try:
            show_id = extract_spotify_id(args.show_id, expected_type="show")
        except ValueError as exc:
            print(f"Error parsing show identifier: {exc}")
            sys.exit(1)

        show_info = api.get_show_info(show_id)
        show_name = show_info.get("name", "Podcast")
        show_publisher = show_info.get("publisher", "")
        total_episodes = show_info.get("total_episodes", "Unknown")
        print(f"Target Show: {show_name} (Total episodes: {total_episodes})")

    # Fetch episodes
    episodes: list[dict[str, Any]] = []
    if args.episode_id:
        try:
            episode_id = extract_spotify_id(args.episode_id, expected_type="episode")
        except ValueError as exc:
            print(f"Error parsing episode identifier: {exc}")
            sys.exit(1)

        ep = api.get_episode_info(episode_id)
        episodes = [ep]
        if not args.show_id:
            show_obj = ep.get("show", {})
            show_name = show_obj.get("name", show_name)
            show_publisher = show_obj.get("publisher", show_publisher)
    elif show_id:
        limit_val = args.limit if args.limit > 0 else None
        episodes = api.get_all_episodes(show_id, limit=limit_val)

    # Determine default output directory under Knowledge_base/WIP/
    if args.output_dir:
        output_path = Path(args.output_dir)
    else:
        show_slug = re.sub(r"[^\w\-]+", "_", show_name).strip("_")
        base_wip_dir = Path("Knowledge_base/WIP")
        matched_dir = None
        if base_wip_dir.exists():
            for child in base_wip_dir.iterdir():
                if child.is_dir() and child.name.lower() == show_slug.lower():
                    matched_dir = child / "raw_transcripts"
                    break
        output_path = (
            matched_dir
            if matched_dir
            else (base_wip_dir / show_slug / "raw_transcripts")
        )

    output_path.mkdir(parents=True, exist_ok=True)

    # Scan existing downloads for duplicate prevention
    existing_downloads = scan_existing_downloads(output_path)
    print(
        "Existing files detected in output folder: "
        f"{len(existing_downloads)} files/IDs indexed."
    )

    # Initialize scraper client
    scraper_client = None
    if sp_dc:
        try:
            from spotify_scraper import SpotifyClient

            scraper_client = SpotifyClient(cookies={"sp_dc": sp_dc})
            print(
                "Successfully initialized Spotify Scraper client with session cookie."
            )
        except ImportError:
            print(
                "Info: 'spotify_scraper' package not installed; "
                "generating metadata and show notes only."
            )
        except (requests.RequestException, OSError, ValueError, RuntimeError) as e:
            print(f"Warning: Failed to initialize SpotifyClient scraper ({e}).")

    # Initialize local translator if requested
    local_translator = None
    if args.translate_local:
        from main.utils.translator import LocalMLXTranslator

        local_translator = LocalMLXTranslator(model_id=args.local_model)

    print(f"\nProcessing {len(episodes)} episode(s)...")

    success_count = 0
    skipped_count = 0
    no_transcript_count = 0

    for i, ep in enumerate(episodes, 1):
        ep_id = ep.get("id")
        ep_name = ep.get("name", "Untitled")
        clean_filename = "".join(
            c if c.isalnum() or c in " ._-" else "_" for c in ep_name
        ).strip()
        clean_filename = clean_filename.replace(" ", "_")[:80]
        base_name = f"{ep.get('release_date', 'unknown')}_{clean_filename}"
        target_file = output_path / f"{base_name}.md"

        # Check for existing download
        if not args.force and (
            ep_id in existing_downloads
            or (target_file.exists() and target_file.stat().st_size > 100)
        ):
            print(f"[{i}/{len(episodes)}] (Skipping already downloaded) {ep_name}")
            skipped_count += 1
            continue

        print(f"\n[{i}/{len(episodes)}] {ep_name} (ID: {ep_id})")

        transcript_lines = None
        if scraper_client:
            try:
                transcript_obj = scraper_client.get_transcript(ep_id)
                if transcript_obj and hasattr(transcript_obj, "lines"):
                    transcript_lines = [
                        {"start_ms": line.start_ms, "text": line.text}
                        for line in transcript_obj.lines
                    ]
                    print(f"  -> Extracted {len(transcript_lines)} transcript lines!")
                    success_count += 1
            except (
                requests.RequestException,
                OSError,
                ValueError,
                RuntimeError,
                AttributeError,
                KeyError,
            ) as e:
                print(f"  -> No transcript found on Spotify ({e})")
                no_transcript_count += 1
        else:
            no_transcript_count += 1

        # Generate Markdown
        md_content = generate_markdown(
            episode_info=ep,
            transcript_lines=transcript_lines,
            show_name=show_name,
            author=show_publisher,
        )

        # Translate locally if requested
        if local_translator:
            print("  -> Translating into English via local Apple Silicon MLX GPU...")
            md_content = local_translator.translate_markdown(
                md_content, target_lang="en"
            )

        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(md_content, encoding="utf-8")
        print(f"  Saved: {target_file.name}")

        time.sleep(0.3)

    if scraper_client:
        scraper_client.close()

    print("\n==========================================")
    print("Finished processing episodes!")
    print(f"  Total in catalogue: {len(episodes)}")
    print(f"  Skipped (already downloaded): {skipped_count}")
    print(f"  Newly extracted with transcripts: {success_count}")
    if no_transcript_count:
        print(
            f"  Episodes with notes only (no Spotify transcript): {no_transcript_count}"
        )
    print(f"  Output directory: {output_path.resolve()}")
    print("==========================================")


if __name__ == "__main__":
    main()
