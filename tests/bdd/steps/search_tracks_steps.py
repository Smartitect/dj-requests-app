"""Given/When steps for search_tracks feature (unit and e2e)."""
import json
from pathlib import Path
from unittest.mock import patch

from behave import given, when

from spotify_shared_steps import make_mock_response, _TOKEN_JSON

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


@given('the Spotify search API returns the fixture "{fixture_path}"')
def step_mock_search_fixture(context, fixture_path):
    context.mock_search_json = json.loads((FIXTURES_DIR / fixture_path).read_text())
    context.mock_search_status = 200


@given("the Spotify search API returns status code {status_code:d}")
def step_mock_search_error(context, status_code):
    context.mock_search_json = None
    context.mock_search_status = status_code


@when('I search for tracks matching "{query}"')
def step_search_tracks(context, query):
    from spotify import SpotifyClient

    if hasattr(context, "client"):
        # E2E mode: real client set up by the Background step
        try:
            context.result = context.client.search_tracks(query)
            context.error = None
        except Exception as e:
            context.result = None
            context.error = e
        return

    # Unit mode: mock HTTP
    token_mock = make_mock_response(200, _TOKEN_JSON)
    search_mock = make_mock_response(
        context.mock_search_status,
        context.mock_search_json,
    )
    with patch("httpx.post", return_value=token_mock), \
         patch("httpx.get", return_value=search_mock):
        client = SpotifyClient("test_id", "test_secret")
        try:
            context.result = client.search_tracks(query)
            context.error = None
        except Exception as e:
            context.result = None
            context.error = e
