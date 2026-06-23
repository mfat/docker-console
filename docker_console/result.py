"""The result of running a captured command via a transport."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CommandResult:
    """Outcome of a captured command. ``exit_code == -1`` means the command
    could not be launched at all (transport error / timeout). Duck-compatible
    with what :class:`docker_console.client.DockerClient` reads
    (``.exit_code`` / ``.stdout`` / ``.stderr``)."""

    exit_code: int
    stdout: str = ""
    stderr: str = ""

    @property
    def ok(self) -> bool:
        return self.exit_code == 0
