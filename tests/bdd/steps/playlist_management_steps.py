"""Given/When/Then steps for playlist_management feature (unit and e2e)."""
import json
import os
from pathlib import Path
from unittest.mock import patch

from behave import given, when, then

from spotify_shared_steps import make_mock_response, _TOKEN_JSON

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


@given("the Spotify token API returns a valid access token")
def step_mock_token(context):
    context.mock_token_json = _TOKEN_JSON


@given('the Spotify playlists API returns the fixture "{fixture_path}"')
def step_mock_playlists(context, fixture_path):
    context.mock_playlists_json = json.loads((FIXTURES_DIR / fixture_path).read_text())


@given('the Spotify playlist tracks API returns the fixture "{fixture_path}"')
def step_mock_playlist_tracks(context, fixture_path):
    context.mock_playlist_tracks_json = json.loads((FIXTURES_DIR / fixture_path).read_text())


@when("I get the user's playlists")
def step_get_playlists(context):
    from spotify import SpotifyClient

    if hasattr(context, "client"):
        # E2E mode
        from dotenv import load_dotenv
        load_dotenv()
        if not os.getenv("SPOTIFY_REFRESH_TOKEN"):
            context.scenario.skip("SPOTIFY_REFRESH_TOKEN not set in .env")
            return
        try:
            context.result = context.client.get_playlists()
            context.error = None
        except Exception as e:
            context.result = None
            context.error = e
        return

    # Unit mode
    token_mock = make_mock_response(200, context.mock_token_json)
    playlists_mock = make_mock_response(200, context.mock_playlists_json)
    with patch("httpx.post", return_value=token_mock), \
         patch("httpx.get", return_value=playlists_mock):
        client = SpotifyClient("test_id", "test_secret", refresh_token="mock_refresh")
        try:
            context.result = client.get_playlists()
            context.error = None
        except Exception as e:
            context.result = None
            context.error = e


@when('I look up the playlist id for "{playlist_name}"')
def step_find_playlist_id(context, playlist_name):
    from spotify import SpotifyClient

    token_mock = make_mock_response(200, context.mock_token_json)
    playlists_mock = make_mock_response(200, context.mock_playlists_json)
    with patch("httpx.post", return_value=token_mock), \
         patch("httpx.get", return_value=playlists_mock):
        client = SpotifyClient("test_id", "test_secret", refresh_token="mock_refresh")
        try:
            context.result = client.find_playlist_id(playlist_name)
            context.error = None
        except Exception as e:
            context.result = None
            context.error = e


@when('I check whether "{track_uri}" is in playlist "{playlist_id}"')
def step_check_track_in_playlist(context, track_uri, playlist_id):
    from spotify import SpotifyClient

    token_mock = make_mock_response(200, context.mock_token_json)
    tracks_mock = make_mock_response(200, context.mock_playlist_tracks_json)
    with patch("httpx.post", return_value=token_mock), \
         patch("httpx.get", return_value=tracks_mock):
        client = SpotifyClient("test_id", "test_secret", refresh_token="mock_refresh")
        try:
            context.result = client.is_track_in_playlist(playlist_id, track_uri)
            context.error = None
        except Exception as e:
            context.result = None
            context.error = e


@when('I add track "{track_uri}" to playlist "{playlist_id}"')
def step_add_track(context, track_uri, playlist_id):
    from spotify import SpotifyClient

    def _post_side_effect(url, **kwargs):
        if "api/token" in str(url):
            return make_mock_response(200, context.mock_token_json)
        return make_mock_response(201, {"snapshot_id": "abc123"})

    with patch("httpx.post", side_effect=_post_side_effect):
        client = SpotifyClient("test_id", "test_secret", refresh_token="mock_refresh")
        try:
            client.add_track_to_playlist(playlist_id, track_uri)
            context.error = None
        except Exception as e:
            context.error = e


@then('the result should be the playlist id "{expected_id}"')
def step_assert_playlist_id(context, expected_id):
    assert context.error is None, f"Unexpected error: {context.error}"
    assert context.result == expected_id, \
        f"Expected playlist id '{expected_id}', got '{context.result}'"


@then("the result should be None")
def step_assert_none(context):
    assert context.error is None, f"Unexpected error: {context.error}"
    assert context.result is None, f"Expected None, got '{context.result}'"


@then("the result should be True")
def step_assert_true(context):
    assert context.error is None, f"Unexpected error: {context.error}"
    assert context.result is True, f"Expected True, got '{context.result}'"


@then("the result should be False")
def step_assert_false(context):
    assert context.error is None, f"Unexpected error: {context.error}"
    assert context.result is False, f"Expected False, got '{context.result}'"


@then("the track should be added without error")
def step_assert_track_added(context):
    assert context.error is None, f"Unexpected error adding track: {context.error}"
