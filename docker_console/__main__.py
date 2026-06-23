"""``python -m docker_console`` / ``docker-console`` entry point."""

from __future__ import annotations

import sys

from .app import main

if __name__ == "__main__":
    sys.exit(main())
