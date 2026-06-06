@unit
Feature: Manage the DJ's Spotify request playlist

  SpotifyClient methods for reading and writing the DJ's playlist,
  authenticated via a refresh token. All HTTP calls are mocked.

  Background:
    Given the Spotify token API returns a valid access token

  Scenario: get_playlists returns the user's playlists as a DataFrame
    Given the Spotify playlists API returns the fixture "spotify/playlists_valid.json"
    When I get the user's playlists
    Then the result should be a Polars DataFrame with 2 rows
    And the result DataFrame should match
      | name:string | track_count:integer | public:boolean |
      | DJ Requests | 3                   | true           |
      | My Mix      | 20                  | false          |

  Scenario: find_playlist_id returns the ID when the playlist exists
    Given the Spotify playlists API returns the fixture "spotify/playlists_valid.json"
    When I look up the playlist id for "DJ Requests"
    Then the result should be the playlist id "37i9dQZF1DXcBWIGoYBM5M"

  Scenario: find_playlist_id returns None when the playlist does not exist
    Given the Spotify playlists API returns the fixture "spotify/playlists_valid.json"
    When I look up the playlist id for "Does Not Exist"
    Then the result should be None

  Scenario: is_track_in_playlist returns True when the track is present
    Given the Spotify playlist tracks API returns the fixture "spotify/playlist_tracks_valid.json"
    When I check whether "spotify:track:4iJyoBOLtHqaWYs3827K6V" is in playlist "37i9dQZF1DXcBWIGoYBM5M"
    Then the result should be True

  Scenario: is_track_in_playlist returns False when the track is absent
    Given the Spotify playlist tracks API returns the fixture "spotify/playlist_tracks_valid.json"
    When I check whether "spotify:track:NOTINPLAYLIST" is in playlist "37i9dQZF1DXcBWIGoYBM5M"
    Then the result should be False

  Scenario: add_track_to_playlist posts to the Spotify API without error
    When I add track "spotify:track:4iJyoBOLtHqaWYs3827K6V" to playlist "37i9dQZF1DXcBWIGoYBM5M"
    Then the track should be added without error
