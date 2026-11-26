"""Stage only the reviewed November 2026 WDI artifact for canonical registration."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import yaml

SLUG = "world-bank-wdi-gdp-resilience-2026-11-26"
MANIFEST_SHA256 = "45807a39fe812ba771fb88812509cdd55c23b2f0cc020de799bde86cb2e1838f"
INDICATORS = {
    "NY.GDP.MKTP.CD", "NY.GDP.MKTP.PP.CD", "NY.GDP.MKTP.KD",
    "SP.POP.TOTL", "NV.AGR.TOTL.ZS", "NV.IND.TOTL.ZS",
    "NV.IND.MANF.ZS", "NV.SRV.TOTL.ZS",
}


def digest(raw: bytes) -> str:
    """Return the SHA-256 digest of unchanged bytes."""
    return hashlib.sha256(raw).hexdigest()


def stage(candidate: Path, root: Path) -> None:
    """Verify the reviewed artifact and stage canonical files without network I/O."""
    manifest_bytes = (candidate / "manifest.json").read_bytes()
    if digest(manifest_bytes) != MANIFEST_SHA256:
        raise ValueError("Candidate is not the exact reviewed manifest")
    manifest: dict[str, Any] = json.loads(manifest_bytes)
    expected = {f"{indicator}.{suffix}.json" for indicator in INDICATORS
                for suffix in ("metadata", "page-1", "page-2")}
    records = manifest["files"]
    if (len(records) != 24 or {record["path"] for record in records} != expected
            or set(manifest["coverage"]) != INDICATORS
            or len(manifest["countries"]) != 33
            or (manifest["start"], manifest["end"]) != (1995, 2025)):
        raise ValueError("Unexpected manifest scope")
    # Verify all file bytes before creating or modifying any registry path.
    for record in records:
        path = candidate / record["path"]
        raw = path.read_bytes()
        if len(raw) != record["bytes"] or digest(raw) != record["sha256"]:
            raise ValueError(f"Source file failed integrity: {path.name}")
    dataset = root / "datasets" / SLUG
    if dataset.exists():
        raise FileExistsError(dataset)
    policy_path = root / "reports" / "canonical-adoption-policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    if any(item["dataset_id"] == SLUG for item in policy["exemptions"]):
        raise ValueError("Unexpected existing adoption exemption")
    raw_dir = dataset / "raw"
    raw_dir.mkdir(parents=True)
    file_metadata: list[dict[str, Any]] = []
    for record in records:
        filename = record["path"]
        shutil.copyfile(candidate / filename, raw_dir / filename)
        file_metadata.append({
            "path": f"raw/{filename}", "role": "raw", "format": "json",
            "encoding": "utf-8", "compression": None, "sha256": record["sha256"],
            "notes": f"Unmodified WDI response. {record['bytes']} bytes; "
                     f"retrieved {record['retrieved_at']}. URL: {record['url']}",
        })
    # This is acquisition provenance, not an upstream observation response.
    (raw_dir / "acquisition-manifest.json").write_bytes(manifest_bytes)
    file_metadata.append({
        "path": "raw/acquisition-manifest.json", "role": "raw", "format": "json",
        "encoding": "utf-8", "compression": None, "sha256": MANIFEST_SHA256,
        "notes": "Unmodified acquisition workflow manifest: provenance and coverage, not World Bank data.",
    })
    metadata = {
        "schema_version": 1, "id": SLUG,
        "title": "World Bank WDI: GDP, population and sectoral value added, 33 countries, 1995-2025",
        "description": "Eight WDI indicators for the fixed EU-27 and US, UK, Switzerland, Japan, China and India. Includes original indicator metadata and paginated API responses.",
        "domain": ["economics", "national-accounts", "economic-growth", "population"],
        "source": {
            "publisher": "World Bank, World Development Indicators (and named indicator data providers)",
            "url": "https://databank.worldbank.org/source/world-development-indicators",
            "retrieved_at": "2026-11-26",
            "snapshot": "WDI source 2; API lastupdated 2026-11-11; retrieved 2026-11-26T17:58:51Z to 17:58:59Z; manifest SHA-256 " + MANIFEST_SHA256,
        },
        "license": {
            "name": "CC BY 4.0 (World Bank dataset terms, with attribution and third-party exceptions)",
            "url": "https://data.worldbank.org/summary-terms-of-use",
            "redistribution": "allowed",
        },
        "citation": {
            "text": "The World Bank: World Development Indicators: original indicator data providers identified in the accompanying indicator metadata. Retrieved 26 November 2026.",
            "url": "https://datatopics.worldbank.org/world-development-indicators/",
        },
        "files": sorted(file_metadata, key=lambda item: item["path"]),
        "lineage": [],
    }
    (dataset / "metadata.yaml").write_text(yaml.safe_dump(
        metadata, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
    (dataset / "README.md").write_text(
        "# World Bank WDI GDP resilience snapshot\n\n"
        "This is the reviewed November 26, 2026 acquisition, not a live API mirror. "
        "All 24 source responses are retained byte-for-byte along with the acquisition manifest.\n\n"
        "## Coverage\n\n"
        "33 countries, 1995–2025, eight indicators, 8,184 cells, 8,116 non-null observations. "
        "GDP and population are complete. Agriculture, industry and services each have seven nulls; "
        "manufacturing has 47. The last balanced year for the three broad sectors is 2021. "
        "Manufacturing is missing throughout for Bulgaria; never treat null as zero. "
        "Manufacturing is nested within industry, and GDP shares need not sum to 100%.\n\n"
        "## Licensing and citation\n\n"
        "The World Bank: World Development Indicators: providers listed in each indicator metadata file. "
        "Retrieved 26 November 2026. All eight indicator landing pages display CC BY 4.0. "
        "Retain provider attribution and comply with the [World Bank dataset terms]"
        "(https://www.worldbank.org/ext/en/legal/terms-conditions/datasets). "
        "See the [review](../../docs/consumer-source-audits/wdi-gdp-resilience-validation-2026-11-26.md).\n",
        encoding="utf-8")
    # Temporary exemption until the actual downstream implementation pins this commit.
    policy["exemptions"].append({
        "dataset_id": SLUG,
        "rationale": "Reviewed snapshot precedes the Medium-Blog GDP economic resilience implementation (PR #776 research protocol). Remove when the consumer registers its implemented revision and pinned data paths/checksums.",
    })
    policy_path.write_text(json.dumps(policy, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    stage(args.candidate, args.root)


if __name__ == "__main__":
    main()
