#!/usr/bin/env python3
"""Spotify Podcast Transcript Scraper & Markdown Generator.

Fetches podcast episode metadata via Spotify Web API and extracts
time-synced episode transcripts, generating clean Markdown files formatted
with YAML frontmatter conforming to the knowledge base taxonomy.
Supports on-the-fly Azure, DeepL, or local MLX translation into English.
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
from spotify_scraper import NotFoundError
from tqdm import tqdm


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
    cleaned = re.sub(r"\s+", "", value).replace("\\", "")
    if not cleaned:
        raise ValueError("Empty Spotify identifier provided.")

    entity_match = re.search(
        r"(?:open\.spotify\.com/(?:intl-[a-zA-Z-]+/)?|spotify:)"
        r"(?P<entity_type>show|episode|track)[/:]"
        r"(?P<spotify_id>[a-zA-Z0-9]{22})(?:[/?#]|$)",
        cleaned,
    )
    if entity_match:
        entity_type = entity_match.group("entity_type")
        if expected_type and entity_type != expected_type:
            raise ValueError(
                f"Expected a Spotify {expected_type}, received {entity_type}."
            )
        return entity_match.group("spotify_id")

    if re.fullmatch(r"[a-zA-Z0-9]{22}", cleaned):
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
        "AZURE_TRANSLATOR_KEY",
        "AZURE_TRANSLATOR_REGION",
        "DEEPL_API_KEY",
        "LOCAL_MLX_MODEL",
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


def extract_title_from_markdown(
    markdown_content: str, default: str = "Untitled"
) -> str:
    """Extracts title from YAML frontmatter or top header.

    Args:
        markdown_content: Document content.
        default: Fallback title if none found.

    Returns:
        Extracted title string.
    """
    match = re.search(r'^title:\s*["\']?(.*?)["\']?$', markdown_content, re.MULTILINE)
    if match and match.group(1).strip():
        return match.group(1).strip()
    match_h1 = re.search(r"^#\s+(.+)$", markdown_content, re.MULTILINE)
    if match_h1 and match_h1.group(1).strip():
        return match_h1.group(1).strip()
    return default


def sanitize_filename(name: str, max_length: int = 80) -> str:
    """Sanitizes a title for safe filesystem filename generation.

    Args:
        name: Raw episode or document title.
        max_length: Maximum character length for base filename.

    Returns:
        Sanitized filename string without extension.
    """
    clean = "".join(c if c.isalnum() or c in " ._-" else "_" for c in name).strip()
    clean = clean.replace(" ", "_")[:max_length]
    return clean or "Untitled"


def build_episode_filename(episode_info: dict[str, Any], title: str) -> str:
    """Build a sortable filename with a stable Spotify identity.

    Args:
        episode_info: Spotify episode metadata.
        title: Translated or original episode title.

    Returns:
        Markdown filename containing release date, title, and episode ID.
    """
    release_date = str(episode_info.get("release_date") or "unknown")
    episode_id = str(episode_info.get("id") or "unknown")
    return f"{release_date}_{sanitize_filename(title)}_{episode_id}.md"


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
    translation_group = parser.add_mutually_exclusive_group()
    translation_group.add_argument(
        "--translate",
        action="store_true",
        help=(
            "Translate downloaded markdown to English using Azure, then DeepL, "
            "then local Apple Silicon MLX as available"
        ),
    )
    translation_group.add_argument(
        "--translate-local",
        action="store_true",
        help=(
            "Translate downloaded markdown to English using local "
            "Apple Silicon MLX model directly"
        ),
    )
    translation_group.add_argument(
        "--translate-deepl",
        action="store_true",
        help=(
            "Translate downloaded markdown to English using DeepL API "
            "(with automatic local MLX fallback)"
        ),
    )
    parser.add_argument(
        "--azure-key",
        default=None,
        help=(
            "Microsoft Azure Translator Key "
            "(optional; reads AZURE_TRANSLATOR_KEY from .env)"
        ),
    )
    parser.add_argument(
        "--azure-region",
        default=None,
        help=(
            "Microsoft Azure Service Region "
            "(optional; reads AZURE_TRANSLATOR_REGION from .env)"
        ),
    )
    parser.add_argument(
        "--deepl-key",
        default=None,
        help="DeepL Authentication Key (optional; reads DEEPL_API_KEY from .env)",
    )
    parser.add_argument(
        "--local-model",
        default=None,
        help=(
            "Model ID for local MLX translation fallback "
            "(reads LOCAL_MLX_MODEL from .env when omitted)"
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

    # Initialize translator if requested
    translator = None
    if args.translate or args.translate_local or args.translate_deepl:
        from main.utils.translator import DEFAULT_LOCAL_MODEL_ID, HybridTranslator

        prefer_api = not args.translate_local
        azure_key = args.azure_key or credentials.get("AZURE_TRANSLATOR_KEY")
        azure_region = args.azure_region or credentials.get("AZURE_TRANSLATOR_REGION")
        deepl_key = args.deepl_key or credentials.get("DEEPL_API_KEY")
        local_model_id = (
            args.local_model
            or credentials.get("LOCAL_MLX_MODEL")
            or DEFAULT_LOCAL_MODEL_ID
        )
        translator = HybridTranslator(
            azure_key=azure_key,
            azure_region=azure_region,
            deepl_key=deepl_key,
            local_model_id=local_model_id,
            prefer_api=prefer_api,
            enable_azure=not args.translate_deepl,
        )

    success_count = 0
    skipped_count = 0
    no_transcript_count = 0

    progress_description = "Scraping & Translating" if translator else "Scraping"
    progress_bar = tqdm(episodes, desc=progress_description, unit="ep")
    for i, ep in enumerate(progress_bar, 1):
        ep_id = str(ep.get("id") or "").strip()
        ep_name = str(ep.get("name") or "Untitled")

        if not ep_id:
            tqdm.write(f"[{i}/{len(episodes)}] Skipped episode without a Spotify ID")
            skipped_count += 1
            continue

        # Check for existing download
        if not args.force and ep_id in existing_downloads:
            tqdm.write(f"[{i}/{len(episodes)}] (Skipped existing) {ep_name}")
            skipped_count += 1
            continue

        progress_bar.set_postfix_str(f"{ep_name[:35]}...")

        transcript_lines = None
        if scraper_client:
            try:
                transcript_obj = scraper_client.get_transcript(ep_id)
                if transcript_obj and hasattr(transcript_obj, "lines"):
                    transcript_lines = [
                        {"start_ms": line.start_ms, "text": line.text}
                        for line in transcript_obj.lines
                    ]
                    success_count += 1
            except (
                NotFoundError,
                requests.RequestException,
                OSError,
                ValueError,
                RuntimeError,
                AttributeError,
                KeyError,
            ):
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

        # Translate with automatic API -> local MLX fallback
        if translator:
            md_content = translator.translate_markdown(md_content, target_lang="en")

        final_title = extract_title_from_markdown(md_content, default=ep_name)
        target_file = output_path / build_episode_filename(ep, final_title)

        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(md_content, encoding="utf-8")
        tqdm.write(f"[{i}/{len(episodes)}] Saved: {target_file.name}")

        time.sleep(0.1)

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
