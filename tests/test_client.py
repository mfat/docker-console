"""Offline tests for the transport-agnostic DockerClient (no docker, no GTK)."""

import logging

import pytest

from docker_console.client import DockerClient, DockerError


class FakeResult:
    def __init__(self, exit_code=0, stdout="", stderr=""):
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


def _recording_client(responder, *, runtime="docker"):
    calls = []

    def run_command(nickname, command, *, timeout=None):
        calls.append(command)
        result = responder(command) if responder else None
        return result if result is not None else FakeResult()

    return DockerClient(run_command, "local", runtime), calls


def test_ps_builds_command_and_parses_ndjson():
    line = '{"ID":"abc","Names":"web","State":"running"}'
    client, calls = _recording_client(lambda c: FakeResult(stdout=line + "\n"))
    rows = client.ps()
    assert calls[-1] == "docker ps -a --format '{{json .}}'"
    assert rows == [{"ID": "abc", "Names": "web", "State": "running"}]


def test_nonzero_exit_raises():
    client, _ = _recording_client(
        lambda c: FakeResult(exit_code=1, stderr="Cannot connect to the Docker daemon"))
    with pytest.raises(DockerError, match="Cannot connect"):
        client.ps()


@pytest.mark.parametrize("action", ["start", "stop", "restart", "kill", "pause", "unpause"])
def test_lifecycle(action):
    client, calls = _recording_client(None)
    client.lifecycle(action, "c1")
    assert calls[-1] == f"docker {action} c1"


def test_command_is_not_shell_injectable():
    client, _ = _recording_client(None)
    assert client.create_run_args("alpine", command="; rm -rf /") == \
        "run -d alpine ';' rm -rf /"
    assert client.create_run_args("alpine", command=["sh", "-c", "echo hi; rm x"]) == \
        "run -d alpine sh -c 'echo hi; rm x'"


def test_create_run_args_unbalanced_quotes_raises():
    client, _ = _recording_client(None)
    with pytest.raises(ValueError):
        client.create_run_args("alpine", command="sh -c 'oops")


def test_sudo_prefix():
    client, calls = _recording_client(None)
    client.use_sudo = True
    client.ping()
    assert calls[-1] == "sudo -n docker ps -q"
    assert client.stats_stream_command() == "sudo docker stats"


def test_volumes_networks_compose_ps_commands():
    client, calls = _recording_client(lambda c: FakeResult(stdout='{"Name":"v1"}'))
    client.remove_volume("v1", force=True)
    assert calls[-1] == "docker volume rm -f v1"
    client.volume_inspect("v1")
    assert calls[-1] == "docker volume inspect v1 --format '{{json .}}'"
    client.remove_network("n1")
    assert calls[-1] == "docker network rm n1"
    rows = '[{"Service":"web","State":"running"}]'
    client2, calls2 = _recording_client(lambda c: FakeResult(stdout=rows))
    assert client2.compose_ps("proj")[0]["Service"] == "web"
    assert calls2[-1] == "docker compose -p proj ps --format json"


def test_compose_ls_degrades_to_table():
    table = "NAME      STATUS\nweb       running\n"

    def responder(cmd):
        if "--format" in cmd or "--all" in cmd:
            return FakeResult(exit_code=1, stderr="unknown flag")
        return FakeResult(stdout=table)

    client, calls = _recording_client(responder)
    out = client.compose_ls()
    assert calls[-1] == "docker compose ls"
    assert out and out[0]["Name"] == "web"


def test_parse_ndjson_logs_bad_lines(caplog):
    client, _ = _recording_client(lambda c: FakeResult(stdout='{"ID":"1"}\nbroken\n'))
    with caplog.at_level(logging.DEBUG, logger="docker_console.client"):
        assert client.ps() == [{"ID": "1"}]
    assert any("parse" in r.message or "unparseable" in r.message for r in caplog.records)
