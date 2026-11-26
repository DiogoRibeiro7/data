"""Acquire candidate WDI snapshots without promoting them to canonical data."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

BASE = "https://api.worldbank.org/v2"
COUNTRIES = tuple(sorted("""AUT BEL BGR HRV CYP CZE DNK EST FIN FRA DEU GRC HUN
IRL ITA LVA LTU LUX MLT NLD POL PRT ROU SVK SVN ESP SWE USA GBR CHE JPN CHN IND
""".split()))
INDICATORS = (
    "NY.GDP.MKTP.CD", "NY.GDP.MKTP.PP.CD", "NY.GDP.MKTP.KD",
    "SP.POP.TOTL", "NV.AGR.TOTL.ZS", "NV.IND.TOTL.ZS",
    "NV.IND.MANF.ZS", "NV.SRV.TOTL.ZS",
)


def request(url: str) -> bytes:
    """Retry transient failures only; preserve response bytes."""
    for attempt in range(4):
        try:
            with urlopen(url, timeout=60) as response:
                return response.read()
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise
        except (URLError, TimeoutError):
            if attempt == 3:
                raise
        time.sleep(2 ** attempt)
    raise RuntimeError("Unreachable retry state")


def parse_page(raw: bytes, page: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Reject API error envelopes and inconsistent pagination."""
    payload = json.loads(raw)
    if not isinstance(payload, list) or len(payload) != 2:
        raise ValueError("Unexpected WDI response envelope")
    header, rows = payload
    if not isinstance(header, dict) or not isinstance(rows, list):
        raise ValueError("Invalid WDI header or records")
    if int(header["page"]) != page or int(header["pages"]) < page:
        raise ValueError("Invalid page metadata")
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError("Invalid record")
    return header, rows


def validate_rows(
    rows: list[dict[str, Any]], indicator: str, countries: tuple[str, ...],
    start: int, end: int,
) -> dict[str, Any]:
    """Validate observation identity, preserve nulls and report coverage."""
    seen: set[tuple[str, int]] = set()
    observed: set[tuple[str, int]] = set()
    for row in rows:
        code = row["countryiso3code"]
        year = int(row["date"])
        key = (code, year)
        if (code not in countries or not start <= year <= end
                or row["indicator"]["id"] != indicator or key in seen):
            raise ValueError(f"Unexpected or duplicate observation: {key}")
        seen.add(key)
        value = row["value"]
        if value is not None:
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError(f"Invalid numeric value: {key}")
            observed.add(key)
    return {
        "records": len(seen),
        "observed": len(observed),
        "explicit_nulls": len(seen - observed),
        "absent_cells": len(countries) * (end - start + 1) - len(seen),
        "coverage_by_country": {
            code: [year for year in range(start, end + 1)
                   if (code, year) in observed] for code in countries
        },
        "complete_years": [
            year for year in range(start, end + 1)
            if all((code, year) in observed for code in countries)
        ],
    }


def acquire(output: Path, start: int, end: int) -> None:
    """Save paginated raw data and metadata; write manifest only on success."""
    output.mkdir(parents=True, exist_ok=False)
    files: list[dict[str, Any]] = []
    coverage: dict[str, Any] = {}

    def save(url: str, filename: str) -> bytes:
        raw = request(url)
        (output / filename).write_bytes(raw)
        files.append({
            "path": filename, "url": url, "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        })
        return raw

    for indicator in INDICATORS:
        meta_url = f"{BASE}/indicator/{indicator}?format=json&source=2"
        metadata = json.loads(save(meta_url, f"{indicator}.metadata.json"))
        if (not isinstance(metadata, list) or len(metadata) != 2
                or not isinstance(metadata[1], list)
                or len(metadata[1]) != 1
                or metadata[1][0]["id"] != indicator
                or str(metadata[1][0]["source"]["id"]) != "2"):
            raise ValueError(f"Unexpected indicator metadata: {indicator}")
        rows: list[dict[str, Any]] = []
        page = 1
        expected: tuple[int, int, str] | None = None
        while True:
            query = urlencode({"format": "json", "source": 2,
                               "date": f"{start}:{end}", "per_page": 1000,
                               "page": page})
            url = f"{BASE}/country/{';'.join(COUNTRIES)}/indicator/{indicator}?{query}"
            header, records = parse_page(save(url, f"{indicator}.page-{page}.json"), page)
            identity = (int(header["pages"]), int(header["total"]),
                        str(header.get("lastupdated", "")))
            if str(header.get("sourceid")) != "2":
                raise ValueError("Unexpected source ID")
            if expected is not None and expected != identity:
                raise ValueError("Pagination vintage or count changed")
            expected = identity
            rows.extend(records)
            if page == identity[0]:
                break
            page += 1
        if len(rows) != identity[1]:
            raise ValueError("Pagination count mismatch")
        coverage[indicator] = validate_rows(rows, indicator, COUNTRIES, start, end)
        if not coverage[indicator]["observed"]:
            raise ValueError(f"No observations: {indicator}")

    manifest = {
        "status": "candidate_only", "source_id": 2,
        "source": "World Development Indicators",
        "redistribution": "pending_indicator_level_review",
        "terms": "https://data.worldbank.org/summary-terms-of-use",
        "countries": COUNTRIES, "start": start, "end": end,
        "files": files, "coverage": coverage,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--start", type=int, default=1995)
    parser.add_argument("--end", type=int, default=2025)
    args = parser.parse_args()
    if not 1960 <= args.start <= args.end <= datetime.now(timezone.utc).year:
        parser.error("Invalid year range")
    acquire(args.output, args.start, args.end)


if __name__ == "__main__":
    main()
