"""A minimal connection picker — a popover listing the available docker targets.

Stands in for sshpilot's richer host picker. Local-first there's only the local
connection, but the popover is already list-driven so remote hosts appear here
once the SSH transport lands.
"""

from __future__ import annotations

from typing import Any, Callable, List, Optional

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


def show_host_picker(parent: Optional[Gtk.Window], anchor: Gtk.Widget,
                     on_picked: Callable[[Any], None], *,
                     toast: Optional[Callable[[str], None]] = None,
                     connections: Optional[List[Any]] = None) -> None:
    connections = list(connections or [])
    if not connections:
        if toast:
            toast("No docker connections")
        return

    popover = Gtk.Popover()
    popover.set_parent(anchor)
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2,
                  margin_top=4, margin_bottom=4, margin_start=4, margin_end=4)
    popover.set_child(box)

    for conn in connections:
        label = getattr(conn, "label", None) or getattr(conn, "nickname", "?")
        btn = Gtk.Button(label=label)
        btn.add_css_class("flat")
        btn.set_halign(Gtk.Align.FILL)
        child = btn.get_child()
        if isinstance(child, Gtk.Label):
            child.set_xalign(0)

        def _clicked(_b: Gtk.Button, c: Any = conn) -> None:
            popover.popdown()
            on_picked(c)

        btn.connect("clicked", _clicked)
        box.append(btn)

    popover.popup()
