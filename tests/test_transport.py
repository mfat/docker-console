"""LocalTransport runs captured commands via subprocess (mocked)."""

import subprocess
import types

import pytest

from docker_console.transport.local import LocalTransport
from docker_console.result import CommandResult


def test_run_captures_exit_stdout_stderr(monkeypatch):
    seen = {}

    def fake_run(argv, **kwargs):
        seen["argv"] = argv
        seen["timeout"] = kwargs.get("timeout")
        return types.SimpleNamespace(returncode=0, stdout="out", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    res = LocalTransport().run("docker ps -q", timeout=12)
    assert isinstance(res, CommandResult)
    assert seen["argv"] == ["/bin/sh", "-lc", "docker ps -q"]
    assert seen["timeout"] == 12
    assert res.exit_code == 0 and res.stdout == "out" and res.ok


def test_run_nonzero(monkeypatch):
    monkeypatch.setattr(subprocess, "run",
                        lambda *a, **k: types.SimpleNamespace(
                            returncode=1, stdout="", stderr="boom"))
    res = LocalTransport().run("docker bogus")
    assert res.exit_code == 1 and res.stderr == "boom" and not res.ok


def test_run_timeout(monkeypatch):
    def fake_run(*a, **k):
        raise subprocess.TimeoutExpired(cmd="x", timeout=1)

    monkeypatch.setattr(subprocess, "run", fake_run)
    res = LocalTransport().run("docker ps", timeout=1)
    assert res.exit_code == -1 and "timed out" in res.stderr.lower()


def test_run_oserror(monkeypatch):
    def fake_run(*a, **k):
        raise OSError("no /bin/sh")

    monkeypatch.setattr(subprocess, "run", fake_run)
    res = LocalTransport().run("docker ps")
    assert res.exit_code == -1 and "no /bin/sh" in res.stderr
