"""Embedded Vte terminal tabs for interactive/streamed docker commands.

Used for ``docker exec -it`` (needs a real PTY), ``logs -f``, ``stats``, ``pull``,
and ``compose up/down``. The local transport hands us an argv (``/bin/sh -lc
<cmd>``); a future SSH transport would hand an ``ssh …`` argv to the same helper.
"""

from __future__ import annotations

import logging
from typing import List, Optional

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Vte", "3.91")
from gi.repository import GLib, Gtk, Vte, Pango  # noqa: E402

logger = logging.getLogger(__name__)


def make_terminal(argv: List[str]) -> Gtk.Widget:
    """Build a Vte terminal widget and spawn ``argv`` in it."""
    term = Vte.Terminal()
    term.set_scrollback_lines(100_000)
    term.set_font(Pango.FontDescription("monospace 11"))
    term.set_hexpand(True)
    term.set_vexpand(True)

    def _exited(_t: Vte.Terminal, status: int) -> None:
        try:
            term.feed(f"\r\n[process exited: {status}]\r\n".encode())
        except Exception:  # noqa: BLE001
            pass

    term.connect("child-exited", _exited)

    term.spawn_async(
        Vte.PtyFlags.DEFAULT,
        None,                       # cwd
        argv,
        None,                       # env
        GLib.SpawnFlags.DEFAULT,
        None, None,                 # child setup + data
        -1,                         # timeout
        None,                       # cancellable
        None,                       # callback
    )

    scroller = Gtk.ScrolledWindow()
    scroller.set_child(term)
    return scroller


def open_local_terminal(window, argv: List[str], title: Optional[str] = None) -> bool:
    """Add a terminal tab to ``window`` running ``argv``. Returns True on success."""
    try:
        widget = make_terminal(argv)
    except Exception:  # noqa: BLE001 — Vte missing / spawn refused
        logger.debug("could not create terminal", exc_info=True)
        return False
    window.add_terminal_tab(widget, title or "Terminal")
    return True
