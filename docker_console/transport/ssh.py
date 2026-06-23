"""SSH transport — placeholder for remote-host support (not implemented in v1).

The app is built local-first, but the transport seam is designed so remote hosts
drop in here without touching the UI or :class:`docker_console.client.DockerClient`.
A real implementation would:

* ``run(command)``  → ``subprocess.run(["ssh", "-F", <config>, <host>, command])``
  (capture stdout/stderr/exit code into a ``CommandResult``), reusing the user's
  ``~/.ssh/config`` for auth/ProxyJump.
* ``spawn_terminal(window, command)`` → open a Vte tab running
  ``ssh -t -F <config> <host> command`` (a PTY for ``docker exec -it`` etc.).
* ``acquire_multiplex`` / ``release_multiplex`` → add
  ``-o ControlMaster=auto -o ControlPath=… -o ControlPersist=…`` so the chatty
  polling reuses one connection.

Until then, constructing one raises so the gap is obvious.
"""

from __future__ import annotations

from typing import Any, Optional

from ..result import CommandResult
from .base import Transport


class SSHTransport(Transport):
    location = "Remote host (SSH)"

    def __init__(self, host: str, *, ssh_config: Optional[str] = None) -> None:
        raise NotImplementedError(
            "Remote (SSH) hosts are not implemented yet — docker-console is "
            "local-first. See docker_console/transport/ssh.py for the plan."
        )

    def run(self, command: str, *, timeout: float = 30) -> CommandResult:  # pragma: no cover
        raise NotImplementedError

    def spawn_terminal(self, window: Any, command: str,
                       title: Optional[str] = None) -> bool:  # pragma: no cover
        raise NotImplementedError
