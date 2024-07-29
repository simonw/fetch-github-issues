import json
import os
import tempfile
from unittest.mock import patch, Mock, call, ANY

import pytest

from fetch_github_issues import cli


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.fixture
def mock_connection():
    with patch("fetch_github_issues.cli.http.client.HTTPSConnection") as mock:
        yield mock


def test_fetch_single_issue(temp_dir, mock_connection):
    mock_response = Mock()
    mock_response.status = 200
    mock_response.read.return_value = json.dumps(
        {
            "number": 1,
            "title": "Test Issue",
            "comments_url": "https://api.github.com/repos/owner/repo/issues/1/comments",
        }
    ).encode()
    mock_response.getheader.return_value = ""

    mock_connection.return_value.getresponse.return_value = mock_response

    cli.fetch_github_issues("owner/repo", [1], temp_dir, "test_api_key")

    expected_calls = [
        call("GET", "/repos/owner/repo/issues/1", headers=ANY),
        call(
            "GET",
            "https://api.github.com/repos/owner/repo/issues/1/comments",
            headers=ANY,
        ),
    ]
    assert mock_connection.return_value.request.call_args_list == expected_calls

    assert os.path.exists(os.path.join(temp_dir, "1.json"))


def test_fetch_all_issues(temp_dir, mock_connection):
    mock_response = Mock()
    mock_response.status = 200
    mock_response.read.side_effect = [
        json.dumps(
            [
                {
                    "number": 1,
                    "title": "Issue 1",
                    "comments_url": "https://api.github.com/repos/owner/repo/issues/1/comments",
                },
                {
                    "number": 2,
                    "title": "Issue 2",
                    "comments_url": "https://api.github.com/repos/owner/repo/issues/2/comments",
                },
            ]
        ).encode(),
        json.dumps([]).encode(),  # Empty response for comments
        json.dumps([]).encode(),  # Empty response for comments
    ]
    mock_response.getheader.return_value = ""

    mock_connection.return_value.getresponse.return_value = mock_response

    cli.fetch_github_issues("owner/repo", None, temp_dir, "test_api_key")

    expected_calls = [
        call("GET", "/repos/owner/repo/issues", headers=ANY),
        call(
            "GET",
            "https://api.github.com/repos/owner/repo/issues/1/comments",
            headers=ANY,
        ),
        call(
            "GET",
            "https://api.github.com/repos/owner/repo/issues/2/comments",
            headers=ANY,
        ),
    ]
    assert mock_connection.return_value.request.call_args_list == expected_calls

    assert os.path.exists(os.path.join(temp_dir, "1.json"))
    assert os.path.exists(os.path.join(temp_dir, "2.json"))


@pytest.mark.parametrize("api_key", [None, "test_api_key"])
def test_api_key_from_env(temp_dir, mock_connection, api_key):
    mock_response = Mock()
    mock_response.status = 200
    mock_response.read.return_value = json.dumps(
        {
            "number": 1,
            "title": "Test Issue",
            "comments_url": "https://api.github.com/repos/owner/repo/issues/1/comments",
        }
    ).encode()
    mock_response.getheader.return_value = ""

    mock_connection.return_value.getresponse.return_value = mock_response

    with patch.dict(os.environ, {"GITHUB_TOKEN": "test_env_api_key"}):
        cli.fetch_github_issues("owner/repo", [1], temp_dir, api_key)

    headers = mock_connection.return_value.request.call_args[1]["headers"]
    expected_token = "test_api_key" if api_key else "test_env_api_key"
    assert headers["Authorization"] == f"token {expected_token}"


def test_non_200_status_code(temp_dir, mock_connection):
    mock_response = Mock()
    mock_response.status = 404
    mock_response.reason = "Not Found"

    mock_connection.return_value.getresponse.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        cli.fetch_github_issues("owner/repo", [1], temp_dir, "test_api_key")

    assert str(exc_info.value) == "HTTP request failed with status code 404: Not Found"
