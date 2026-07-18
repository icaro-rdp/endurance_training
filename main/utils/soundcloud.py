from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests


class SoundCloudError(RuntimeError):
    """Raised for SoundCloud API or download failures."""


class DownloadNotAllowed(SoundCloudError):
    """Raised when the track does not expose an authorized download URL."""


class SoundCloud:
    API_BASE = "https://api.soundcloud.com"
    AUTH_BASE = "https://secure.soundcloud.com"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        access_token: str | None = None,
        timeout: int = 30,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json; charset=utf-8",
            "User-Agent": "SoundCloudAuthorizedDownloader/1.0",
        })

    def authenticate_app(self) -> dict[str, Any]:
        """
        Get an application token for public API operations using the
        OAuth Client Credentials flow.
        """
        response = self.session.post(
            f"{self.AUTH_BASE}/oauth/token",
            auth=(self.client_id, self.client_secret),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "client_credentials"},
            timeout=self.timeout,
        )
        self._raise_for_error(response)

        token_data = response.json()
        self.access_token = token_data["access_token"]
        return token_data

    def _auth_headers(self) -> dict[str, str]:
        if not self.access_token:
            raise SoundCloudError(
                "No access token. Call authenticate_app() or provide one."
            )
        return {"Authorization": f"OAuth {self.access_token}"}

    def _raise_for_error(self, response: requests.Response) -> None:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            try:
                detail = response.json()
            except ValueError:
                detail = response.text[:500]

            raise SoundCloudError(
                f"SoundCloud request failed ({response.status_code}): {detail}"
            ) from exc

    def resolve(self, permalink_url: str) -> dict[str, Any]:
        """Resolve a SoundCloud track permalink to its official API object."""
        response = self.session.get(
            f"{self.API_BASE}/resolve",
            params={"url": permalink_url},
            headers=self._auth_headers(),
            timeout=self.timeout,
        )
        self._raise_for_error(response)

        resource = response.json()
        if resource.get("kind") != "track":
            raise SoundCloudError("The supplied URL does not resolve to one track.")

        return resource

    def get_track(self, track_id: int | str) -> dict[str, Any]:
        """Fetch current metadata for a track."""
        response = self.session.get(
            f"{self.API_BASE}/tracks/{track_id}",
            headers=self._auth_headers(),
            timeout=self.timeout,
        )
        self._raise_for_error(response)
        return response.json()

    def authorized_download_url(self, track: dict[str, Any]) -> str:
        """
        Return an official download URL only when SoundCloud includes one.

        This intentionally does not turn stream/transcoding URLs into files
        and does not bypass disabled downloads, previews, geo-blocks, or
        other access restrictions.
        """
        if track.get("downloadable") is not True:
            raise DownloadNotAllowed(
                "The creator has not enabled downloading for this track."
            )

        download_url = track.get("download_url")
        if not download_url:
            raise DownloadNotAllowed(
                "This API response does not expose an authorized download URL."
            )

        return download_url

    def download(self, permalink_url: str, destination: str | Path) -> Path:
        """
        Resolve a permalink and save only an explicitly authorized download.

        Returns the final local path.
        """
        track = self.resolve(permalink_url)
        download_url = self.authorized_download_url(track)

        destination = Path(destination).expanduser()
        destination.parent.mkdir(parents=True, exist_ok=True)

        with self.session.get(
            download_url,
            headers=self._auth_headers(),
            stream=True,
            allow_redirects=True,
            timeout=self.timeout,
        ) as response:
            self._raise_for_error(response)

            content_type = response.headers.get("Content-Type", "")
            if "text/html" in content_type.lower():
                raise SoundCloudError(
                    "Received HTML instead of audio; the download was rejected."
                )

            with destination.open("wb") as output:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        output.write(chunk)

        if destination.stat().st_size == 0:
            destination.unlink(missing_ok=True)
            raise SoundCloudError("The downloaded file was empty.")

        return destination
