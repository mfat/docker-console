"""JSON settings store: get/set + persistence."""

import os

from docker_console.settings import Settings


def test_get_default_and_set_roundtrip(tmp_path):
    path = os.path.join(tmp_path, "settings.json")
    s = Settings(path)
    assert s.get("refresh_interval", 10) == 10  # default
    s.set("refresh_interval", 15)
    s.set("sudo:local", True)
    # A fresh instance reads the persisted file.
    s2 = Settings(path)
    assert s2.get("refresh_interval") == 15
    assert s2.get("sudo:local") is True
    assert s2.get("missing", "fallback") == "fallback"


def test_set_same_value_is_idempotent(tmp_path):
    path = os.path.join(tmp_path, "s.json")
    s = Settings(path)
    s.set("k", 1)
    mtime = os.path.getmtime(path)
    s.set("k", 1)  # unchanged → no rewrite
    assert os.path.getmtime(path) == mtime


def test_corrupt_file_starts_fresh(tmp_path):
    path = os.path.join(tmp_path, "s.json")
    with open(path, "w") as fh:
        fh.write("{not json")
    s = Settings(path)
    assert s.get("anything", "d") == "d"
    s.set("ok", 1)  # still writable
    assert Settings(path).get("ok") == 1
