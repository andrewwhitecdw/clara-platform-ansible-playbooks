"""Regression test for the remove-kubernetes file-removal path.

The install-kubernetes role copies flannel and plugin manifests to
``/tmp`` on the remote host. The remove-kubernetes role must therefore
use the absolute ``/tmp/{{item}}`` path when deleting them. A relative
``tmp/{{item}}`` path would resolve against the remote user's home
directory and silently leave the files behind.
"""

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_FILE = (
    REPO_ROOT
    / "playbooks"
    / "roles"
    / "remove-kubernetes"
    / "tasks"
    / "remove-kubernetes.yml"
)
TASK_NAME = "Remove Kubernetes Files from Remote Host"


def test_remove_kubernetes_uses_absolute_tmp_path():
    assert TASK_FILE.exists(), f"Task file not found: {TASK_FILE}"

    with TASK_FILE.open() as f:
        tasks = list(yaml.safe_load_all(f))

    found = False
    for doc in tasks:
        if doc is None:
            continue
        for task in doc:
            if not isinstance(task, dict):
                continue
            if task.get("name") == TASK_NAME:
                found = True
                path = task.get("file", {}).get("path")
                assert path is not None, f"'{TASK_NAME}' task has no file.path"
                assert path.startswith("/tmp/"), (
                    f"'{TASK_NAME}' uses a non-absolute tmp path: {path!r}"
                )

    assert found, f"Task '{TASK_NAME}' not found in {TASK_FILE}"


if __name__ == "__main__":
    test_remove_kubernetes_uses_absolute_tmp_path()
    print("OK")
