"""Given step that sets up a real SpotifyClient from .env for e2e tests."""
import os
from dotenv import load_dotenv
from behave import given


@given("a SpotifyClient loaded from the environment")
def step_load_client_from_env(context):
    load_dotenv()
    if not os.getenv("SPOTIFY_CLIENT_ID") or not os.getenv("SPOTIFY_CLIENT_SECRET"):
        context.scenario.skip(
            "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env to run e2e tests"
        )
        return
    from spotify import SpotifyClient
    context.client = SpotifyClient.from_env()
