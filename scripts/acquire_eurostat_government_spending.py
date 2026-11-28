"""Download an auditable Eurostat candidate; never promote it automatically."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
COUNTRIES = "AT BE BG HR CY CZ DK EE FI FR DE EL HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE".split()
FISCAL_ITEMS = "TE B1G P3 D62PAY D632PAY D1PAY P2 P51G D41PAY TR B9".split()
LICENSE_URL = "https://ec.europa.eu/eurostat/help/copyright-notice"
QUERIES: dict[str, tuple[str, dict[str, str | list[str]]]] = {
    "fiscal.json": ("gov_10a_main", {"freq": "A", "sector": "S13", "unit": "PC_GDP", "na_item": FISCAL_ITEMS}),
    "growth.json": ("nama_10_gdp", {"freq": "A", "unit": "CLV_PCH_PRE", "na_item": "B1GQ"}),
    "nominal_gdp.json": ("nama_10_gdp", {"freq": "A", "unit": "CP_MEUR", "na_item": "B1GQ"}),
}


def request_url(dataset: str, filters: dict[str, str | list[str]]) -> str:
    """Return a reproducible URL restricted to the EU27 and 1995–2025."""
    params = {"lang": "EN", "geo": COUNTRIES, "sinceTimePeriod": "1995",
              "untilTimePeriod": "2025", **filters}
    return BASE + dataset + "?" + urlencode(params, doseq=True)


def validate_payload(payload: dict[str, Any], filters: dict[str, str | list[str]]) -> None:
    """Reject missing requested categories, error messages and empty responses."""
    if payload.get("class") != "dataset" or not payload.get("value"):
        raise ValueError("Eurostat returned an empty or non-dataset response")
    dimensions = payload["dimension"]
    for key, wanted in {**filters, "geo": COUNTRIES}.items():
        index = dimensions[key]["category"]["index"]
        expected = {wanted} if isinstance(wanted, str) else set(wanted)
        if set(index) != expected:
            raise ValueError(f"{key}: expected {expected}, received {set(index)}")
    years = set(dimensions["time"]["category"]["index"])
    if not years or not years <= {str(y) for y in range(1995, 2026)}:
        raise ValueError(f"Unexpected time dimension: {years}")


def acquire(output: Path) -> None:
    """Preserve exact response bytes and source metadata with SHA-256 digests."""
    output.mkdir(parents=True, exist_ok=False)
    files: list[dict[str, Any]] = []
    for filename, (dataset, filters) in QUERIES.items():
        url = request_url(dataset, filters)
        request = Request(url, headers={"User-Agent": "research-data-registry/1.0"})
        with urlopen(request, timeout=180) as response:
            raw = response.read()
        payload = json.loads(raw)
        validate_payload(payload, filters)
        (output / filename).write_bytes(raw)
        files.append({"path": filename, "dataset": dataset, "doi": f"10.2908/{dataset}",
                      "url": url, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                      "source_updated": payload.get("updated"), "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                      "non_null_observations": sum(v is not None for v in (payload["value"].values()
                          if isinstance(payload["value"], dict) else payload["value"]))})
    manifest = {"status": "candidate-not-canonical", "source": "Eurostat",
                "reuse_policy": LICENSE_URL, "files": files}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    """Parse the output directory and acquire a fresh candidate."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    acquire(parser.parse_args().output)


if __name__ == "__main__":
    main()
