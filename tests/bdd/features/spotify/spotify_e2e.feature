@e2e
Feature: Live Spotify API integration

  Connects to the real Spotify API to verify end-to-end behaviour.
  Skipped automatically if credentials are absent from .env.

  Requires in .env:
    SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

  Scenarios tagged @requires_refresh_token additionally require:
    SPOTIFY_REFRESH_TOKEN  (run scripts/spotify_auth.py first)

  Background:
    Given a SpotifyClient loaded from the environment

  Scenario: Can search the catalogue using client credentials
    When I search for tracks matching "Johnny B. Goode"
    Then the result should be a non-empty Polars DataFrame

  Scenario: Search results contain all expected columns
    When I search for tracks matching "Jolene"
    Then the DataFrame columns should include
      | column_name:string |
      | id                 |
      | uri                |
      | name               |
      | artists            |
      | album              |
      | release_date       |
      | duration_ms        |
      | popularity         |
      | explicit           |
      | thumbnail_url      |

  Scenario: Search for a well-known song returns the expected artist
    When I search for tracks matching "Bohemian Rhapsody"
    Then the results should include a track by "Queen"

  @requires_refresh_token
  Scenario: Authenticated user can fetch their playlists
    When I get the user's playlists
    Then the result should be a non-empty Polars DataFrame
    And the DataFrame columns should include
      | column_name:string |
      | id                 |
      | name               |
      | track_count        |
      | public             |
