# DJ Requests App

A lightweight web app that lets audience members search the Spotify catalogue and submit song requests to the DJ's playlist — no Spotify account required. Audience members scan a QR code at the venue and use the mobile-friendly interface.

---

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- A Spotify Developer account and app (see setup below)

Install uv if you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.local/bin/env
```

---

## Quick Start

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd dj-requests-app
uv sync
```

### 2. Create a Spotify Developer App

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and log in.
2. Click **Create app** and fill in:
   - **App name:** DJ Requests App
   - **App description:** Enables audience members to search the Spotify catalogue and request songs.
   - **Website:** leave blank (or add your deployed URL later)
   - **Redirect URIs:** add `http://127.0.0.1:8888/callback` — this exact URI is required; `http://localhost` is **not** accepted.
   - **API/SDKs:** tick **Web API**
3. Save. Then go to **Settings** to find your **Client ID** and **Client Secret**.

### 3. Configure credentials

Copy the example env file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REFRESH_TOKEN=          # populated by the auth script below
SPOTIFY_PLAYLIST_NAME=DJ Requests
```

> `.env` is gitignored and will never be committed.

### 4. Create a request playlist in Spotify

In the Spotify app (or web player), create a playlist named **DJ Requests** (or whatever name you set in `SPOTIFY_PLAYLIST_NAME`). This is where audience requests will appear.

### 5. Authenticate with Spotify (one-time setup)

This step obtains a refresh token so the app can add tracks to your playlist on your behalf:

```bash
uv run python scripts/spotify_auth.py
```

A browser window will open for the Spotify consent screen. After approving, `SPOTIFY_REFRESH_TOKEN` is written to `.env` automatically.

---

## Explore the API

Open the exploration notebook to get a feel for the Spotify API responses and the Polars DataFrames produced by `SpotifyClient`:

```bash
uv run jupyter lab notebooks/spotify_exploration.ipynb
```

---

## Running Tests

### Unit tests (mocked — no credentials required)

```bash
uv run behave --tags @unit
```

### E2E tests (live Spotify API — credentials required)

Ensure `.env` is populated, then:

```bash
uv run behave --tags @e2e
```

Scenarios tagged `@requires_refresh_token` additionally need `SPOTIFY_REFRESH_TOKEN` in `.env`.

---

## Project Structure

```
src/
  spotify/               — SpotifyClient: search, playlist reads/writes
scripts/
  spotify_auth.py        — One-time OAuth helper; writes refresh token to .env
notebooks/
  spotify_exploration.ipynb  — API exploration notebook
tests/
  bdd/
    features/spotify/    — Gherkin feature files
    steps/               — Step definitions
    fixtures/spotify/    — Mock API response JSON fixtures
docs/
  REQUIREMENTS.md
  ARCHITECTURE.md
```

---

## Development Commands

```bash
uv sync                    # Install / update dependencies
uv add <package>           # Add a new dependency
uv run behave --tags @unit # Run unit tests
uv run behave --tags @e2e  # Run e2e tests
```
