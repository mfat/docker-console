"""Adw.Application bootstrap for Docker Console."""

from __future__ import annotations

import os

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw  # noqa: E402

APP_ID = "io.github.mfat.dockerconsole"


class DockerConsoleApplication(Adw.Application):
    def __init__(self) -> None:
        super().__init__(application_id=APP_ID,
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self._window = None

    def do_activate(self) -> None:
        # Make bundled icons (the Docker brand symbolic) resolvable by name.
        from gi.repository import Gdk
        display = Gdk.Display.get_default()
        icons_dir = os.path.join(os.path.dirname(__file__), "resources", "icons")
        if display is not None and os.path.isdir(icons_dir):
            Gtk.IconTheme.get_for_display(display).add_search_path(icons_dir)

        if self._window is None:
            from .window import DockerConsoleWindow
            self._window = DockerConsoleWindow(self)
        self._window.present()


def main(argv=None) -> int:
    import sys
    return DockerConsoleApplication().run(argv if argv is not None else sys.argv)
