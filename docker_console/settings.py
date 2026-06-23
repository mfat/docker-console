"""Tiny JSON-backed settings store.

The UI reads/writes a handful of flat keys (``controlmaster``,
``refresh_interval``, ``last_host``, and per-connection ``sudo:<nick>`` /
``runtime:<nick>`` / ``runtime_mode:<nick>``). We persist them to a single JSON
file under ``$XDG_CONFIG_HOME/docker-console/settings.json`` and write on every
change — small data, no need for GSettings/dconf.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict

logger = logging.getLogger(__name__)


def _config_path() -> str:
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, "docker-console", "settings.json")


class Settings:
    """Flat key/value store persisted as JSON. Keys are arbitrary strings
    (including ``sudo:local`` style)."""

    def __init__(self, path: str | None = None) -> None:
        self._path = path or _config_path()
        self._data: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        try:
            with open(self._path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                self._data = data
        except FileNotFoundError:
            pass
        except (OSError, json.JSONDecodeError):
            logger.warning("could not read settings %s; starting fresh", self._path,
                           exc_info=True)

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
            tmp = f"{self._path}.tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh, indent=2, sort_keys=True)
            os.replace(tmp, self._path)
        except OSError:
            logger.warning("could not write settings %s", self._path, exc_info=True)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        if self._data.get(key) == value:
            return
        self._data[key] = value
        self._save()
