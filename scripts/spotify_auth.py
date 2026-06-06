"""
One-time Spotify OAuth setup.

Run with:  uv run python scripts/spotify_auth.py

Prerequisites:
  1. SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env
  2. Register http://127.0.0.1:8888/callback as a redirect URI in the
     Spotify Developer Dashboard (Dashboard → your app → Edit Settings → Redirect URIs)

On success, SPOTIFY_REFRESH_TOKEN is written to .env.
"""
import os
import urllib.parse
from pathlib import Path

import httpx
from dotenv import load_dotenv, set_key

REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "playlist-modify-public playlist-modify-private playlist-read-private"
ENV_PATH = Path(__file__).parent.parent / ".env"


def main() -> None:
    load_dotenv(ENV_PATH)

    client_id = os.environ["SPOTIFY_CLIENT_ID"]
    client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]

    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
    })

    print(f"\nPaste this URL into your browser:\n\n  {auth_url}\n")

    print("─" * 60)
    print("After you click Agree, the browser will redirect to a URL")
    print("that starts with:  http://127.0.0.1:8888/callback?code=...")
    print()
    print("The page will show 'connection refused' — that is expected.")
    print("Copy the FULL URL from the browser address bar and paste it below.")
    print("─" * 60)

    callback_url = input("\nCallback URL: ").strip()

    params = urllib.parse.parse_qs(urllib.parse.urlparse(callback_url).query)
    if "code" not in params:
        raise SystemExit(
            "No authorisation code found in the URL.\n"
            "Make sure you copied the full URL including the '?code=...' part."
        )

    resp = httpx.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": params["code"][0],
            "redirect_uri": REDIRECT_URI,
        },
        auth=(client_id, client_secret),
    )
    resp.raise_for_status()

    if not ENV_PATH.exists():
        ENV_PATH.touch()

    set_key(str(ENV_PATH), "SPOTIFY_REFRESH_TOKEN", resp.json()["refresh_token"])
    print(f"\n✓ Refresh token written to {ENV_PATH.name}")


if __name__ == "__main__":
    main()
