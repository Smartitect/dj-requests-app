"""Spotify Web API client for the DJ Requests app."""
import os
import time
from typing import Any

import httpx
import polars as pl
from dotenv import load_dotenv


class SpotifyClient:
    """
    Thin wrapper around the Spotify Web API.

    Client Credentials flow is used for catalogue search (no user context required).
    Authorization Code flow (via refresh token) is used for playlist reads and writes.
    """

    _ACCOUNTS = "https://accounts.spotify.com/api/token"
    _API = "https://api.spotify.com/v1"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str | None = None,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._client_token: str | None = None
        self._client_token_expiry: float = 0.0
        self._user_token: str | None = None
        self._user_token_expiry: float = 0.0

    @classmethod
    def from_env(cls) -> "SpotifyClient":
        """Construct a client from environment variables (loads .env automatically)."""
        load_dotenv()
        return cls(
            client_id=os.environ["SPOTIFY_CLIENT_ID"],
            client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
            refresh_token=os.getenv("SPOTIFY_REFRESH_TOKEN"),
        )

    # ------------------------------------------------------------------
    # Token management
    # ------------------------------------------------------------------

    def _client_auth_headers(self) -> dict[str, str]:
        """Bearer token via Client Credentials — auto-refreshes on expiry."""
        if not self._client_token or time.monotonic() >= self._client_token_expiry:
            resp = httpx.post(
                self._ACCOUNTS,
                data={"grant_type": "client_credentials"},
                auth=(self._client_id, self._client_secret),
            )
            resp.raise_for_status()
            data = resp.json()
            self._client_token = data["access_token"]
            self._client_token_expiry = time.monotonic() + data["expires_in"] - 60
        return {"Authorization": f"Bearer {self._client_token}"}

    def _user_auth_headers(self) -> dict[str, str]:
        """Bearer token via refresh token — auto-refreshes on expiry."""
        if not self._refresh_token:
            raise ValueError(
                "No refresh token set. Run `uv run python scripts/spotify_auth.py` first."
            )
        if not self._user_token or time.monotonic() >= self._user_token_expiry:
            resp = httpx.post(
                self._ACCOUNTS,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self._refresh_token,
                },
                auth=(self._client_id, self._client_secret),
            )
            resp.raise_for_status()
            data = resp.json()
            self._user_token = data["access_token"]
            self._user_token_expiry = time.monotonic() + data["expires_in"] - 60
        return {"Authorization": f"Bearer {self._user_token}"}

    # ------------------------------------------------------------------
    # Search (Client Credentials)
    # ------------------------------------------------------------------

    def search_tracks(self, query: str, limit: int = 20) -> pl.DataFrame:
        """Search the Spotify catalogue and return matching tracks as a DataFrame."""
        resp = httpx.get(
            f"{self._API}/search",
            params={"q": query, "type": "track", "limit": limit},
            headers=self._client_auth_headers(),
        )
        resp.raise_for_status()
        return self._parse_tracks(resp.json()["tracks"]["items"])

    def get_raw_search(self, query: str, limit: int = 5) -> dict[str, Any]:
        """Return the raw Spotify JSON response — useful for exploring the schema."""
        resp = httpx.get(
            f"{self._API}/search",
            params={"q": query, "type": "track", "limit": limit},
            headers=self._client_auth_headers(),
        )
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Playlists (Authorization Code)
    # ------------------------------------------------------------------

    def get_playlists(self) -> pl.DataFrame:
        """Return the authenticated user's playlists as a DataFrame."""
        resp = httpx.get(
            f"{self._API}/me/playlists",
            params={"limit": 50},
            headers=self._user_auth_headers(),
        )
        resp.raise_for_status()
        return pl.DataFrame([
            {
                "id": p["id"],
                "name": p["name"],
                "track_count": p["tracks"]["total"],
                "public": p["public"],
            }
            for p in resp.json()["items"]
        ])

    def find_playlist_id(self, playlist_name: str) -> str | None:
        """Return the Spotify playlist ID matching the given name, or None."""
        df = self.get_playlists()
        match = df.filter(pl.col("name") == playlist_name)
        return match["id"][0] if not match.is_empty() else None

    def get_playlist_tracks(self, playlist_id: str) -> pl.DataFrame:
        """Return all tracks in a playlist as a DataFrame."""
        resp = httpx.get(
            f"{self._API}/playlists/{playlist_id}/tracks",
            headers=self._user_auth_headers(),
        )
        resp.raise_for_status()
        tracks = [entry["track"] for entry in resp.json()["items"] if entry["track"]]
        return self._parse_tracks(tracks)

    def is_track_in_playlist(self, playlist_id: str, track_uri: str) -> bool:
        """Return True if the track URI is already in the playlist."""
        return track_uri in self.get_playlist_tracks(playlist_id)["uri"].to_list()

    def add_track_to_playlist(self, playlist_id: str, track_uri: str) -> None:
        """Append a track to the playlist. Raises httpx.HTTPStatusError on failure."""
        resp = httpx.post(
            f"{self._API}/playlists/{playlist_id}/tracks",
            json={"uris": [track_uri]},
            headers=self._user_auth_headers(),
        )
        resp.raise_for_status()

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_tracks(items: list[dict]) -> pl.DataFrame:
        rows = []
        for t in items:
            images = t["album"].get("images", [])
            rows.append({
                "id": t["id"],
                "uri": t["uri"],
                "name": t["name"],
                "artists": ", ".join(a["name"] for a in t["artists"]),
                "album": t["album"]["name"],
                "release_date": t["album"]["release_date"],
                "duration_ms": t["duration_ms"],
                "popularity": t["popularity"],
                "explicit": t["explicit"],
                "thumbnail_url": images[-1]["url"] if images else None,
            })
        return pl.DataFrame(rows)
