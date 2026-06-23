"""Connection registry — the docker targets the app can manage.

Local-first: the registry holds a single ``local`` connection backed by
:class:`~docker_console.transport.local.LocalTransport`. The model already carries
everything a remote host needs (``kind``, a per-connection transport), so adding
SSH hosts later is just registering more :class:`Connection`s with an
``SSHTransport`` — the UI and client are unchanged.

The UI reads ``.nickname`` (identifier) and ``.protocol``/``.kind`` (for the
host-bar label); it never assumes SSH.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .transport.base import Transport
from .transport.local import LocalTransport

LOCAL_NICKNAME = "local"


@dataclass
class Connection:
    nickname: str
    transport: Transport
    kind: str = "local"          # "local" | "ssh"
    protocol: str = "local"      # mirrors sshpilot's connection attr the UI reads
    label: str = ""

    def __post_init__(self) -> None:
        if not self.label:
            self.label = "Local Docker" if self.kind == "local" else self.nickname


class ConnectionRegistry:
    """Ordered set of connections keyed by nickname; seeded with local."""

    def __init__(self) -> None:
        self._by_nick: Dict[str, Connection] = {}
        self.add(Connection(LOCAL_NICKNAME, LocalTransport(), kind="local"))

    def add(self, conn: Connection) -> None:
        self._by_nick[conn.nickname] = conn

    def get(self, nickname: str) -> Optional[Connection]:
        return self._by_nick.get(nickname)

    def transport_for(self, nickname: str) -> Optional[Transport]:
        conn = self._by_nick.get(nickname)
        return conn.transport if conn else None

    def all(self) -> List[Connection]:
        return list(self._by_nick.values())
