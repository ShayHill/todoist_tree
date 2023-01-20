# todoist_tree

These are the core functions of [todoist_bot](https://github.com/ShayHill/todoist_bot).

The reading and writing functions are just (sometimes typeguarded) aliases of Todoist api calls. The differentiating functionality is building a tree with

``` python
import time
from todoist_tree import headers
from todoist_tree import read_changes
from todoist_tree import tree

headers = new_headers(api_token)
todoist = None
sync_token: str = "*"

complete = False

while not complete:

    todoist = read_changes.read_changes(headers)
    if todoist is None:
        # no changes or failure
        time.sleep(2)
        continue

    sync_token = todoist.sync_token

    projects = todoist.projects
    sections = todoist.sections
    tasks = todoist.tasks

    id2node = tree.map_id_to_branch(
        todoist.projects,
        todoist.sections,
        todoist.tasks
    )

    # do something here

    time.sleep(5)
```

The tree isn't doesn't have one root. `map_id_to_branch` maps the id[1] of each project, section, and task to a node. Top-level projects will not have parents, so they are effectively roots of their own trees.

See [todoist_bot](https://github.com/ShayHill/todoist_bot) for a full example.

[1] where `id` is the value returned in the json dictionary from the Todoist api, *not* the Python object id.
