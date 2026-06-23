"""AppContext — the shim the Docker Console page/tabs were written against.

The UI was extracted from an sshpilot plugin where a ``PluginContext`` provided
``run_command`` / ``open_command_terminal`` / ``settings`` / ``list_connections``
/ ``run_on_ui_thread`` / ``ui.notify`` / ``acquire_multiplex`` /
``release_multiplex``. This object reproduces that surface exactly, backed by the
local connection registry + transport and the app window — so ``page.py`` and the
tab mixins run unchanged.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, List, Optional

from gi.repository import GLib

from .connections import ConnectionRegistry
from .result import CommandResult
from .settings import Settings

logger = logging.getLogger(__name__)


class _UiFacade:
    """``ctx.ui`` — the bits the page touches."""

    def __init__(self, window: Any) -> None:
        self._window = window

    def notify(self, message: str, *_a, **_k) -> None:
        if self._window is not None:
            self._window.toast(message)


class AppContext:
    def __init__(self, registry: ConnectionRegistry, settings: Settings,
                 window: Any = None) -> None:
        self._registry = registry
        self.settings = settings
        self._window = window
        self.ui = _UiFacade(window)

    def bind_window(self, window: Any) -> None:
        self._window = window
        self.ui = _UiFacade(window)

    # -- captured commands ------------------------------------------------
    def run_command(self, nickname: str, command: str, *,
                    timeout: float = 30) -> CommandResult:
        transport = self._registry.transport_for(nickname)
        if transport is None:
            return CommandResult(-1, "", f"No connection named {nickname!r}")
        return transport.run(command, timeout=timeout)

    # -- interactive / streamed commands ----------------------------------
    def open_command_terminal(self, nickname: str, command: str,
                              title: Optional[str] = None) -> bool:
        transport = self._registry.transport_for(nickname)
        if transport is None or self._window is None:
            return False
        try:
            return bool(transport.spawn_terminal(self._window, command, title=title))
        except Exception:  # noqa: BLE001 — surface as a failed open
            logger.debug("open_command_terminal failed", exc_info=True)
            return False

    # -- connections ------------------------------------------------------
    def list_connections(self) -> List[Any]:
        return self._registry.all()

    # -- threading --------------------------------------------------------
    def run_on_ui_thread(self, fn: Callable[..., Any], *args: Any) -> None:
        GLib.idle_add(lambda: (fn(*args), False)[1])

    # -- SSH connection reuse (no-op locally; SSH transport adds it later) -
    def acquire_multiplex(self, nickname: str) -> None:
        t = self._registry.transport_for(nickname)
        if t is not None:
            t.acquire_multiplex()

    def release_multiplex(self, nickname: str) -> None:
        t = self._registry.transport_for(nickname)
        if t is not None:
            t.release_multiplex()
