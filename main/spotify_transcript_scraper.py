#!/usr/bin/env python3
"""
Spotify Podcast Transcript Scraper & Markdown Generator

Fetches podcast episode metadata via Spotify Web API and extracts
time-synced episode transcripts, generating clean Markdown files formatted
with YAML frontmatter conforming to the knowledge base taxonomy.
Includes robust duplicate detection to prevent redundant downloads.
"""

import argparse
import os
import re
import sys
import time
from datetime import timedelta
from pathlib import Path
from typing import Any

import requests
from dotenv import dotenv_values

DEFAULT_SHOW_ID = "5IHj4utnRlTNcCCoxyinkx"  # Empirical Cycling Podcast


def load_credentials() -> dict[str, str]:
    """Loads and sanitizes environment variables from .env file or environment."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    env_vars = {}
    if env_path.exists():
        raw_env = dotenv_values(env_path)
        for k, v in raw_env.items():
            if k and v:
                clean_k = k.strip("\"' ")
                clean_v = v.strip("\"' ")
                env_vars[clean_k] = clean_v

    # Fall back to os.environ if not in .env file
    for key in ["SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", "SPOTIFY_SP_DC"]:
        if key not in env_vars and key in os.environ:
            env_vars[key] = os.environ[key]

    return env_vars


class SpotifyAPIClient:
    """Handles interaction with official Spotify Web API."""

    def __init__(self, client_id: str, client_secret: str):
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
        """Gets show metadata."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"https://api.spotify.com/v1/shows/{show_id}?market=US"
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_all_episodes(self, show_id: str, limit: int | None) -> list[dict[str, Any]]:
        """Paginates through all episodes of a show."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        episodes = []
        offset = 0
        batch_size = 50

        print(f"Fetching episode catalogue for show '{show_id}' via Web API...")
        while True:
            url = f"https://api.spotify.com/v1/shows/{show_id}/episodes?limit={batch_size}&offset={offset}&market=US"
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
    """Formats milliseconds into [MM:SS] or [HH:MM:SS]."""
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
    """
    Groups time-synced transcript lines into structured, readable paragraphs
    with timestamps every ~45 seconds.
    """
    if not lines:
        return "*Spoken transcript not available via Spotify for this episode.*"

    paragraphs = []
    current_para = []
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
    """
    Scans the target directory and extracts existing Spotify episode IDs and URLs
    to prevent redundant downloads.
    """
    existing_identifiers: set[str] = set()
    if not output_dir.exists():
        return existing_identifiers

    for file_path in output_dir.glob("*.md"):
        if file_path.stat().st_size < 50:
            continue
        # Add filename base
        existing_identifiers.add(file_path.stem.lower())

        # Read header to find spotify_url or episode ID
        try:
            with open(file_path, encoding="utf-8") as f:
                head = f.read(1500)
                # Match spotify URL e.g. https://open.spotify.com/episode/<id>
                match = re.search(r"open\.spotify\.com/episode/([a-zA-Z0-9]+)", head)
                if match:
                    existing_identifiers.add(match.group(1))
        except OSError:
            pass

    return existing_identifiers


def generate_markdown(
    episode_info: dict[str, Any],
    transcript_lines: list[dict[str, Any]] | None,
    show_name: str = "Empirical Cycling Podcast",
) -> str:
    """Generates a complete, structured Markdown document."""
    title = episode_info.get("name", "Untitled Episode").strip()
    release_date = episode_info.get("release_date", "")
    duration_ms = episode_info.get("duration_ms", 0)
    duration_str = format_ms(duration_ms)
    spotify_url = episode_info.get("external_urls", {}).get("spotify", "")
    desc = episode_info.get("description", "").strip()

    clean_desc = re.sub(r"\s+", " ", desc).replace('"', "'")
    summary = clean_desc[:200] + ("..." if len(clean_desc) > 200 else "")

    transcript_content = (
        format_transcript_paragraphs(transcript_lines)
        if transcript_lines
        else "*Spoken transcript not available via Spotify for this episode.*"
    )

    md = f"""---
title: "{title.replace('"', "'")}"
category: NaN
topics: NaN
source: "{show_name}"
author: "Kolie Moore"
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


def main():
    parser = argparse.ArgumentParser(
        description="Spotify Podcast Transcript Scraper (Markdown Only)"
    )
    parser.add_argument(
        "--show-id",
        default=DEFAULT_SHOW_ID,
        help=f"Spotify Show ID (default: Empirical Cycling: {DEFAULT_SHOW_ID})",
    )
    parser.add_argument(
        "--episode-id",
        default=None,
        help="Specific Spotify Episode ID (optional)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Max number of episodes to process (default: 0 = all episodes)",
    )
    parser.add_argument(
        "--output-dir",
        default="Knowledge_base/Episodes/Empirical_cycling_podcast/raw_transcripts",
        help="Output directory for saved markdown files",
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
    show_info = api.get_show_info(args.show_id)
    show_name = show_info.get("name", "Podcast")
    total_episodes = show_info.get("total_episodes", "Unknown")
    print(f"Target Show: {show_name} (Total episodes: {total_episodes})")

    output_path = Path(args.output_dir)
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
        except (requests.RequestException, OSError, ValueError, RuntimeError) as e:
            print(f"Warning: Failed to initialize SpotifyClient scraper ({e}).")

    # Fetch episodes
    episodes = []
    if args.episode_id:
        headers = {"Authorization": f"Bearer {api.access_token}"}
        r = requests.get(
            f"https://api.spotify.com/v1/episodes/{args.episode_id}?market=US",
            headers=headers,
        )
        r.raise_for_status()
        episodes = [r.json()]
    else:
        limit_val = args.limit if args.limit > 0 else None
        episodes = api.get_all_episodes(args.show_id, limit=limit_val)

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

        # Generate and save Markdown
        md_content = generate_markdown(ep, transcript_lines, show_name)
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
