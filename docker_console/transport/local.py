"""Local transport — runs docker/podman on this machine.

Captured commands go through ``/bin/sh -lc`` (a login shell so the user's PATH
applies, matching how the CLI behaves in a terminal). Interactive commands open a
Vte terminal tab. Vte is imported lazily inside :meth:`spawn_terminal` so the
captured path (and the unit tests) don't need a GTK/Vte runtime.
"""

from __future__ import annotations

import subprocess
from typing import Any, Optional

from ..result import CommandResult
from .base import Transport

_SHELL = "/bin/sh"


class LocalTransport(Transport):
    location = "Local machine"

    def run(self, command: str, *, timeout: float = 30) -> CommandResult:
        try:
            proc = subprocess.run(
                [_SHELL, "-lc", command],
                capture_output=True, text=True, timeout=timeout, check=False,
            )
            return CommandResult(proc.returncode, proc.stdout, proc.stderr)
        except subprocess.TimeoutExpired:
            return CommandResult(-1, "", "Command timed out")
        except OSError as exc:
            return CommandResult(-1, "", str(exc))

    def spawn_terminal(self, window: Any, command: str,
                       title: Optional[str] = None) -> bool:
        from ..terminal import open_local_terminal  # lazy: pulls in Vte
        return open_local_terminal(window, [_SHELL, "-lc", command], title=title)
