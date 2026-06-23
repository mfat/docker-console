"""Transport abstraction — the seam between the UI and *where* docker runs.

A transport knows how to run a captured command and how to open an interactive
terminal for it. The local transport runs on this machine; a future SSH transport
runs on a remote host over the same interface (see ``ssh.py``). The whole point of
this module is that the UI and :class:`docker_console.client.DockerClient` never
care which one they're talking to.
"""

from __future__ import annotations

import abc
from typing import Any, Optional

from ..result import CommandResult


class Transport(abc.ABC):
    """Runs docker/podman commands somewhere (local machine, remote host, …)."""

    #: Short, human-facing description of where this runs (e.g. "Local machine").
    location: str = ""

    @abc.abstractmethod
    def run(self, command: str, *, timeout: float = 30) -> CommandResult:
        """Run a captured shell command and return its result. Never raises for
        a non-zero exit — that's encoded in :attr:`CommandResult.exit_code`."""

    @abc.abstractmethod
    def spawn_terminal(self, window: Any, command: str,
                       title: Optional[str] = None) -> bool:
        """Open an interactive terminal tab in ``window`` running ``command``.
        Returns True if the terminal was opened."""

    # ControlMaster-style connection reuse is an SSH concept; local is a no-op.
    def acquire_multiplex(self) -> None:  # noqa: D401
        pass

    def release_multiplex(self) -> None:
        pass
