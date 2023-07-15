"""Ask for an API token, read the data, then explore with a REPL.

:author: Shay Hill
:created: 2023-07-15
"""

from todoist_tree import read_changes, headers

token = "put token here to test"


class TestRead:
    def test_read_repl(self):
        """Read data from Todoist and explore with a REPL."""
        _ = read_changes.read_changes(headers.new_headers(token))
        # breakpoint()
