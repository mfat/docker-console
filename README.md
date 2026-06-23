# Docker Console

A **local-first** Docker/Podman manager for the GNOME desktop — GTK4 + libadwaita.
Point it at the Docker (or Podman) daemon on your machine and manage containers,
images, volumes, networks, and Compose projects from a clean native UI.

> Extracted from the Docker Console feature originally built inside
> [sshpilot](https://github.com/mfat/sshpilot). Built so **remote (SSH) hosts** can
> be added later without touching the UI — see *Adding remote hosts* below.

## Features

- **Containers** — list (with health), start/stop/restart/pause/kill/remove, search,
  inspect details, **create** (image, ports, volumes, env, network, `-i`/`-t`, user,
  memory/CPU limits), open an interactive **shell**, follow **logs**.
- **Logs** — in-page snapshot with search, errors-only, auto-scroll, copy, save, and
  auto-refresh; or follow live in a terminal tab.
- **Stats** — per-container CPU/memory/IO table, plus streaming **live stats**.
- **Images** — list, pull, history, remove, prune (images / system / volumes).
- **Volumes / Networks** — list, inspect, remove.
- **Compose** — list projects, up/redeploy, start/stop/restart, per-service breakdown,
  view the compose file, tear down.
- Pausable auto-refresh with a configurable interval; optional `sudo`; docker/podman
  runtime override.

Interactive/streamed commands (`exec -it`, `logs -f`, `stats`, `pull`, `compose up`)
open in an embedded **Vte** terminal tab.

## Requirements

System packages (GObject-introspection libraries — not installable via pip):

- GTK 4, libadwaita ≥ 1.4, Vte 3.91, PyGObject (`python3-gi`)
- A working `docker` or `podman` CLI on your machine

Debian/Ubuntu:

```sh
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 gir1.2-vte-3.91
```

## Run

```sh
python3 -m docker_console
# or, after `pip install .`:
docker-console
```

If your user isn't in the `docker` group, toggle **sudo** in the header (requires
passwordless sudo for the captured calls; interactive terminals will prompt).

## Adding remote hosts (planned)

The app talks to docker through a small **transport** seam
(`docker_console/transport/`). `LocalTransport` runs commands on this machine; a
future `SSHTransport` will run the *same* command strings on a remote host
(`ssh -F <config> <host> <cmd>` for captured calls, an `ssh -t` PTY in a Vte tab for
interactive ones, and `-o ControlMaster=…` for connection reuse). The UI and the
docker client are already transport-agnostic, so remote support is additive — see
`docker_console/transport/ssh.py`.

## License

GPL-3.0-or-later.
