# Architecture

## Spotify API

Spotify's Web API covers both core requirements.

**Searching the catalogue** — the `/search` endpoint lets the app query tracks, artists, albums, etc. This works with the *Client Credentials* flow (app-level authentication), so audience members can search without signing into Spotify.

**Adding to a playlist** — modifying a playlist (`POST /playlists/{id}/tracks`) requires the *Authorization Code* flow with the `playlist-modify-public` or `playlist-modify-private` scope. The app holds the DJ's credentials server-side and adds tracks to the playlist on their behalf; audience members never need a Spotify account.

### Known Constraints

| Constraint | Detail |
|---|---|
| No audio previews | Spotify removed preview URLs from new apps in late 2024. Not relevant to this app. |
| Development mode quota | New apps are capped at 25 manually allowlisted users. A publicly accessible request app requires Spotify's *Extended Quota Mode* — an application must be submitted to Spotify for review before going live. |
| Rate limits | Generous at event scale; not an expected bottleneck. |
| Redirect URI rules | Since April 2025, Spotify enforces HTTPS-only redirect URIs for all new clients. The only permitted HTTP exception is loopback literals (`http://127.0.0.1`). `http://localhost` is **not** accepted — use `http://127.0.0.1:{port}` for local development and `https://{domain}/callback` in production. Both URIs must be registered in the Spotify Developer Dashboard. |
| Credentials | The client secret and refresh token must never be sent to the browser. |

### Authentication Flow

The app uses two separate Spotify auth flows:

1. **Client Credentials** (search) — used for all catalogue searches. No user context required; token is obtained automatically by the backend using the app's client ID and secret.
2. **Authorization Code** (playlist writes) — used to add tracks to the DJ's playlist. Requires a one-time manual OAuth step (see [Setup](#setup)) to obtain a refresh token, which the backend exchanges for short-lived access tokens at runtime.

---

## Application

A simple, lightweight **single-page web app** — no login required for audience members.

The frontend is a mobile-first responsive interface served by the Python backend. The DJ shares the app URL via a QR code displayed at the venue.

### Pages / Routes

| Route | Description |
|---|---|
| `GET /` | Main search interface — audience-facing |
| `GET /api/search?q=` | Backend proxy to Spotify search; returns track list |
| `POST /api/request/{track_id}` | Adds the selected track to the DJ's request playlist; returns conflict if already present |

### Duplicate Request Handling

Before adding a track, the backend checks whether it is already in the playlist. If it is, the API returns a `409 Conflict` response and the UI displays an "already requested" message, prompting the user to choose a different song.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Web framework | **FastAPI** |
| HTTP client (Spotify API) | `httpx` (async, compatible with FastAPI) |
| Frontend | Vanilla HTML/CSS/JS (single page, served as a static file by FastAPI) |
| Configuration | `.env` file (excluded from source control) |
| Containerisation | Docker |
| Hosting | Azure Container Apps |

---

## Setup

### One-time Spotify OAuth

The app requires a refresh token scoped to the DJ's Spotify account. This is obtained once by running a helper script:

```bash
uv run python scripts/spotify_auth.py
```

The script opens a browser for the Spotify consent screen. On approval, it writes `SPOTIFY_REFRESH_TOKEN` to the local `.env` file. This step does not need to be repeated unless the token is revoked.

> **Redirect URI requirement:** Spotify no longer accepts `http://localhost` as a redirect URI (enforced for all new clients since April 2025). The script must use `http://127.0.0.1:{port}` as the redirect URI. This exact URI must be registered in the Spotify Developer Dashboard under the app's client settings before running the script.

### Configuration

All runtime configuration lives in a `.env` file (gitignored):

```dotenv
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
SPOTIFY_REFRESH_TOKEN=...
SPOTIFY_PLAYLIST_NAME=DJ Requests
```

The `SPOTIFY_PLAYLIST_NAME` key is the only setting that changes between gigs. It must match the name of a playlist already created in the DJ's Spotify account.

---

## Hosting

The app is packaged as a Docker container and deployed as an **Azure Container App**. The public URL produced by the deployment is what the DJ encodes into the QR code for display at the venue.
