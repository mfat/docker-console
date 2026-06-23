"""Connection registry is seeded with a local connection."""

from docker_console.connections import ConnectionRegistry, LOCAL_NICKNAME
from docker_console.transport.local import LocalTransport


def test_registry_seeded_with_local():
    reg = ConnectionRegistry()
    local = reg.get(LOCAL_NICKNAME)
    assert local is not None
    assert local.kind == "local"
    assert local.label == "Local Docker"
    assert isinstance(local.transport, LocalTransport)
    assert isinstance(reg.transport_for(LOCAL_NICKNAME), LocalTransport)
    assert LOCAL_NICKNAME in {c.nickname for c in reg.all()}


def test_unknown_connection_is_none():
    reg = ConnectionRegistry()
    assert reg.get("ghost") is None
    assert reg.transport_for("ghost") is None
