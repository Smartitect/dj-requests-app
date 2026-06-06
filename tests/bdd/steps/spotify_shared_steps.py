"""Shared assertion steps used across both unit and e2e Spotify tests."""
import httpx
from unittest.mock import Mock
from behave import then


def make_mock_response(status_code: int, json_data=None) -> Mock:
    """Build a mock httpx response. Raises HTTPStatusError for 4xx/5xx."""
    mock = Mock()
    mock.status_code = status_code
    if json_data is not None:
        mock.json.return_value = json_data
    if status_code >= 400:
        mock.raise_for_status.side_effect = httpx.HTTPStatusError(
            f"HTTP {status_code}", request=Mock(), response=mock
        )
    else:
        mock.raise_for_status.return_value = None
    return mock


_TOKEN_JSON = {"access_token": "mock_access_token", "token_type": "Bearer", "expires_in": 3600}


@then("the result should be a Polars DataFrame with {n:d} rows")
def step_assert_row_count(context, n):
    assert context.error is None, f"Unexpected error: {context.error}"
    assert context.result is not None, "No result returned"
    assert len(context.result) == n, f"Expected {n} rows, got {len(context.result)}"


@then("the result should be a non-empty Polars DataFrame")
def step_assert_non_empty(context):
    assert context.error is None, f"Unexpected error: {context.error}"
    assert context.result is not None, "No result returned"
    assert len(context.result) > 0, "Result DataFrame is empty"


@then("the DataFrame columns should include")
def step_assert_columns_include(context):
    assert context.error is None, f"Unexpected error: {context.error}"
    expected_cols = [row.cells[0] for row in context.table]
    for col in expected_cols:
        assert col in context.result.columns, \
            f"Column '{col}' not found. Actual columns: {context.result.columns}"


@then("the call should fail with an HTTP error")
def step_assert_http_error(context):
    assert context.error is not None, "Expected an error but none was raised"
    assert isinstance(context.error, httpx.HTTPStatusError), \
        f"Expected httpx.HTTPStatusError, got {type(context.error).__name__}: {context.error}"


@then('the results should include a track by "{artist}"')
def step_results_include_artist(context, artist):
    assert context.error is None, f"Unexpected error: {context.error}"
    assert context.result is not None, "No result returned"
    artists_col = context.result["artists"].to_list()
    assert any(artist in a for a in artists_col), \
        f"No track by '{artist}' found. Sample artists: {artists_col[:5]}"
