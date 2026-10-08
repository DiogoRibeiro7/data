#!/usr/bin/env python3
"""Fetch one canonical dataset file from a pinned data-repository commit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data_registry.fetch import (  # noqa: E402
    COMMIT_RE,
    DEFAULT_RAW_BASE_URL,
    DEFAULT_REPOSITORY,
    REPOSITORY_RE,
    SHA256_RE,
    DatasetReference,
    fetch_dataset_file,
    sha256_file,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--timeout", type=float, default=60.0)
    return parser.parse_args()


def main() -> int:
    """Run the command-line fetch operation."""

    args = parse_args()
    try:
        reference = DatasetReference(
            repository=args.repository,
            commit=args.commit,
            path=args.path,
            sha256=args.sha256,
        )
        output = fetch_dataset_file(
            reference,
            args.output,
            timeout_seconds=args.timeout,
            force=args.force,
        )
    except (ValueError, TypeError, FileExistsError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Verified dataset file: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
