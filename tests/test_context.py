"""AppContext routes to the connection's transport and exposes the shim API."""

import types

from docker_console.connections import ConnectionRegistry, Connection
from docker_console.context import AppContext
from docker_console.result import CommandResult
from docker_console.settings import Settings


class _FakeTransport:
    location = "fake"

    def __init__(self):
        self.ran = []

    def run(self, command, *, timeout=30):
        self.ran.append((command, timeout))
        return CommandResult(0, "ok")

    def spawn_terminal(self, window, command, title=None):
        return True

    def acquire_multiplex(self):
        pass

    def release_multiplex(self):
        pass


def _ctx(tmp_path):
    reg = ConnectionRegistry()
    reg.add(Connection("fake", _FakeTransport(), kind="ssh", protocol="ssh"))
    return AppContext(reg, Settings(str(tmp_path / "s.json")))


def test_run_command_routes_to_transport(tmp_path):
    ctx = _ctx(tmp_path)
    res = ctx.run_command("fake", "docker ps", timeout=5)
    assert res.ok
    conn = next(c for c in ctx.list_connections() if c.nickname == "fake")
    assert conn.transport.ran == [("docker ps", 5)]


def test_run_command_unknown_connection(tmp_path):
    ctx = _ctx(tmp_path)
    res = ctx.run_command("nope", "docker ps")
    assert res.exit_code == -1 and "nope" in res.stderr


def test_list_connections_includes_local(tmp_path):
    ctx = _ctx(tmp_path)
    nicks = {c.nickname for c in ctx.list_connections()}
    assert "local" in nicks and "fake" in nicks


def test_run_on_ui_thread_invokes_fn(tmp_path):
    from gi.repository import GLib
    ctx = _ctx(tmp_path)
    got = []
    ctx.run_on_ui_thread(lambda a, b: got.append((a, b)), 1, 2)
    # Flush the default main context once so the idle callback fires.
    while GLib.MainContext.default().iteration(False):
        pass
    assert got == [(1, 2)]


def test_open_command_terminal_without_window_returns_false(tmp_path):
    ctx = _ctx(tmp_path)  # no window bound
    assert ctx.open_command_terminal("fake", "docker logs -f x") is False
