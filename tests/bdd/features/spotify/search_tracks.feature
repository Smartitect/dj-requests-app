@unit
Feature: Search Spotify catalogue for tracks

  SpotifyClient.search_tracks() proxies the Spotify /search endpoint and
  returns results as a flat Polars DataFrame. All HTTP calls are mocked.

  Scenario: Valid response returns a DataFrame with the expected columns
    Given the Spotify search API returns the fixture "spotify/search_valid.json"
    When I search for tracks matching "Sweet Home Chicago"
    Then the result should be a Polars DataFrame with 2 rows
    And the DataFrame columns should include
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

  Scenario: Track fields are correctly parsed from the API response
    Given the Spotify search API returns the fixture "spotify/search_valid.json"
    When I search for tracks matching "Sweet Home Chicago"
    Then the result DataFrame should match
      | name:string        | artists:string | album:string                            | popularity:integer | explicit:boolean |
      | Sweet Home Chicago | Blues Brothers | The Blues Brothers                      | 62                 | false            |
      | Sweet Home Chicago | Robert Johnson | Robert Johnson: The Complete Recordings | 45                 | false            |

  Scenario: Multiple artists are joined into a single comma-separated string
    Given the Spotify search API returns the fixture "spotify/search_multi_artist.json"
    When I search for tracks matching "Under Pressure"
    Then the result DataFrame should match
      | name:string    | artists:string     |
      | Under Pressure | Queen, David Bowie |

  Scenario: Track with no album artwork has a null thumbnail_url
    Given the Spotify search API returns the fixture "spotify/search_no_artwork.json"
    When I search for tracks matching "test"
    Then the result DataFrame should match
      | name:string | thumbnail_url:string |
      | Test Track  | null                 |

  Scenario: HTTP error from the Spotify API raises an exception
    Given the Spotify search API returns status code 429
    When I search for tracks matching "Sweet Home Chicago"
    Then the call should fail with an HTTP error
