"""Real-GTK smoke (skips cleanly where GTK can't initialise)."""

import pytest


def _gtk_or_skip():
    try:
        import gi
        gi.require_version("Gtk", "4.0")
        gi.require_version("Adw", "1")
        from gi.repository import Gtk, Adw
        if not isinstance(getattr(Gtk, "MAJOR_VERSION", None), int):
            pytest.skip("gi is stubbed")
        if not Gtk.init_check():
            pytest.skip("GTK cannot initialise (no display)")
        Adw.init()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"GTK unavailable: {exc}")


def _ctx(tmp_path):
    from docker_console.connections import ConnectionRegistry
    from docker_console.context import AppContext
    from docker_console.settings import Settings
    return AppContext(ConnectionRegistry(), Settings(str(tmp_path / "s.json")))


def test_page_builds_seven_tabs(tmp_path):
    _gtk_or_skip()
    from docker_console.page import DockerConsolePage
    from docker_console.connections import LOCAL_NICKNAME

    page = DockerConsolePage(_ctx(tmp_path), initial_host=LOCAL_NICKNAME)
    names = []
    child = page._stack.get_first_child()
    while child is not None:
        names.append(page._stack.get_page(child).get_name())
        child = child.get_next_sibling()
    assert names == ["containers", "logs", "stats", "images",
                     "volumes", "networks", "compose"]
    # Local connection: no "via SSH" caption, friendly host label.
    assert page._via_label.get_label() == ""
    assert page._host_label.get_label() == "Local Docker"
    assert page._refresh_interval() == 10
