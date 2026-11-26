"""Acquire a reviewable CWON 2024 snapshot from World Bank Wealth Accounts.

Run as a module from the repository root. Raw responses are preserved; nothing
is published or promoted to the canonical registry by this command.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from scripts.acquire_wdi_gdp_resilience import (
    BASE, COUNTRIES, parse_page, request, validate_rows,
)

SOURCE_ID = "59"
EXPECTED_SOURCE_DATE = "2024-10-08"
START, END = 1995, 2020
INDICATORS = {
    "NW.TOW.PC": "national comprehensive wealth",
    "NW.PCA.PC": "produced capital",
    "NW.HCA.PC": "human capital",
    "NW.NCA.TOTL.PC": "renewable natural capital",
    "NW.NCA.SSOI.PC": "nonrenewable natural capital",
    "NW.NFA.PC": "foreign assets",
    "NW.NFL.PC": "foreign liabilities",
}


def single_metadata(raw: bytes) -> dict[str, Any]:
    """Require exactly one metadata record, not an API error envelope."""
    header, records = parse_page(raw, 1)
    if int(header["pages"]) != 1 or int(header["total"]) != 1 or len(records) != 1:
        raise ValueError("Expected exactly one metadata record")
    return records[0]


def check_source(raw: bytes) -> dict[str, Any]:
    """Reject source changes; do not silently use another CWON edition."""
    source = single_metadata(raw)
    if (str(source.get("id")) != SOURCE_ID
            or source.get("name") != "Wealth Accounts"
            or source.get("lastupdated") != EXPECTED_SOURCE_DATE):
        raise ValueError("Unexpected Wealth Accounts source identity/vintage")
    return source


def check_indicator(raw: bytes, indicator: str) -> dict[str, Any]:
    """Verify both indicator identity and real per-capita measurement semantics."""
    metadata = single_metadata(raw)
    name = str(metadata.get("name", "")).lower()
    expected = INDICATORS[indicator]
    # Match renewable and nonrenewable distinctly; never accept current USD.
    if (metadata.get("id") != indicator
            or str(metadata.get("source", {}).get("id")) != SOURCE_ID
            or not re.search(r"\b" + re.escape(expected) + r"\b", name)
            or "per capita" not in name or "real chained 2019" not in name):
        raise ValueError(f"Unexpected indicator metadata: {indicator}: {name}")
    return metadata


def acquire(output: Path) -> dict[str, Any]:
    """Retrieve all pages, record checksums, and validate country-year coverage."""
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

    source_url = f"{BASE}/source/{SOURCE_ID}?format=json"
    source = check_source(save(source_url, "source-before.json"))
    for indicator in INDICATORS:
        meta_url = f"{BASE}/indicator/{indicator}?format=json&source={SOURCE_ID}"
        metadata = check_indicator(save(meta_url, f"{indicator}.metadata.json"), indicator)
        rows: list[dict[str, Any]] = []
        page = 1
        expected: tuple[int, int, str] | None = None
        while True:
            query = urlencode({"format": "json", "source": SOURCE_ID,
                               "date": f"{START}:{END}", "per_page": 1000, "page": page})
            url = f"{BASE}/country/{';'.join(COUNTRIES)}/indicator/{indicator}?{query}"
            header, records = parse_page(save(url, f"{indicator}.page-{page}.json"), page)
            identity = (int(header["pages"]), int(header["total"]),
                        str(header.get("lastupdated", "")))
            if str(header.get("sourceid")) != SOURCE_ID:
                raise ValueError("Unexpected observation source ID")
            if identity[2] != EXPECTED_SOURCE_DATE:
                raise ValueError("Observation vintage differs from reviewed source")
            if expected is not None and expected != identity:
                raise ValueError("Pagination identity changed")
            expected = identity
            rows.extend(records)
            if page == identity[0]:
                break
            page += 1
        if len(rows) != identity[1]:
            raise ValueError("Pagination count mismatch")
        result = validate_rows(rows, indicator, COUNTRIES, START, END)
        if not result["observed"]:
            raise ValueError(f"No observations: {indicator}")
        coverage[indicator] = {**result, "indicator_name": metadata["name"],
                               "source_updated": identity[2]}
    check_source(save(source_url, "source-after.json"))
    manifest: dict[str, Any] = {
        "status": "candidate_only",
        "edition": "The Changing Wealth of Nations 2024",
        "source_id": SOURCE_ID,
        "source_name": source["name"],
        "source_updated": source["lastupdated"],
        "redistribution": "pending_indicator_level_review",
        "catalog": "https://datacatalog.worldbank.org/search/dataset/0042066/wealth-accounting",
        "terms": "https://data.worldbank.org/summary-terms-of-use",
        "countries": COUNTRIES, "start": START, "end": END,
        "files": files, "coverage": coverage,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    """Require a new output directory and fixed study window."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    acquire(args.output)


if __name__ == "__main__":
    main()
