#!/usr/bin/env python3
"""Compatibility wrapper for the packaged repository validator."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from data_registry.validator import *  # noqa: F403,E402
from data_registry.validator import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
