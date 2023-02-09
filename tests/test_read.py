"""Read Todoist data from the sever.

:author: Shay Hill
:created: 2023-02-06
"""

from todoist_tree import read_changes, headers
import os


class TestRead:
    def test_wrong_api_token(self, capfd):
        """Test that an invalid API token raises an exception."""
        headers_ = headers.new_headers("invalid_api_token")
        _ = read_changes.read_changes(headers_)
        out, _ = capfd.readouterr()
        msg_tail = "Please check your token and try again."
        assert msg_tail in out

    def test_valid_api_token(self):
        """Test that a valid API token does not raise an exception.

        This may not work, because the server may not be available when running the
        test. Won't happen often, but it could.
        """
        valid_api_token = os.environ["TODOIST_API_TOKEN"]
        headers_ = headers.new_headers(valid_api_token)
        todoist = read_changes.read_changes(headers_)
        assert todoist is not None
