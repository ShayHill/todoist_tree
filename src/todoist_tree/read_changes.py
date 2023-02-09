"""Sync with Todoist and return data.

Only return data if changes have been made since last sync or if explicitly called
with sync_token = "*".

This module already catches and bypasses any expected exceptions. If something goes
wrong with the sync, it will return None. Handle this in main.py by sleeping a bit
then trying again.

:author: Shay Hill
:created: 2022-12-28
"""

from __future__ import annotations

import json
import time
import sys
from typing import TYPE_CHECKING, Any

import requests
from pydantic import BaseModel

from todoist_tree.headers import SYNC_URL

if TYPE_CHECKING:

    from requests.structures import CaseInsensitiveDict

# error codes with special handling
_UNAUTHORIZED = 401
_FORBIDDEN = 403

# This is everything this project will look at.
_RESOURCE_TYPES = ("notes", "items", "labels", "projects", "sections")


class _Model(BaseModel):
    """Base model for type casting Todoist response."""

    id: str


class Comment(_Model):
    """Todoist comment (note)."""

    added_at: str = ""
    added_by_uid: str = ""
    child_order: int = 0
    content: str = ""
    item_id: str = ""
    user_id: str = ""


class Label(_Model):
    """Todoist label."""

    name: str


class Project(_Model):
    """Todoist project."""

    name: str
    child_order: int
    parent_id: str | None = None


class Section(_Model):
    """Todoist section."""

    name: str
    section_order: int
    project_id: str


class Task(_Model):
    """Todoist task (item)."""

    added_at: str = ""
    added_by_uid: str = ""
    assigned_by_uid: str | None = None
    child_order: int = 0
    content: str = ""
    description: str = ""
    labels: list[str] = []
    parent_id: str | None = None
    priority: int = 0
    project_id: str | None = ""
    section_id: str | None = None


class _Response(BaseModel):
    """Todoist sync response."""

    full_sync: bool
    sync_token: str
    notes: list[Comment]
    labels: list[dict[str, Any]]
    projects: list[dict[str, Any]]
    sections: list[dict[str, Any]]
    items: list[dict[str, Any]]


class Todoist:
    """Todist data model.

    The api just returns projects, sections, tasks, etc. as a dictionary of lists of
    dictionaries. The only way to distinguish a task from a project, for instance, is
    to look at the dictionary keys or pass around the entire export json dictionary
    and take "item" or "project" keys from it. That works, but it makes things like
    isintance() (and other nice ways to sort objects) a little less straightforward.
    """

    def __init__(self, resp_json: _Response) -> None:
        """Initialize a Todoist object from a Todoist response.json().

        :param resp_json: The response.json() from a Todoist API call

        For any resource type with an associated _Model class in _RESOURCE_TYPES,
        create a list of _Model instances. For resource types with a None value in
        _RESOURCE_TYPES, assign the returned value to an attribute of the same name.
        """
        self.sync_token = resp_json.sync_token
        self.comments = resp_json.notes
        self.labels = [Label(**x) for x in resp_json.labels]
        self.projects = [Project(**x) for x in resp_json.projects]
        self.sections = [Section(**x) for x in resp_json.sections]
        self.tasks = [Task(**x) for x in resp_json.items]


def read_changes(
    headers: CaseInsensitiveDict[str], sync_token: str = "*"
) -> Todoist | None:
    """Load changes from Todoist or raise exception.

    :param headers: Headers for the request (produced by headers.get_headers)
    :param sync_token: Token to sync from. If any changes are found, will request
        again with "*" to return all data.
    :return: Todoist data as a Todoist instance or None if no changes have been made.

    If no changes have been made or sync fails, return an empty dictionary.
    If any changes have been made, request and return ALL data, not just the changes.
    """
    data = {"sync_token": sync_token, "resource_types": list(_RESOURCE_TYPES)}
    try:
        resp = requests.post(SYNC_URL, headers=headers, data=json.dumps(data))
        resp.raise_for_status()
    # specific error messages for common errors
    except requests.exceptions.HTTPError as e:
        msg_tail = "Please check your token and try again."
        if e.response.status_code == _UNAUTHORIZED:
            _ = sys.stdout.write(f"Invalid API token. {msg_tail}\n")
        elif e.response.status_code == _FORBIDDEN:
            _ = sys.stdout.write(f"API token does not have access. {msg_tail}\n")
        else:
            _ = sys.stdout.write(f"Failed to reach Todoist: {e}\n")
        return None
    except Exception as e:
        _ = sys.stdout.write(f"Failed to reach Todoist: {e}\n")
        return None

    resp_json = _Response(**resp.json())

    if not any(getattr(resp_json, r) for r in _RESOURCE_TYPES):
        return None

    if not resp_json.full_sync:
        # changes have been made, return all data
        time.sleep(1)
        return read_changes(headers)

    return Todoist(resp_json)
